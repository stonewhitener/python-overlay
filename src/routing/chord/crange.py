class crange:
    """
    crange(stop, modulo) -> crange object　[0, stop)
    crange(start, stop, modulo) -> crange object
    crange(start, stop, step, modulo) -> crange object
    """
    def __init__(self, start, stop, step=None, modulo=None):
        if step == 0:
            raise ValueError('crange() arg 3 must not be zero')

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

    def __iter__(self):
        n = self.start
        if n > self.stop:
            while n < self.modulo:
                yield n
                n += 1
            n = 0
        while n < self.stop:
            yield n
            n += 1

    def __contains__(self, n):
        if self.start >= self.stop:
            return self.start <= n < self.modulo or 0 <= n < self.stop
        else:
            return self.start <= n < self.stop

    def __repr__(self):
        return 'crange({}, {}, {})'.format(self.start, self.stop, self.modulo)


if __name__ == '__main__':
    print(list(crange(7, 3, 2 ** 3)))
    print(3 in crange(7, 3, 2 ** 3))
    print(7 in crange(7, 3, 2 ** 3))
    print(1 in crange(3, 3, 2 ** 3))
