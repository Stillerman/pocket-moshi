# syntax = docker/dockerfile:1.6

########################
# 1) Build Moshi (Rust) with CUDA feature
########################
FROM runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04 AS build

# ---- NEW: choose the compute capability (can be overridden with --build-arg) ----
ARG COMPUTE_CAP=80
ENV CUDA_COMPUTE_CAP=${COMPUTE_CAP}

# System deps for Rust + building
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    curl ca-certificates build-essential pkg-config libssl-dev git \
 && rm -rf /var/lib/apt/lists/*

# Install rustup/cargo
ENV CARGO_HOME=/root/.cargo \
    RUSTUP_HOME=/root/.rustup \
    PATH=/root/.cargo/bin:$PATH
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y

# Cache cargo registry & git between builds
# (kaniko + BuildKit honor these mounts to reduce rebuild time)
RUN --mount=type=cache,target=/root/.cargo/registry \
    --mount=type=cache,target=/root/.cargo/git \
    cargo install --locked --features cuda moshi-server

########################
# 2) Final runtime image (RunPod PyTorch CUDA 12.8.1, Python 3.11)
########################
FROM runpod/pytorch:2.8.0-py3.11-cuda12.8.1-cudnn-devel-ubuntu22.04

# Minimal runtime packages (optional)
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    ca-certificates net-tools iproute2 procps \
 && rm -rf /var/lib/apt/lists/*

# Copy Moshi binary
COPY --from=build /root/.cargo/bin/moshi-server /usr/local/bin/moshi-server

# Copy configs (adjust if your config is named differently)
WORKDIR /app
COPY configs ./configs

# (Optional) If you want the tiny RunPod handler available:
COPY rp_handler.py /app/rp_handler.py

# Expose the port Moshi will bind to
EXPOSE 8765/tcp

# Default command: run Moshi directly (pure WS server)
# For Serverless worker pattern you can override CMD to `python /app/rp_handler.py`
CMD ["moshi-server","worker","--config","/app/configs/config-tts.toml","--port","8765"]

