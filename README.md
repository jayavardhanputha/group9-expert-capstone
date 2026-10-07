# Azure DevSecOps Capstone: Inventory Management API

A small, end-to-end sample demonstrating how a team can build, test, scan, package, and deploy an API using GitHub Actions and Terraform for Azure. The repository is deliberately useful **without an Azure subscription**: local development, API tests, container builds, security checks, and Terraform validation do not log into Azure or create cloud resources.

> The supplied specification files contained titles only and no additional acceptance criteria. This implementation is an explicit, self-contained sample interpretation of an Azure DevSecOps platform: a containerized Flask inventory API, infrastructure as code, CI/security/documentation checks, and an opt-in cloud deployment workflow.

## Project structure

- `app/inventory-api/` — Flask REST API, SQLite persistence, Dockerfile, tests.
- `infrastructure/terraform/` — Azure Container Apps, Log Analytics, and Azure Files persistence.
- `.github/workflows/` — test/build, Terraform, security, Markdown validation, and optional Azure deployment.
- `ai-specifications/`, `architecture/`, `docs/`, `engineering-decisions/` — project architecture, governance, security, and delivery guidance.

## Run locally (no Azure required)

Requirements: Python 3.12+ and optionally Docker.

From `app/inventory-api`:

1. Install `requirements.txt` into a virtual environment.
2. Set `DATABASE_PATH` to a writable local path if you do not want the default `instance/inventory.db`.
3. Start the API with `flask --app app run --host 127.0.0.1 --port 8000`.
4. Open `http://127.0.0.1:8000/` or `http://127.0.0.1:8000/health/ready`.

Create an item with a JSON POST to `/api/v1/items` containing `name` and non-negative integer `quantity`; `location` is optional. List items at `/api/v1/items`. The API also supports GET, PUT, and DELETE for `/api/v1/items/<id>`. The API is demo-grade: SQLite is appropriate for a single local instance, not concurrent production workloads.

To run tests, install pytest and execute `python -m pytest -q` from `app/inventory-api`. To build and run the container, use `docker build -t inventory-api:local app/inventory-api` and `docker run --rm -p 8000:8000 -v inventory-data:/data inventory-api:local` from the repository root.

## GitHub Actions

Push the repository to GitHub. Workflows run on pushes/pull requests without Azure credentials:

- API tests and Docker image build.
- Terraform format, initialize (backend disabled), and validate.
- Bandit, dependency audit, and Gitleaks secret scanning.
- Markdown link validation.

The workflow builds the image but does not publish or deploy it by default. A registry/image and Azure subscription are needed only for the optional deployment workflow.

## Optional Azure deployment

1. Create an Azure subscription and a GitHub Container Registry package (or another registry accessible to Azure Container Apps). Publish the API image, preferably tagged with the immutable commit SHA.
2. Add GitHub repository variables `AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, and `AZURE_SUBSCRIPTION_ID`; configure an Azure federated identity credential for this GitHub repository and branch/environment. Grant the identity least-privilege permissions for the target subscription/resource group. No client secret is required.
3. Add repository variable `API_IMAGE` with the full immutable container image URI.
4. Review and run **Deploy to Azure (manual)** from the Actions tab. The workflow uses OIDC login, runs Terraform plan, requires GitHub environment approval before apply, and applies only after approval. Configure the `production` environment and protect it with required reviewers.

The Terraform deployment creates billable Azure resources (Container Apps, Log Analytics, Storage Account/Azure Files). Review the plan, region availability, pricing, and organization policies first. Destroy the demo stack when finished with the destroy workflow after review. These steps cannot run without an Azure subscription and appropriate permissions; the local/CI parts still work.

## Security and production limitations

- CI workflows use read-only repository permissions unless publishing/deployment explicitly requires more.
- Azure authentication uses GitHub OIDC rather than long-lived credentials.
- Terraform marks the demo API public; production deployments should add authentication/authorization, private networking or an API gateway, TLS policy, rate limiting, and security monitoring.
- SQLite/Azure Files is a simple stateful demo, not a high availability relational database. Use Azure Database for PostgreSQL or another managed database for production and move secrets to Key Vault.
- Pin third-party GitHub Actions to reviewed commit SHAs for regulated/production use; the examples use major-version tags for readability.

See [Reference Architecture](ai-specifications/reference-architecture.md), [Platform Specification](ai-specifications/enterprise-platform-spec.md), [Security Strategy](ai-specifications/security-strategy.md), [Governance](docs/governance.md), [Operating Model](ai-specifications/operating-model.md), [Migration Roadmap](ai-specifications/migration-roadmap.md), and [ADR-001](engineering-decisions/ADR-001-platform-standard.md).
