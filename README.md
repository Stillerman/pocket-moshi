```
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