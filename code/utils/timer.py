import csv
import os
import time

_CSV_FIELDS = ["fragment", "variant", "task", "element", "tseitin", "total_time"]


class Timer:
    def __init__(
        self,
        message=None,
        file="result.csv",
        block=False,
        fragment=None,
        variant=None,
        task=None,
        element=None,
        tseitin=None,
        extra_time=0.0,
    ):
        self.message = message
        self.block = block
        self._t = None
        self.file = file
        self.fragment = fragment
        self.variant = variant
        self.task = task
        self.element = element
        self.tseitin = tseitin
        self.extra_time = extra_time

    def __enter__(self):
        self._t = time.time()
        return self

    def __exit__(self, *args, **kwargs):
        elapsed = time.time() - self._t + self.extra_time
        if self.block and self.fragment is not None and self.file:
            self._write_csv_row(elapsed)
        elif self.message:
            print(f"[{self.message}] {elapsed:.6f}s")

    def _write_csv_row(self, elapsed):
        needs_header = not os.path.exists(self.file) or os.path.getsize(self.file) == 0
        with open(self.file, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=_CSV_FIELDS)
            if needs_header:
                writer.writeheader()
            writer.writerow(
                {
                    "fragment": self.fragment,
                    "variant": self.variant or "",
                    "task": self.task,
                    "element": self.element,
                    "tseitin": "" if self.tseitin is None else str(self.tseitin),
                    "total_time": "%.6f" % elapsed,
                }
            )
