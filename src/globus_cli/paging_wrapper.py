from typing import Iterator, Optional


# wrap to add a `has_next()` method and `limit` param to a naive iterator
class PagingWrapper:
    def __init__(self, iterator: Iterator, limit: Optional[int] = None):
        self.iterator = iterator
        self.next = None
        self.limit = limit
        self._step()

    def _step(self):
        try:
            self.next = next(self.iterator)
        except StopIteration:
            self.next = None

    def has_next(self):
        return self.next is not None

    def __iter__(self):
        yielded = 0
        while self.has_next() and (self.limit is None or yielded < self.limit):
            cur = self.next
            self._step()
            yield cur
            yielded += 1
