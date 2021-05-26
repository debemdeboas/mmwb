# Matrix Data Multiprocessing With Barriers

This repository contains an implementation using a custom barrier.
The algorithm for the barrier is a two-phase barrier (or a turnstile barrier) [[1]](#1).

## Classes

This project is comprised of three main custom classes.
Their code is explained in the sections to follow.

### Shared matrix

The shared matrix class implements a thread-safe array of arrays (matrix).
Upon creation, the class creates a lock for accessing the inner matrix.
Every matrix access (either read or write) has to first acquire the critical section.

To avoid code repetition, the `SharedMatrix` class contains a `SharedMatrixDecorator` helper class, which contains a class function that implements the critical section decorator.
To make a function thread-safe, it needs to have the following signature:

```python
@SharedMatrixDecorator.threadsafe
def foo(self, *args):
    ...
```

Where `self` is of type `SharedMatrix`.

Inner code:

```python
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
```

There is an instance check before any code is executed in order to guarantee that the first argument is of type `SharedMatrix`.

### Custom barrier

The custom barrier class implements a custom barrier using three semaphores in a double turnstile manner.
Its `wait()` function is comprised of two phases, the rendezvous and the critical point (in order).

To instantiate a custom barrier of type `CustomBarrier`, you must pass the number of parties that will await on the barrier until every other member arrives.

The code has been adapted from *Barrier objects*[[1]](#1). In the book, the implementation is better explained, but here is an exerpt:

> The `__init__` method runs when we create a new `CustomBarrier` object, and initializes the instance  variables. The parameter `n` is the number of threads that
> have to invoke wait before the `CustomBarrier` opens.
> The variable `self` refers to the object the method is operating on. Since
> each barrier object has its own mutex and turnstiles, `self.mutex` refers to the
> specific mutex of the current object.

### Worker

The `Worker` class implements our worker threads.
This class inherits from `Threading.Thread`, meaning that it's its own individual thread.
Its `__init__` method receives a barrier, an observer barrier (optional), a matrix, a position, a number of iterations and a logging flag:

```python
def __init__(self, barrier: CustomBarrier, observer_barrier: Union[CustomBarrier, None], shared_matrix: SharedMatrix, pos: Tuple[int, int], iterations: int, verbose_logging: bool) -> None:
    ...
```

When the worker is started (using `.start()`), the `run()` method is called.
This method will run `self.iterations` times, calculating the average of its neighboring cells, synchronizing on the barrier, synchronizing again on the [observer](#observer) barrier, saving the average and synchronizing again on the shared barrier.

### Observer

A helper observer thread that receives a barrier and a matrix.
This thread will print the matrix after every synchronization on the barrier on an infinite loop.

## Usage

Running the script is, as is customary, as easy as:

```commandline
python main.py
```

The script will then prompt the user for more information pertaining to the program execution, such as the matrix size.

## References

<a id="1">[1]</a> 
Downey, Allen B. (2009). *The Little Book of Semaphores, Second Edition*. Chapter 3.6.7, Barrier objects.
