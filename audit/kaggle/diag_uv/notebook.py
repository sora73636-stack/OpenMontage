import subprocess, time, datetime, sys
def sh(c, t=1200):
    print("$", c, flush=True)
    p = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=t)
    print("rc", p.returncode, "out", p.stdout[-500:], "err", p.stderr[-500:], flush=True)
    return p.returncode
print("start", datetime.datetime.utcnow().isoformat(), flush=True)
sh("which uv || python -m pip install --user uv")
sh("uv venv --python 3.11 /kaggle/working/audit/envs/diag_uv")
sh("uv pip install --python /kaggle/working/audit/envs/diag_uv/bin/python torch==2.6.0 --index-url https://download.pytorch.org/whl/cu126")
sh(" /kaggle/working/audit/envs/diag_uv/bin/python -c \"import torch; print(torch.__version__, torch.cuda.device_count())\"")
for i in range(6):
    print("tick", i, datetime.datetime.utcnow().isoformat(), flush=True)
    time.sleep(10)
print("done", datetime.datetime.utcnow().isoformat(), flush=True)
