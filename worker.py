from shared_matrix import SharedMatrix
from custom_barrier import CustomBarrier
from threading import Thread, current_thread
from typing import Tuple, Union
from statistics import mean


class Worker(Thread):
    def __init__(self, barrier: CustomBarrier, observer_barrier: Union[CustomBarrier, None], shared_matrix: SharedMatrix, pos: Tuple[int, int], iterations: int, verbose_logging: bool) -> None:
        super().__init__(daemon=True)

        if verbose_logging:
            self.log = lambda msg: print(f'[{current_thread()}]{msg}')
        else:
            self.log = lambda _: None

        self.observer_barrier = observer_barrier
        self.barrier = barrier
        self.matrix = shared_matrix
        self.cell = pos
        self.iterations = iterations

    def phase_1(self):
        # Calculate average of neighboring cells
        # Step 1: Read neighboring cells
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

        # Step 2: Calculate average
        return mean(cells)

    def phase_2(self, average) -> None:
        # Write average to cell
        self.matrix.set(self.cell, average)

    def run(self):
        for _ in range(self.iterations):
            avg = self.phase_1()
            self.log(f'Phase 1 complete. Average: {avg}')
            self.barrier.wait()

            if self.observer_barrier != None:
                self.observer_barrier.wait()

            self.phase_2(avg)
            self.barrier.wait()
            self.log('Phase 2 complete')
        self.log('Done')
