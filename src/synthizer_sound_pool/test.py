import synthizer
import time
from buffer_cache import BufferCache
from sound_manager import SoundManager


with synthizer.initialized(
    log_level=synthizer.LogLevel.DEBUG, logging_backend=synthizer.LoggingBackend.STDERR
):
    ctx = synthizer.Context()
    ctx.default_panner_strategy = synthizer.PannerStrategy.HRTF
    buffer_cache = BufferCache(512)
    sndmgr = SoundManager(ctx, buffer_cache)
    gen, src = sndmgr.stream("snd.mp3", looping=True, gain=-5)
    # print(dir(gen), dir(src))
    time.sleep(12)
    input()
