# /app/rp_handler.py
import os, subprocess, time, json, socket
from pathlib import Path
import runpod

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

def start_moshi():
    # Determine our public ip (RunPod exposes it; clients will connect to it)
    public_ip = os.getenv("PUBLIC_IP") or subprocess.getoutput("hostname -I").split()[0]
    tcp_port = PORT

    print(json.dumps({"msg": "starting_moshi", "public_ip": public_ip, "tcp_port": tcp_port}), flush=True)

    moshi = subprocess.Popen([
        "moshi-server","worker","--config", CFG, "--port", str(PORT)
    ])

    # Wait a moment for Moshi to start up
    time.sleep(10)
    
    # Check if Moshi started successfully
    if moshi.poll() is not None:
        return None, f"Moshi failed to start with code {moshi.returncode}"
    
    return moshi, {"status": "ready", "public_ip": public_ip, "tcp_port": tcp_port}

def handler(job):
    """RunPod serverless handler function"""
    print(json.dumps({"msg": "job_received", "job_id": job.get("id")}), flush=True)
    
    moshi, result = start_moshi()
    
    if moshi is None:
        return {"error": result}
    
    # Return connection info immediately so client can connect
    print(json.dumps({"msg": "moshi_ready", "returning_connection_info": result}), flush=True)
    
    # Note: In serverless, the container stays alive for a while after returning
    # The monitoring will happen in background until container shuts down
    
    return result

if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})

