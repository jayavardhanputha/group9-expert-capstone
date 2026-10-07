# Migration Roadmap

## Demo adoption sequence

1. **Local:** run API and tests without Azure; review API contract and limitations.
2. **CI:** push to GitHub, protect the default branch, require test/build/security/Terraform checks, and remediate findings.
3. **Azure foundation:** after a subscription is approved, create a dedicated state resource group, storage account, and private Blob container; enable versioning/soft delete and grant narrowly scoped Blob data access to the deployment identity.
4. **Federation:** create an Entra application/service principal and GitHub federated identity credential constrained to the repository and protected deployment environment; assign least-privilege Azure roles. Add repository variables for IDs, backend coordinates, and a public immutable API image URI.
5. **First deploy:** inspect the plan and costs, obtain protected environment approval, deploy the demo, verify probes and logs, and record outputs.
6. **Retire:** dispatch destroy after approval, verify resource removal, retain or securely remove the state backend according to policy.

## Production evolution gates

Before production: replace SQLite/Azure Files with a managed database and migrations; add identity, authorization, private ingress/networking, managed secrets, image provenance/signing/SBOM, policy-as-code, backup/restore/DR, monitoring and alerting, load/security testing, cost budgets, and documented SLOs. Security/privacy/governance owners approve the control evidence before data migration.

## No-subscription path

Steps 1-2 and Terraform static validation are useful independently. Do not supply fabricated Azure IDs or run apply/destroy without a real subscription, provisioned backend, approved identity, and reviewed plan.
