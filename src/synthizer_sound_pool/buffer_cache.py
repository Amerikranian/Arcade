from collections import OrderedDict
from synthizer import Buffer


class BufferCache:
    def __init__(self, max_size, is_in_bytes=False):
        self.current_size = 0
        self.max_size = max_size * 1024 ** 2 if not is_in_bytes else max_size
        self.buffers = OrderedDict()

    def is_full(self):
        return self.current_size >= self.max_size

    def clean(self, requested_size):
        while (
            self.current_size + requested_size >= self.max_size
            and len(self.buffers) > 0
        ):
            # Should probably be changed in the future to discard buffers based on usage rather than load order
            self.buffers.popitem(last=False)

    def add_buffer(self, key):
        buffer = Buffer.from_file(key)
        buffer_size = buffer.get_size_in_bytes()
        if self.is_full():
            self.clean(buffer_size)
        self.buffers[key] = buffer
        self.current_size += buffer_size

    def get_buffer(self, filename):
        if filename not in self.buffers:
            self.add_buffer(filename)
        return self.buffers[filename]
