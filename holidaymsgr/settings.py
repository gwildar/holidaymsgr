
import sys
import os
from .base_settings import *

import json

def json_patch(path):
    try:
        d = json.load(open(path))
    except IOError:
        print >>sys.stderr, "Unable to open json settings in %r" % (path,)
        raise SystemExit(-1)
    except ValueError:
        print >>sys.stderr, "Unable to parse json settings in %r" % (path,)
        raise SystemExit(-1)
    for k,v in d.items():
        globals()[k] = v
    
def patch_settings():
    for p in sys.path:
        path = os.path.join(p, "local_settings.json")
        if os.path.exists(path):
            json_patch(path)
            break
    

patch_settings()
