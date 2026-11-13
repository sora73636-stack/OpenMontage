import time, datetime, torch
print("GPU diag start", datetime.datetime.utcnow().isoformat())
print("devices", torch.cuda.device_count(), [torch.cuda.get_device_name(i) for i in range(torch.cuda.device_count())])
time.sleep(5)
print("GPU diag done", datetime.datetime.utcnow().isoformat())
