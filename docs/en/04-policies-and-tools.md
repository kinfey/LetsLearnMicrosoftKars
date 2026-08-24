# 4. Inference, Tool, MCP, and Egress Policies

## Policy layers

KARS separates workload code from governance:

1. `InferencePolicy` selects models and sets token budgets.
2. `ToolPolicy` controls tool use and rate limits.
3. `McpServer` registers a tool server and its authentication requirements.
4. Egress policy controls destinations the sandbox can reach.

This separation lets platform teams own guardrails while application teams own
agent prompts and logic.

## Inference budgets

Create or update a policy through the CLI:

```bash
kars ip apply daily-budget \
  --sandbox hello \
  --model gpt-4.1 \
  --token-budget 100000
```

Budgets limit blast radius and cost; they do not replace Azure quotas or cost
alerts. Inspect the resulting resource rather than assuming a successful CLI
exit means the router loaded it:

```bash
kars policy show hello
kubectl get inferencepolicy -n kars-system -o yaml
```

## Tool policy

The following applies a broad development rule with explicit rate limits:

```bash
kars tp apply dev-tools \
  --tool '*' \
  --rps 10 \
  --burst 20
```

For production, replace `*` with named tools and grant only the operations the
agent requires.

## MCP registration

Register a production MCP server with OAuth metadata and an allowlisted tool:

```bash
kars mcp apply research-mcp \
  --url https://mcp.example.com \
  --production-mode \
  --oauth-issuer https://login.example.com \
  --oauth-audience mcp-api \
  --allowed-tool search
```

Do not bake MCP credentials into the agent image. Route identity and access
through the platform contract.

## Learn, approve, enforce

KARS egress starts in learning mode by default. Learning records unknown
non-blocklisted hosts; it is not strict production enforcement.

```bash
kars egress hello --learn
# Exercise only the intended workflow.
kars egress hello --learned
kars egress hello --approve api.github.com
kars egress hello --enforce
```

Review every learned destination. Do not automatically approve the list:
untrusted content may deliberately trigger an unwanted host during learning.
Use `EgressApproval` for temporary, TTL-bounded exceptions rather than widening
the permanent baseline.

## Signed policy bundles

Advanced environments can package policies as OCI artifacts, reference them by
digest, and verify signatures with cosign. Digest pinning prevents tag drift;
signature verification establishes publisher intent. The sandbox should become
ready only after the router reports that it loaded the expected digest.

## Exercise

Give a sandbox a daily inference budget, allow one named tool, observe required
network destinations in learning mode, approve the minimum set, and switch to
enforcement. Confirm an unapproved destination is denied in the audit stream.

## Official references

- [CLI reference](https://github.com/Azure/kars/blob/main/docs/cli-reference.md)
- [CRD reference](https://github.com/Azure/kars/blob/main/docs/api/crd-reference.md)
- [Security](https://github.com/Azure/kars/blob/main/docs/security.md)
