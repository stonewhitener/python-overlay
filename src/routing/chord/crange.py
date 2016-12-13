class crange:
    """Circular Range Class

    >>> crange(6, 2 ** 3)
    crange(start=0, stop=6, step=1, modulo=8)
    >>> crange(6, 2, 2 ** 3)
    crange(start=6, stop=2, step=1, modulo=8)
    >>> crange(7, -1, 2, 2 ** 3)
    crange(start=7, stop=-1, step=2, modulo=8)

    >>> list(crange(0, 0, 2 ** 3))
    [0, 1, 2, 3, 4, 5, 6, 7]
    >>> list(crange(4, 4, 2 ** 3))
    [4, 5, 6, 7, 0, 1, 2, 3]
    >>> list(crange(0, 4, 2 ** 3))
    [0, 1, 2, 3]
    >>> list(crange(4, 0, 2 ** 3))
    [4, 5, 6, 7]
    >>> list(crange(2, 6, 2 ** 3))
    [2, 3, 4, 5]
    >>> list(crange(6, 2, 2 ** 3))
    [6, 7, 0, 1]

    >>> list(crange(7, -1, -1, 2 ** 3))
    [7, 6, 5, 4, 3, 2, 1, 0]
    >>> list(crange(3, 3, -1, 2 ** 3))
    [3, 2, 1, 0, 7, 6, 5, 4]
    >>> list(crange(3, -1, -1, 2 ** 3))
    [3, 2, 1, 0]
    >>> list(crange(7, 3, -1, 2 ** 3))
    [7, 6, 5, 4]
    >>> list(crange(5, 1, -1, 2 ** 3))
    [5, 4, 3, 2]
    >>> list(crange(1, 5, -1, 2 ** 3))
    [1, 0, 7, 6]

    >>> list(crange(4, 4, 3, 2 ** 3))
    [4, 7, 2]
    >>> list(crange(4, 4, -3, 2 ** 3))
    [4, 1, 6]

    >>> 6 in crange(6, 2, 2 ** 3)
    True
    >>> 2 in crange(6, 2, 2 ** 3)
    False
    >>> 7 in crange(4, 4, 3, 2 ** 3)
    True
    >>> 3 in crange(4, 4, 3, 2 ** 3)
    False
    >>> 1 in crange(4, 4, -3, 2 ** 3)
    True
    >>> 3 in crange(4, 4, -3, 2 ** 3)
    False

    >>> for i in crange(6, 3, 2 ** 3):
    ...     print(i)
    6
    7
    0
    1
    2
    """
    def __init__(self, start, stop, step=None, modulo=None):
        if step is None and modulo is None:
            self.start = 0
            self.stop = start
            self.step = 1
            self.modulo = stop
        else:
            self.start = start
            self.stop = stop
            if modulo is None:
                self.step = 1
                self.modulo = step
            else:
                self.step = step
                self.modulo = modulo

        if not (0 <= self.start < self.modulo):
            raise ValueError('crange() start must be in [0, modulo)')
        if not (-1 <= self.stop <= self.modulo):
            raise ValueError('crange() stop must be in [-1, modulo]')
        if self.step == 0:
            raise ValueError('crange() step must not be zero')
        if type(self.start) is not int or type(self.stop) is not int or type(self.step) is not int or type(self.modulo) is not int:
            raise TypeError('crange() arg must be an integer')

    def __iter__(self):
        n = self.start
        if self.step > 0:
            if n >= self.stop:
                while n < self.modulo:
                    yield n
                    n += self.step
                n %= self.modulo
            while n < self.stop:
                yield n % self.modulo
                n += self.step
        else:
            if n <= self.stop:
                while n >= 0:
                    yield n
                    n += self.step
                n %= self.modulo
            while n > self.stop:
                yield n
                n += self.step

    def __contains__(self, n):
        if (n - self.start) % self.step == 0:
            if self.step > 0:
                if self.start >= self.stop:
                    return self.start <= n < self.modulo or 0 <= n < self.stop
                else:
                    return self.start <= n < self.stop
            else:
                if self.start <= self.stop:
                    return self.start >= n >= 0 or self.modulo > n > self.stop
                else:
                    return self.start >= n > self.stop
        else:
            return False

    def __repr__(self):
        return 'crange(start={}, stop={}, step={}, modulo={})'.format(self.start, self.stop, self.step, self.modulo)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
