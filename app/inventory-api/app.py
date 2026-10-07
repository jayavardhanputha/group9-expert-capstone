"""A small inventory API suitable for local demos and Azure Container Apps."""

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, g, jsonify, request


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
	app = Flask(__name__)
	app.config.from_mapping(
		DATABASE=os.environ.get("DATABASE_PATH", str(Path(app.instance_path) / "inventory.db")),
	)
	if test_config:
		app.config.update(test_config)

	Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)

	def get_db() -> sqlite3.Connection:
		if "db" not in g:
			g.db = sqlite3.connect(app.config["DATABASE"])
			g.db.row_factory = sqlite3.Row
		return g.db

	@app.teardown_appcontext
	def close_db(_error: BaseException | None = None) -> None:
		database = g.pop("db", None)
		if database is not None:
			database.close()

	with app.app_context():
		get_db().execute(
			"""CREATE TABLE IF NOT EXISTS items (
				   id INTEGER PRIMARY KEY AUTOINCREMENT,
				   name TEXT NOT NULL,
				   quantity INTEGER NOT NULL CHECK (quantity >= 0),
				   location TEXT NOT NULL DEFAULT '',
				   updated_at TEXT NOT NULL
			   )"""
		)
		get_db().commit()

	def serialize_item(row: sqlite3.Row) -> dict[str, Any]:
		return {key: row[key] for key in ("id", "name", "quantity", "location", "updated_at")}

	def validate_payload(payload: Any, *, creating: bool) -> tuple[dict[str, Any] | None, str | None]:
		if not isinstance(payload, dict):
			return None, "Request body must be a JSON object."
		allowed = {"name", "quantity", "location"}
		if set(payload) - allowed:
			return None, "Only name, quantity, and location fields are allowed."
		if creating and ("name" not in payload or "quantity" not in payload):
			return None, "name and quantity are required."
		values: dict[str, Any] = {}
		if "name" in payload:
			if not isinstance(payload["name"], str) or not payload["name"].strip():
				return None, "name must be a non-empty string."
			values["name"] = payload["name"].strip()
		if "quantity" in payload:
			quantity = payload["quantity"]
			if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 0:
				return None, "quantity must be a non-negative integer."
			values["quantity"] = quantity
		if "location" in payload:
			if not isinstance(payload["location"], str):
				return None, "location must be a string."
			values["location"] = payload["location"].strip()
		return values, None

	@app.get("/")
	def home():
		return jsonify({"service": "inventory-api", "api": "/api/v1/items", "status": "ok"})

	@app.get("/health/live")
	def liveness():
		return jsonify({"status": "ok"})

	@app.get("/health/ready")
	def readiness():
		get_db().execute("SELECT 1").fetchone()
		return jsonify({"status": "ready"})

	@app.get("/api/v1/items")
	def list_items():
		rows = get_db().execute("SELECT * FROM items ORDER BY id").fetchall()
		return jsonify({"items": [serialize_item(row) for row in rows]})

	@app.post("/api/v1/items")
	def create_item():
		values, error = validate_payload(request.get_json(silent=True), creating=True)
		if error:
			return jsonify({"error": error}), 400
		assert values is not None
		now = datetime.now(timezone.utc).isoformat()
		cursor = get_db().execute(
			"INSERT INTO items (name, quantity, location, updated_at) VALUES (?, ?, ?, ?)",
			(values["name"], values["quantity"], values.get("location", ""), now),
		)
		get_db().commit()
		row = get_db().execute("SELECT * FROM items WHERE id = ?", (cursor.lastrowid,)).fetchone()
		return jsonify(serialize_item(row)), 201

	@app.get("/api/v1/items/<int:item_id>")
	def get_item(item_id: int):
		row = get_db().execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
		if row is None:
			return jsonify({"error": "Item not found."}), 404
		return jsonify(serialize_item(row))

	@app.put("/api/v1/items/<int:item_id>")
	def update_item(item_id: int):
		values, error = validate_payload(request.get_json(silent=True), creating=False)
		if error:
			return jsonify({"error": error}), 400
		assert values is not None
		if not values:
			return jsonify({"error": "Provide at least one field to update."}), 400
		db = get_db()
		existing = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
		if existing is None:
			return jsonify({"error": "Item not found."}), 404
		values["updated_at"] = datetime.now(timezone.utc).isoformat()
		assignments = ", ".join(f"{field} = ?" for field in values)
		db.execute(
			f"UPDATE items SET {assignments} WHERE id = ?",
			(*values.values(), item_id),
		)
		db.commit()
		row = db.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
		return jsonify(serialize_item(row))

	@app.delete("/api/v1/items/<int:item_id>")
	def delete_item(item_id: int):
		cursor = get_db().execute("DELETE FROM items WHERE id = ?", (item_id,))
		get_db().commit()
		if cursor.rowcount == 0:
			return jsonify({"error": "Item not found."}), 404
		return "", 204

	return app


app = create_app()