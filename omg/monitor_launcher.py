import sys
import os

OMG_DIR = r"C:\Users\log\Desktop\Code\omg"
os.chdir(OMG_DIR)
sys.path.insert(0, OMG_DIR)

log_path = os.path.join(OMG_DIR, "logs", "monitor_stdout.log")
os.makedirs(os.path.dirname(log_path), exist_ok=True)
log_file = open(log_path, "a", encoding="utf-8", buffering=1)
sys.stdout = log_file
sys.stderr = log_file

import traceback
try:
    from crypto_realtime_monitor import main
    main()
except Exception as e:
    traceback.print_exc()
finally:
    log_file.close()
