# https://www.geeksforgeeks.org/barrier-objects-python/

from threading import Semaphore, Thread, current_thread
import threading
import functools
from time import sleep
from typing import List, Tuple
import random
from math import sqrt
from statistics import mean
from copy import deepcopy

class CustomBarrier():
    def __init__(self, parties: int) -> None:
        self.turnstile = Semaphore(0)
        self.turnstile2 = Semaphore(0)
        self.mutex = Semaphore(1)
        self.count = 0
        self.parties = parties

    def phase1(self):
        # Rendezvous
        self.mutex.acquire()
        self.count += 1
        if self.count == self.parties:
            self.turnstile.release(self.parties)
        self.mutex.release()
        self.turnstile.acquire()

    def phase2(self):
        # Critical point
        self.mutex.acquire()
        self.count -= 1
        if self.count == 0:
            self.turnstile2.release(self.parties)
        self.mutex.release()
        self.turnstile2.acquire()

    def wait(self):
        self.phase1()
        self.phase2()


class SharedMatrix():
    class LockDecorator():
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

    def __init__(self, original_matrix: List[List[int]]) -> None:
        self._matrix = original_matrix
        self._lock = threading.Lock()

    @LockDecorator.threadsafe
    def __len__(self) -> int: return len(self._matrix)

    @LockDecorator.threadsafe
    def print(self) -> None:
        pretty_print(self._matrix)

    @LockDecorator.threadsafe
    def get(self, pos: Tuple[int, int]) -> int:
        return self._matrix[pos[0]][pos[1]]

    @LockDecorator.threadsafe
    def set(self, pos: Tuple[int, int], val: int) -> None:
        self._matrix[pos[0]][pos[1]] = val


class Worker(Thread):
    def __init__(self, barrier: CustomBarrier, observer_barrier: CustomBarrier, shared_matrix: SharedMatrix, pos: Tuple[int, int], iterations: int) -> None:
        super().__init__(daemon=True)
        global g_verbose
        if g_verbose:
            self.log = lambda msg: print(f'[{current_thread()}]{msg}')
        else:
            self.log = lambda msg: None
        self.barrier = barrier
        self.matrix = shared_matrix
        self.cell = pos
        self.iterations = iterations
        self.observer_barrier = observer_barrier

    def phase_1(self):
        # Calculate average of neighboring cells
        # 1: read neighboring cells
        i, j = self.cell

        north_pos = (i - 1, j)
        south_pos = (i + 1, j)
        west_pos = (i, j - 1)
        east_pos = (i, j + 1)

        cells = []

        for pos in [north_pos, south_pos, west_pos, east_pos]:
            try:
                if pos[0] < 0 or pos[1] < 0:
                    continue

                val = self.matrix.get(pos)
                cells.append(val)
            except IndexError:
                continue

        # 2: calculate average
        return mean(cells)

    def phase_2(self, average):
        # Write average to cell
        self.matrix.set(self.cell, average)

    def run(self):
        for _ in range(self.iterations):
            avg = self.phase_1()
            self.log(f'Phase 1 complete. Average: {avg}')
            self.barrier.wait()
            self.observer_barrier.wait()
            # sleep(0.5)
            self.phase_2(avg)
            self.barrier.wait()
            self.log('Phase 2 complete')
        self.log('Done')

def pretty_print(matrix):
    s = [[str(e)[:5] for e in row] for row in matrix]
    lens = [max(map(len, col)) for col in zip(*s)]
    fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
    table = [fmt.format(*row) for row in s]
    print('\n'.join(table))


def observer(barrier: CustomBarrier, matrix: SharedMatrix):
    print('Current matrix:')
    matrix.print()
    barrier.wait()
    while True:
        barrier.wait()
        print('Current matrix:')
        matrix.print()


size = int(input('Enter with the desired N for the NxN matrix\n> '))
iterations = input('Enter with the desired number of iterations\n> ')

normal_matrix = []
for _ in range(size):
    aux = []
    for _ in range(size):
        aux.append(random.randint(0, 100))
    normal_matrix.append(aux)

old_matrix = deepcopy(normal_matrix)
matrix = SharedMatrix(normal_matrix)

PARTIES = len(matrix) ** 2
N = int(sqrt(PARTIES))

print('Starting with the following matrix:')
matrix.print()
sleep(1)

bar = CustomBarrier(PARTIES)
observer_barrier = CustomBarrier(PARTIES + 1)
workers = []

verbose_logs = input('Do you want verbose logs? [y/N]\n> ')
if verbose_logs.lower() == 'y':
    g_verbose = True
    print('! VERBOSE LOGS ARE ON !')
else:
    g_verbose = False

matrix_logger = input('Do you want to print the matrix before every write operation? [Y/n]\n> ')
if matrix_logger.lower() == 'n':
    Thread(daemon=True, target=observer, args=(observer_barrier, matrix,)).start()
else:
    None

for i in range(N):
    for j in range(N):
        worker = Worker(bar, observer_barrier, matrix, (i, j), int(iterations))
        workers.append(worker)
        worker.start()

[worker.join() for worker in workers]

print('\nDone! Started from...:')
pretty_print(old_matrix)
print('...to:')
matrix.print()
