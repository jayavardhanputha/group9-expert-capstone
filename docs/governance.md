# Governance

## Repository governance

- Use pull requests, named code owners/reviewers, and required status checks on the default branch.
- Keep application, infrastructure, and deployment changes versioned together; record material architectural changes as ADRs.
- Grant workflows minimum permissions; do not commit credentials, Terraform state, plan files, or production data.
- Protect GitHub deployment environments and use OIDC federated identity constrained to the intended repository/environment.
- Review image provenance, scanner results, Terraform plan, regional policy, and cost before any apply.

## Resource and data governance

The deployed resources are tagged as a demo and use a dedicated resource group. Treat sample inventory records as non-sensitive. Set organizational resource locks/policies, cost alerts/budgets, retention, and deletion rules before wider use. Terraform remote state can contain sensitive values: keep its Blob container private, restrict data-plane access, enable recovery controls, and never publish state artifacts.

## Change and exception management

Document deviations from baseline, owner, rationale, compensating control, approval, and expiry. Reassess exceptions at release and remove them when no longer required. The public unauthenticated endpoint and file-based data store are accepted only for this isolated demonstration, not approved production exceptions.
