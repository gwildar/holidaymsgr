
import sys
import os
from .base_settings import *
import logging
import json

def json_patch(path):
    logger.warn("Attempting to load local settings from %r" %(path,))
    try:
        d = json.load(open(path))
    except IOError:
        logger.exception("Unable to open json settings in %r" % (path,))
        raise SystemExit(-1)
    except ValueError:
        logger.exception("Unable to parse json settings in %r" % (path,))
        raise SystemExit(-1)
    for k,v in d.items():
        globals()[k] = v
    
def patch_settings():
    env_settings = os.environ.get('JSON_SETTINGS', None)
    if env_settings is not None:
        json_patch(env_settings)
    else:
        for p in sys.path:
            path = os.path.join(p, "local_settings.json")
            if os.path.exists(path):
                json_patch(path)
                break
    
patch_settings()
