# Sentinels Multi-Tenant Isolation Guarantees

In a multi-tenant Enterprise platform, guaranteeing strict data isolation is critical. A tenant MUST NEVER be able to read or query telemetry, incidents, or configurations belonging to another tenant.

Sentinels enforces this strict isolation across the entire technology stack using the following mechanisms:

## 1. API Authorization Boundaries (FastAPI & Keycloak)
- Every request to the Management API requires an OIDC JWT signed by Keycloak.
- The JWT contains a custom `tenant_id` claim.
- **Middleware Enforcement**: The FastAPI `TenantMiddleware` extracts the `tenant_id` from the JWT and injects it into the request context. If a user attempts to access an endpoint (e.g., `/api/v1/sensors/sensor-xyz`), the backend asserts `sensor.tenant_id == request.tenant_id`. Any mismatch results in a hard `403 Forbidden`.

## 2. PostgreSQL Row-Level Security (RLS)
- We utilize PostgreSQL's native Row-Level Security (RLS).
- Every table (`sensors`, `configurations`, `incidents`) has a `tenant_id` column.
- **Policy**: `CREATE POLICY tenant_isolation_policy ON sensors USING (tenant_id = current_setting('app.current_tenant'));`
- Even if an SQL injection vulnerability exists in the API, the database engine itself mathematically prevents cross-tenant data leakage.

## 3. OpenSearch Isolation
- Telemetry data is never stored in a massive, flat index.
- We utilize **Tenant-Specific Index Routing**.
- Indices are structured as: `tenant_<uuid>-telemetry-YYYY-MM-DD`.
- When an analyst performs a Threat Hunt, the OpenSearch query is strictly scoped to `tenant_<uuid>-telemetry-*`. Cross-index wildcard searches (`*-telemetry-*`) are blocked by OpenSearch RBAC roles mapped to the user's Keycloak token.

## 4. MinIO (S3) Isolation
- Raw PCAP and malware sample binaries are stored in MinIO.
- Each tenant is assigned a dedicated S3 Bucket (`sentinels-tenant-<uuid>`).
- IAM Policies strictly restrict access to the bucket. Even if a URL is intercepted, it cannot be accessed without the tenant's specific temporary AWS STS credentials.

## Validation Conclusion
Through the layered defense of API Middleware, Database RLS, OpenSearch Indexing, and S3 IAM, we achieve complete architectural isolation. No single misconfiguration can lead to cross-tenant data spillage.
