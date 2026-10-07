# Enterprise Platform Specification

## Purpose

Demonstrate a small, auditable Azure DevSecOps delivery path using a sample Inventory Management API. The platform supports local development and GitHub-hosted validation without an Azure subscription. Cloud provisioning is an explicit, manually triggered, approval-gated optional path.

## Scope and acceptance criteria

- Versioned Flask REST API supports inventory item create, read, update, and delete, with input validation and JSON errors.
- SQLite persists data for local demo use; a mounted Azure Files share keeps the single-replica Azure demo's data between container restarts.
- Container runs as a non-root user, exposes liveness/readiness endpoints, and has a health check.
- Pull requests and pushes run API tests, build the image, validate Terraform formatting/configuration, scan Python/dependencies/secrets, and validate Markdown.
- Azure resources are described as Terraform; Azure is not contacted by pull-request workflows.
- Cloud plan/apply and destroy are manual, use OIDC federation, and are gated by protected GitHub environments.
- Local demo, tests, Docker build, and Terraform validation are possible without Azure credentials or a subscription.

## Out of scope

Production authentication, authorization, multi-tenant access, database migrations, high availability, multi-region DR, autoscaling, private ingress, and a managed relational database. These are recommended extensions, not implemented claims.

## Interfaces

`GET /` reports service metadata; `GET /health/live` and `/health/ready` provide probes. `/api/v1/items` supports GET (list) and POST (create); `/api/v1/items/{id}` supports GET, PUT (partial update), and DELETE. Create requires a non-empty name and non-negative integer quantity; location defaults to the empty string.

## Nonfunctional demonstration targets

- Reproducible CI and immutable image references supplied by the operator.
- No secrets committed; no Azure credentials required during normal CI.
- Terraform state is remote and locked in Azure Blob Storage for cloud deployment.
- Single replica and 30-day Log Analytics retention keep the demo understandable; cost and regional availability must be checked before provisioning.
