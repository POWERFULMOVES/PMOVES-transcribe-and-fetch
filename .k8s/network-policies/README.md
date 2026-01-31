# Kubernetes Network Policies for PMOVES.AI

## 5-Tier Network Architecture

This directory contains Kubernetes NetworkPolicy manifests implementing defense-in-depth network segmentation for PMOVES.AI services.

### Network Tiers

| Tier | Subnet | Purpose | Internal Only |
|------|--------|---------|---------------|
| **api-tier** | 172.30.1.0/24 | API gateways, REST endpoints | No |
| **app-tier** | 172.30.2.0/24 | Business logic services | No |
| **bus-tier** | 172.30.3.0/24 | NATS message bus | No |
| **data-tier** | 172.30.4.0/24 | Databases, storage | **Yes** |
| **monitoring-tier** | 172.30.5.0/24 | Observability stack | No |

### Traffic Flow Rules

1. **External → API Tier**: Allowed (ingress)
2. **API Tier → App Tier**: Allowed (service-to-service)
3. **API Tier → Bus Tier**: Allowed (event publishing)
4. **App Tier → Data Tier**: Allowed (database access)
5. **App Tier → Bus Tier**: Allowed (event publishing)
6. **Data Tier → All**: **DENIED** (no outbound initiation)
7. **Monitoring Tier → All**: Allowed (scrape/read access)

### Applying Policies

```bash
# Apply all policies
kubectl apply -f .k8s/network-policies/

# Apply specific tier
kubectl apply -f .k8s/network-policies/data-tier-policy.yaml
```

### Validation

```bash
# Verify policies are applied
kubectl get networkpolicies -A

# Test connectivity between tiers
kubectl exec -it <api-pod> -- curl -s http://<data-service>:<port>
```

## Security Considerations

- Data tier cannot initiate outbound connections (prevents data exfiltration)
- All cross-tier communication must be explicitly allowed
- Monitoring has read-only access to all tiers
- External access only via API tier ingress
