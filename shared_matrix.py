import functools
from typing import Tuple, List
import threading


class SharedMatrix():
    class SharedMatrixDecorator():
        @classmethod
        def threadsafe(cls, func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if isinstance(args[0], SharedMatrix):
                    cs = args[0]._lock
                    try:
                        cs.acquire()
                        ret = func(*args, **kwargs)
                    finally:
                        cs.release()
                    return ret
                return None
            return wrapper

    @staticmethod
    def pretty_print(matrix) -> None:
        s = [[str(e)[:5] for e in row] for row in matrix]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        print('\n'.join(table))

    def __init__(self, original_matrix: List[List[int]]) -> None:
        self._matrix = original_matrix
        self._lock = threading.Lock()

    @SharedMatrixDecorator.threadsafe
    def __len__(self) -> int: return len(self._matrix)

    @SharedMatrixDecorator.threadsafe
    def get(self, _p: Tuple[int, int]) -> int: return self._matrix[_p[0]][_p[1]]

    @SharedMatrixDecorator.threadsafe
    def set(self, _p: Tuple[int, int], val: int) -> None:
        self._matrix[_p[0]][_p[1]] = val

    @SharedMatrixDecorator.threadsafe
    def print(self) -> None:
        self.pretty_print(self._matrix)

