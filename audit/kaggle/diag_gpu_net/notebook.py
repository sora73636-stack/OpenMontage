import time, datetime, torch, urllib.request
print("GPU+net diag start", datetime.datetime.utcnow().isoformat())
print("devices", torch.cuda.device_count())
try:
    print("http", urllib.request.urlopen("https://pypi.org/simple/", timeout=10).status)
except Exception as e:
    print("http error", e)
for i in range(14):
    print("tick", i, datetime.datetime.utcnow().isoformat(), flush=True)
    time.sleep(10)
print("GPU+net diag done", datetime.datetime.utcnow().isoformat())
