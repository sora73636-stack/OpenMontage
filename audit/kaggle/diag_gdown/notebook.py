import subprocess, time, datetime
def sh(c, t=600):
    print("$", c, flush=True)
    p = subprocess.run(c, shell=True, capture_output=True, text=True, timeout=t)
    print("rc", p.returncode, "out", p.stdout[-400:], "err", p.stderr[-400:], flush=True)
print("start", datetime.datetime.utcnow().isoformat(), flush=True)
sh("python -m pip install -q gdown")
sh("python -m gdown 1ZKjcbmt1hypiFprJPIKW0Tt0lr_2i7bg -O /kaggle/working/rife_4_25 --no-cookies")
for i in range(6):
    print("tick", i, datetime.datetime.utcnow().isoformat(), flush=True)
    time.sleep(10)
print("done", datetime.datetime.utcnow().isoformat(), flush=True)
