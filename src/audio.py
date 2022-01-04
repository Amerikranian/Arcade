import synthizer

from synthizer import (
    Buffer,
    BufferGenerator,
    StreamingGenerator,
    Context,
    DirectSource,
    Generator,
    GlobalEcho,
    GlobalFdnReverb,
    Source,
    ScalarPannedSource,
    Source3D,
)


class BufferCache:
    def __init__(self, file_manager, max_size=1024 ** 2 * 512):
        self.file_manager = file_manager
        self.max_size = max_size
        self.paths = []
        self.buffers = dict()
        self.current_size = 0

    def get_size(self, buffer):
        return buffer.get_channels() * buffer.get_length_in_samples() * 2

    def get_buffer(self, path):
        if path not in self.buffers:
            buffer = self.file_manager.get_buffer(path)
            self.paths.insert(0, path)
            self.buffers[path] = buffer
            self.current_size += self.get_size(buffer)
            self.clean_buffers()
        return self.buffers[path]

    def clean_buffers(self):
        while self.current_size > self.max_size and len(self.paths) > 1:
            self.pop_buffer().destroy()

    def pop_buffer(self):
        path = self.paths.pop()
        buffer = self.buffers.pop(path)
        self.current_size -= self.get_size(buffer)
        return buffer

    def destroy_all(self):
        while len(self.paths) > 0:
            self.pop_buffer().destroy()
        self.current_size = 0


class SoundManager:
    def __init__(self, synthizer_context, buffer_cache, **kwargs):
        self.synthizer_context = synthizer_context
        self.buffer_cache = buffer_cache
        self.sounds = []
        self.defaults = kwargs

    @property
    def position(self):
        return self.synthizer_context.position[:3]

    def register_sound(self, sound):
        self.sounds.append(sound)

    def unregister_sound(self, sound):
        self.sounds.remove(sound)
        sound.destroy()

    def destroy_all(self):
        while len(self.sounds) > 0:
            self.unregister_sound(self.sounds[0])

    def play(self, path, stream=False, **kwargs):
        if not kwargs:
            kwargs = self.defaults
        if not stream:
            buffer = self.buffer_cache.get_buffer(path)
            generator = BufferGenerator(self.synthizer_context)
            generator.buffer.value = buffer
        else:
            buffer = None
            generator = StreamingGenerator.from_file(self.synthizer_context, path)
        sound = Sound(self.synthizer_context, generator, buffer, **kwargs)
        sound.play()
        self.register_sound(sound)
        return sound

    def stream(self, path, **kwargs):
        return self.play(path, True, **kwargs)

    def set_position(self, position):
        self.synthizer_context.position = position

    def update(self):
        for event in self.synthizer_context.get_events():
            if (
                isinstance(event, synthizer.FinishedEvent)
                and event.source != None
                and event.source.get_userdata() in self.sounds
            ):
                sound = event.source.get_userdata()
                if sound.on_finish:
                    sound.on_finish()
                self.unregister_sound(sound)


class Sound:
    def __init__(self, synthizer_context, generator, buffer=None, **kwargs):
        self.synthizer_context = synthizer_context
        self.buffer = buffer
        self.generator = generator
        self.source = None
        self._position = kwargs.setdefault("position", None)
        self._paused = True
        self.destroyed = False
        self.set_source()
        self.set_properties(kwargs)

    @property
    def looping(self):
        if self.destroyed:
            return False
        return self.generator.looping

    @looping.setter
    def looping(self, value):
        if not self.destroyed:
            self.generator.looping.value = value

    @property
    def volume(self):
        if self.destroyed:
            return -1
        return self.generator.gain

    @volume.setter
    def volume(self, value):
        if not self.destroyed:
            if value > 0:
                self.generator.gain.value = value
            else:
                self.generator.gain.value = 0

    @property
    def seek(self):
        if self.destroyed:
            return -1
        return self.generator.position

    @seek.setter
    def seek(self, value):
        if not self.destroyed:
            if value > 0:
                self.generator.position.value = value
            else:
                self.generator.position.value = 0

    @property
    def pitch_bend(self):
        if self.destroyed:
            return -1
        return self.generator.pitch_bend

    @pitch_bend.setter
    def pitch_bend(self, value):
        if not self.destroyed:
            if value > 0:
                self.generator.pitch_bend.value = value
            else:
                self.generator.pitch_bend.value = 0

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value
        if not self.destroyed and self.position:
            self.source.position.value = value

    @property
    def paused(self):
        if self.destroyed:
            return True
        return self._paused

    @paused.setter
    def paused(self, value):
        if not self.destroyed:
            if value == True:
                self.pause()
            else:
                self.play()

    def pause(self):
        if not self.destroyed:
            self._paused = True
            self.source.pause()

    def play(self):
        if not self.destroyed:
            self._paused = False
            self.source.add_generator(self.generator)
            self.source.play()

    def seek_by(self, amount):
        if not self.destroyed:
            if self.generator.position + amount > 0:
                self.generator.position += amount
            else:
                self.generator.position = 0

    def set_properties(self, properties):
        if not self.destroyed:
            self.generator.set_userdata(self)
            self.volume = properties.setdefault("gain", 1.0)
            self.looping = properties.setdefault("looping", False)
            self.pitch_bend = properties.setdefault("pitch_bend", 1.0)
            self.position = properties.setdefault("position", None)
            self.on_finish = properties.setdefault("on_finish", None)

    def set_source(self):
        if self.source != None:
            self.source.destroy()
            self.source = None
        if self.position == None:
            source = DirectSource(self.synthizer_context)
        elif isinstance(self.position, int) or isinstance(self.position, float):
            source = ScalarPannedSource(self.synthizer_context)
            source.panning_scalar = self.position
        elif isinstance(self.position, tuple):
            source = Source3D(self.synthizer_context)
            source.position.value = self.position
        self.source = source

    def destroy(self):
        self.pause()
        try:
            self.generator.dec_ref()
            self.source.dec_ref()
        except:
            pass
        self.destroyed = True

    def restart(self):
        self.generator.position.value = 0.0
