from threading import Thread
from time import sleep
import random
from math import sqrt
from copy import deepcopy
from custom_barrier import CustomBarrier
from shared_matrix import SharedMatrix
from worker import Worker


def observer(barrier: CustomBarrier, matrix: SharedMatrix) -> None:
    print('Current matrix:')
    matrix.print()
    barrier.wait()
    while True:
        barrier.wait()
        print('Current matrix:')
        matrix.print()


size = int(input('Enter with the desired N for the NxN matrix\n> '))
iterations = input('Enter with the desired number of iterations\n> ')

if input('Do you want verbose logs? [y/N]\n> ').lower() == 'y':
    verbose_logging = True
    print('! VERBOSE LOGS ARE ON !')
else:
    verbose_logging = False

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
workers = []

if input('Do you want to print the matrix before every write operation? [y/N]\n> ').lower() == 'y':
    observer_barrier = CustomBarrier(PARTIES + 1)
    Thread(daemon=True, target=observer, args=(observer_barrier, matrix,)).start()
else:
    observer_barrier = None
    None

for i in range(N):
    for j in range(N):
        worker = Worker(bar, observer_barrier, matrix, (i, j), int(iterations), verbose_logging)
        workers.append(worker)
        worker.start()

[worker.join() for worker in workers]

print('\nDone! Started from...:')
SharedMatrix.pretty_print(old_matrix)
print('...to:')
matrix.print()
