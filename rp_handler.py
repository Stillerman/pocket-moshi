# /app/rp_handler.py
import os, subprocess, time, json, socket
from pathlib import Path

# No runpod SDK needed if you just print progress to stdout for logs;
# If you use runpod's python SDK, you can publish progress updates.
# This version is a minimal "start moshi, wait for idle" loop.

PORT = int(os.getenv("MOSHI_PORT", "8765"))
CFG  = os.getenv("MOSHI_CONFIG", "/app/configs/config-joint.toml")
IDLE_SECS = int(os.getenv("IDLE_SECS", "120"))

def has_established_conn(port: int) -> bool:
    # Check for established TCP sockets on the given port
    # Use /proc/net/tcp to avoid requiring netstat/ss if you prefer.
    try:
        out = subprocess.check_output(["ss","-tan"], text=True)
        for line in out.splitlines():
            if "ESTAB" in line and f":{port} " in line:
                return True
    except Exception:
        pass
    return False

def main():
    # Determine our public ip (RunPod exposes it; clients will connect to it)
    public_ip = os.getenv("PUBLIC_IP") or subprocess.getoutput("hostname -I").split()[0]
    tcp_port = PORT

    print(json.dumps({"msg": "starting_moshi", "public_ip": public_ip, "tcp_port": tcp_port}), flush=True)

    moshi = subprocess.Popen([
        "moshi-server","worker","--config", CFG, "--port", str(PORT)
    ])

    last_active = time.time()

    # Simple liveness/idle loop
    try:
        while True:
            time.sleep(3)
            if has_established_conn(PORT):
                last_active = time.time()
            if time.time() - last_active > IDLE_SECS:
                print(json.dumps({"msg": "idle_timeout", "idle_seconds": IDLE_SECS}), flush=True)
                break
            # exit if moshi died
            if moshi.poll() is not None:
                print(json.dumps({"msg": "moshi_exited", "code": moshi.returncode}), flush=True)
                break
    finally:
        try:
            moshi.terminate()
            moshi.wait(timeout=10)
        except Exception:
            pass

if __name__ == "__main__":
    main()

