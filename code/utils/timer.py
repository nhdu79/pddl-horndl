import time


class Timer:
    def __init__(self, message=None, end=",", file="result.csv", block=False):
        self.message = message
        self.block = block
        self._t = None
        self.end = end
        self.file = file

    def __enter__(self):
        self._t = time.time()

    def __exit__(self, *args, **kwargs):
        elapsed = time.time() - self._t
        with open(self.file, "a") as f:
            f.write("%.6f" % elapsed + self.end)
