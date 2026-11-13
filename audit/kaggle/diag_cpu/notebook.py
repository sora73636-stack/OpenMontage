import time, datetime
print("CPU diag start", datetime.datetime.utcnow().isoformat())
for i in range(12):
    print("tick", i, datetime.datetime.utcnow().isoformat(), flush=True)
    time.sleep(10)
print("CPU diag done", datetime.datetime.utcnow().isoformat())
