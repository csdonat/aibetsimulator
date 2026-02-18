import time
from utils.logger import get_logger

log = get_logger("TIMER")

def timed(name: str, func, *args, **kwargs):
    #  log.info(f"⏳ Starting: {name}")
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    log.info(f"✅ Finished: {name} in {end - start:.2f} sec")
    return result
