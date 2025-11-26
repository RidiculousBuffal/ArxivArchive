import os
import sys
import time
os.environ['TZ'] = 'Asia/Shanghai'
if sys.platform != "win32":
    time.tzset()