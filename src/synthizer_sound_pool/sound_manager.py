import synthizer


class SoundManager:
    def __init__(self, ctx, buffer_cache):
        self.synthizer_context = ctx
        self.buffer_cache = buffer_cache

    def get_file(self, filename):
        return self.buffer_cache.get_buffer(filename)

    def get_file_stream(self, filename):
        return synthizer.StreamHandle.from_file(filename)

    def update_generic_sound_values(self, generator, source, **kwargs):
        """Updates generators and sources irrespective of type"""
        offset = kwargs.get("offset", None)
        if offset is not None:
            generator.playback_position = offset
        looping = kwargs.get("looping", False)
        generator.looping = looping
        gain = kwargs.get("gain", None)
        if gain is not None:
            source.gain = 10 ** (gain / 20)

    def update_3d_sound_values(self, generator, source, **kwargs):
        # We allow for implicit Y and Z
        pos = (kwargs.get("x", None), kwargs.get("y", 0), kwargs.get("z", 0))
        if pos[0] is not None:
            source.position = pos
        self.update_generic_sound_values(generator, source, **kwargs)

    def dec_src_ref(self, src, should_stop=True):
        if should_stop:
            src.pause()
        src.dec_ref()

    def play_3d_source(self, filename, lingering=True, dec_ref=True, **kwargs):
        buff = self.get_file(filename)
        gen = synthizer.BufferGenerator(self.synthizer_context)
        gen.buffer = buff
        src = synthizer.Source3D(self.synthizer_context)
        # Do any user configuration
        self.update_3d_sound_values(gen, src, **kwargs)
        src.config_delete_behavior(linger=lingering)
        src.add_generator(gen)
        if dec_ref:
            src.dec_ref()

        # No guarantees that, if dec_ref is set to True, the user won't do anything dumb
        return (gen, src)

    def stream(self, filename, **kwargs):
        stream_handle = self.get_file_stream(filename)
        gen = synthizer.StreamingGenerator.from_stream_handle(
            self.synthizer_context, stream_handle
        )
        src = synthizer.DirectSource(self.synthizer_context)
        self.update_generic_sound_values(gen, src, **kwargs)
        src.add_generator(gen)
        # The user is responsible for keeping track of sources and dec_ref
        return (gen, src)
