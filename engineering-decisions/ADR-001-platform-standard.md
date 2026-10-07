# ADR-001: Azure DevSecOps sample platform

- **Status:** Accepted for capstone demonstration
- **Date:** 2026-10-06

## Context

The project needs a complete, runnable sample that demonstrates application delivery on Azure through GitHub Actions, while contributors currently have no Azure subscription. The initial repository contained a placeholder Flask health endpoint, a resource-group-only Terraform file, and name-only workflows. Supplied specification files were headings without detailed requirements.

## Decision

- Use Flask with a small SQLite-backed inventory CRUD API, pytest tests, and a non-root Gunicorn container.
- Use GitHub Actions for local-independent tests, container build, code/dependency/secret scanning, Markdown checks, and Azure-free Terraform validation.
- Use Terraform for an Azure Container Apps demo with Log Analytics and Azure Files mounted for the SQLite file.
- Keep Azure deployment manual, use GitHub OIDC, remote Azure Blob state, a reviewed plan artifact, and protected environment approvals.
- Keep local API execution, tests, container build, and static infrastructure checks available without an Azure subscription.

## Consequences

The project is inexpensive to understand and portable for a demo, but not production-ready: no API identity controls, single replica, SQLite/Azure Files rather than managed DB, publicly accessible ingress, and no private networking or recovery architecture. The remote state backend must be bootstrapped separately after Azure access exists. Operators must verify provider/service availability, costs, and organization policies before deploying.

## Alternatives considered

- **Azure Functions:** smaller operational footprint, but less direct container/Container Apps deployment learning.
- **Managed relational database:** a better production choice, but introduces provisioned services, credentials/identity, and migrations beyond a subscription-free starter sample.
- **Automatic Azure deploy from every push:** rejected because it creates costs and requires credentials/subscription; deployment is opt-in and approval-gated.
