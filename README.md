```
USER="jstillerman"
TOKEN="dckr_pat_xxxxxxxxxxx"

AUTH_BASE64=$(printf "%s" "$USER:$TOKEN" | base64)
export DOCKER_AUTH_CONFIG="{\"auths\":{\"https://index.docker.io/v1/\":{\"auth\":\"$AUTH_BASE64\"}}}"

REG="docker.io/jstillerman/pocket-moshi"
SHA=$(git rev-parse --short HEAD)

# Ada (RTX 4000) → 89
depot build --platform linux/amd64 --push \
  --build-arg COMPUTE_CAP=89 \
  -t ${REG}:latest -t ${REG}:cc89 -t ${REG}:${SHA}-cc89 .

# Optional extra tags for portability (run these too if you want)
depot build --platform linux/amd64 --push \
  --build-arg COMPUTE_CAP=80 \
  -t ${REG}:cc80 .

depot build --platform linux/amd64 --push \
  --build-arg COMPUTE_CAP=75 \
  -t ${REG}:cc75 .
```


## Building & Pushing Images with Depot + Docker Hub

Our images are built remotely with [Depot](https://depot.dev) and pushed to Docker Hub.  
Because Docker Hub can be picky about auth scopes, make sure to follow these steps exactly:

### 1. Create a Docker Hub Personal Access Token
- Go to: [Docker Hub Access Tokens](https://app.docker.com/account/settings/personal-access-tokens)
- Create a **New Access Token** with **Read & Write** access.
- Copy the token immediately.

### 2. Create the repo once on Docker Hub
- Log in to [Docker Hub Repositories](https://hub.docker.com/repositories/jstillerman)
- Click **Create Repository** → name it `pocket-moshi` (lowercase).
- Namespace should be `jstillerman`.

### 3. Configure registry auth for Depot
In your shell (macOS/Linux):

```bash
USER="jstillerman"
TOKEN="<YOUR_DOCKERHUB_PAT>"

AUTH_BASE64=$(printf "%s" "$USER:$TOKEN" | base64)

export DOCKER_AUTH_CONFIG='{
  "auths": {
    "docker.io":                    { "auth": "'"$AUTH_BASE64"'" },
    "registry-1.docker.io":         { "auth": "'"$AUTH_BASE64"'" },
    "https://index.docker.io/v1/":  { "auth": "'"$AUTH_BASE64"'" }
  }
```