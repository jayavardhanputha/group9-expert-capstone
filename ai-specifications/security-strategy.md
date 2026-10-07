# Security Strategy

## Implemented in this sample

- Parameterized SQL for values, strict request validation, and no user-supplied SQL.
- Container process runs as non-root; only required API port is exposed.
- GitHub Actions use `contents: read` by default; Azure login uses OIDC rather than a client secret.
- Security workflow runs Bandit, pip-audit, and Gitleaks; Terraform is validated in CI without Azure access.
- Terraform protects storage from anonymous blob access, enforces TLS 1.2, and tags demo resources.
- Deployment and destroy are manual; production environment approval is required before resource-changing jobs.

## Known risks and gaps

The API has no authentication or authorization and public ingress is enabled. The demo data is not sensitive. SQLite on Azure Files is not a production persistence design. The sample does not configure a WAF, private endpoints, network restrictions, Key Vault, managed database, image signing, SBOM attestation, runtime threat detection, or production alerting. These limitations must be resolved before handling real data.

## Operational controls

Protect the default branch, require review and successful checks, protect production GitHub environments with designated reviewers, limit Azure role scope, and review OIDC subject conditions. Keep Terraform state in a dedicated private Blob container with data-plane RBAC, versioning/soft delete, restricted access, and recovery testing. Review scanner alerts, dependency updates, Azure Activity Log, and Container Apps/Log Analytics health. Revoke federation and rotate access promptly during incidents.
