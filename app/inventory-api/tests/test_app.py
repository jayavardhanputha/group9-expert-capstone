import json

import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db")})
    with app.test_client() as test_client:
        yield test_client


def test_health_endpoints(client):
    assert client.get("/health/live").json == {"status": "ok"}
    assert client.get("/health/ready").json == {"status": "ready"}


def test_inventory_crud(client):
    created_response = client.post(
        "/api/v1/items",
        data=json.dumps({"name": "Laptop", "quantity": 4, "location": "Lab 1"}),
        content_type="application/json",
    )
    assert created_response.status_code == 201
    created = created_response.json
    assert created["name"] == "Laptop"
    assert created["quantity"] == 4

    item_id = created["id"]
    assert client.get(f"/api/v1/items/{item_id}").json["location"] == "Lab 1"
    assert client.get("/api/v1/items").json["items"][0]["id"] == item_id

    updated_response = client.put(
        f"/api/v1/items/{item_id}",
        data=json.dumps({"quantity": 2}),
        content_type="application/json",
    )
    assert updated_response.status_code == 200
    assert updated_response.json["quantity"] == 2
    assert client.delete(f"/api/v1/items/{item_id}").status_code == 204
    assert client.get(f"/api/v1/items/{item_id}").status_code == 404


def test_invalid_payload_and_missing_item(client):
    invalid = client.post(
        "/api/v1/items",
        data=json.dumps({"name": "", "quantity": -1}),
        content_type="application/json",
    )
    assert invalid.status_code == 400
    assert client.get("/api/v1/items/999").status_code == 404
    assert client.delete("/api/v1/items/999").status_code == 404
