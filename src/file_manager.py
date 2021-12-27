import os
import json


class FileManager:
    """A dummy class mostly used to offer the ability to swap file access interfaces.
    As of now, the class does not support any directory prepends when loading resources
    Any errors the class encounters are the responsibility of the caller"""

    def __init__(self, read_mode="r", write_mode="w"):
        self.read_mode = read_mode
        self.write_mode = write_mode

    def file_exists(self, path):
        return os.path.isfile(path)

    def fetch_text(self, filename, read_mode=None):
        if read_mode is None:
            read_mode = self.read_mode

        with open(filename, read_mode) as f:
            data = f.read()

        return data

    def fetch_json(self, filename, read_mode=None, expand_primitives=True):
        data = json.loads(self.fetch_text(filename, read_mode))
        if expand_primitives:
            return self._expand_json_keys(data)
        else:
            return data

    def write_text(self, data, filename, write_mode=None):
        if write_mode is None:
            write_mode = self.write_mode

        with open(filename, write_mode) as f:
            f.write(data)

    def write_json(
        self, data, filename, write_mode=None, indent_level=4, key_sort=True
    ):
        self.write_text(
            json.dumps(data, indent=indent_level, sort_keys=key_sort),
            filename,
            write_mode,
        )

    def _expand_json_keys(self, data):
        """Converts the given dictionary keys to primitive types, only integers for now
        Since json does not automatically cast keys back to their respective types, this function aims to bridge that gap"""
        dct = {}
        for k, v in data.items():
            if k.isdigit():
                new_k = int(k)
            else:
                new_k = k
            if isinstance(v, dict):
                res = self._expand_json_keys(v)
            else:
                res = v
            dct[new_k] = res

        return dct
