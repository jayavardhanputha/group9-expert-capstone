# Operating Model

## Roles

- **Application developer:** changes API and tests; owns validation and API compatibility.
- **Platform engineer:** maintains reusable Terraform, GitHub workflows, identity federation, and platform guardrails.
- **Security reviewer:** reviews dependency/secret scan results, threat model, and production exceptions.
- **Release approver:** reviews the plan and approves the protected environment apply/destroy.
- **Service owner:** owns availability, data classification, support, and incident decisions.

## Delivery and support

Changes enter through pull requests. Require a review and green CI before merge. An authorized operator dispatches a deployment from a reviewed commit with a pinned image digest/tag; review the plan artifact and authorize apply. Verify `/health/ready`, inspect logs, and record release/version. For rollback, deploy the previously approved image through a new plan/apply. Do not directly edit cloud resources: reconcile changes through Terraform.

For this demo, check GitHub workflow status, Container Apps revision/provisioning, `/health/ready`, and Log Analytics logs. Preserve the Terraform state and storage share. Escalate security incidents to the organization's incident response process; disable the GitHub federated identity or revoke Azure role assignment if needed.

## Service-level note

This sample defines no production SLO or on-call commitment. Its single replica, public unauthenticated API, and SQLite persistence are for demonstrations only. Establish availability, recovery-point/time, retention, and support objectives before production use.
