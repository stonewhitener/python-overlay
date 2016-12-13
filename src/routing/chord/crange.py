class crange:
    """\
    Circular Range Class
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

    def __eq__(self, other):
        if type(other) is crange:
            return self.start == other.start and self.stop == other.stop and self.step == other.step and self.modulo == other.modulo
        else:
            return False
