from threading import Semaphore


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
