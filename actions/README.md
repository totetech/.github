# Shared GitHub Actions

Reusable composite actions for the totetech organization. These actions contain **no project-specific defaults** — all sensitive values (GCP project IDs, service accounts, registry paths) must be passed by the consuming workflow.

## Actions

### `gcloud-auth` — GCP Authentication via OIDC

Authenticates to Google Cloud using Workload Identity Federation. No long-lived service account keys.

**Usage:**

```yaml
permissions:
  contents: read
  id-token: write  # Required for OIDC

steps:
  - uses: actions/checkout@v4

  - name: Authenticate to Google Cloud
    uses: totetech/.github/actions/gcloud-auth@<sha>
    with:
      workload_identity_provider: 'projects/<project-number>/locations/global/workloadIdentityPools/<pool>/providers/<provider>'
      service_account: '<sa-name>@<project>.iam.gserviceaccount.com'
      access_token_lifetime: '1800'  # optional, default 30 min
      region: 'us-central1'          # optional, for Docker registry auth
```

**Inputs:**

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `workload_identity_provider` | Yes | — | WIF provider resource path |
| `service_account` | Yes | — | Service account email |
| `token_format` | No | `access_token` | Token format to request |
| `access_token_lifetime` | No | `1800` | Token lifetime in seconds |
| `region` | No | `us-central1` | Artifact Registry region for Docker auth |

### `docker-build` — Build and Push to Artifact Registry

Builds a Docker image with Buildx, pushes to GCP Artifact Registry with GitHub Actions layer caching.

**Usage:**

```yaml
steps:
  - uses: actions/checkout@v4

  - name: Authenticate to Google Cloud
    uses: totetech/.github/actions/gcloud-auth@<sha>
    with:
      workload_identity_provider: '...'
      service_account: '...'

  - name: Build and push
    id: docker-build
    uses: totetech/.github/actions/docker-build@<sha>
    with:
      image_name: 'my-repo/my-image'
      ar_registry: 'us-central1-docker.pkg.dev/my-project'
```

**Inputs:**

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| `image_name` | Yes | — | Image path in registry (e.g. `repo/image`) |
| `ar_registry` | Yes | — | Artifact Registry base path (e.g. `us-central1-docker.pkg.dev/project-id`) |
| `folder` | No | `.` | Build context directory |

**Outputs:**

| Output | Description |
|--------|-------------|
| `image_tag` | Full image tag that was pushed (`registry/repo/image:branch-sha`) |
| `digest` | Image digest (`sha256:...`) for pinning or signing |

**Features:**
- Docker Buildx with multi-layer caching (`type=gha, mode=max`)
- Branch-based tagging (`<branch>-<commit-sha>`)
- Build summary in GitHub Actions step summary (JSON)
- Build artifact uploaded (30-day retention)

## Security

- **No defaults with sensitive values** — all GCP identifiers must be passed explicitly
- **Pin by SHA** — always reference `@<commit-sha>`, not `@main`, for production workflows
- **CODEOWNERS** — changes to `actions/` require `@jatin-toteai` approval

## Versioning

Pin actions to a specific commit SHA for stability:

```yaml
# Pinned (recommended for production)
uses: totetech/.github/actions/gcloud-auth@abc1234def5678

# Branch reference (acceptable for development)
uses: totetech/.github/actions/gcloud-auth@main
```
