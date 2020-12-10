import datetime
import json
import sys
import time


for line in sys.stdin:
    p = json.loads(line)
    if 'ts' not in p:
        continue

    p['ts'] = datetime.datetime.fromtimestamp(time.mktime(tuple(p['ts'] + [0])))
    
    print(p['ts'].strftime('%Y-%m-%dT%H:%M:%S'), p['h'], p['t'])
