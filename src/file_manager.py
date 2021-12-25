import json


class FileManager:
    """A dummy class mostly used to offer the ability to swap file access interfaces.
    As of now, the class does not support any directory prepends when loading resources
    Any errors the class encounters are the responsibility of the caller"""

    def __init__(self, read_mode="r", write_mode="w"):
        self.read_mode = read_mode
        self.write_mode = write_mode

    def fetch_text(self, filename, read_mode=None):
        if read_mode is None:
            read_mode = self.read_mode

        with open(filename, read_mode) as f:
            data = f.read()

        return data

    def fetch_json(self, filename, read_mode=None):
        return json.loads(self.fetch_text(filename, read_mode))

    def write_text(self, data, filename, write_mode=None):
        if write_mode is None:
            write_mode = self.write_mode

        with open(filename, write_mode) as f:
            f.write(data)

    def write_json(self, data, filename, write_mode=None):
        self.write_text(json.dumps(data), filename, write_mode)
