import unittest

from routing.chord.crange import crange


class TestCrange(unittest.TestCase):
    def test_init(self):
        self.assertEqual(crange(6, 2 ** 3), crange(start=0, stop=6, step=1, modulo=8))
        self.assertEqual(crange(6, 2, 2 ** 3), crange(start=6, stop=2, step=1, modulo=8))
        self.assertEqual(crange(7, -1, 2, 2 ** 3), crange(start=7, stop=-1, step=2, modulo=8))

    def test_iter(self):
        self.assertEqual(list(crange(0, 0, 2 ** 3)), [0, 1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(list(crange(4, 4, 2 ** 3)), [4, 5, 6, 7, 0, 1, 2, 3])
        self.assertEqual(list(crange(0, 4, 2 ** 3)), [0, 1, 2, 3])
        self.assertEqual(list(crange(4, 0, 2 ** 3)), [4, 5, 6, 7])
        self.assertEqual(list(crange(2, 6, 2 ** 3)), [2, 3, 4, 5])
        self.assertEqual(list(crange(6, 2, 2 ** 3)), [6, 7, 0, 1])

        self.assertEqual(list(crange(7, -1, -1, 2 ** 3)), [7, 6, 5, 4, 3, 2, 1, 0])
        self.assertEqual(list(crange(3, 3, -1, 2 ** 3)), [3, 2, 1, 0, 7, 6, 5, 4])
        self.assertEqual(list(crange(3, -1, -1, 2 ** 3)), [3, 2, 1, 0])
        self.assertEqual(list(crange(7, 3, -1, 2 ** 3)), [7, 6, 5, 4])
        self.assertEqual(list(crange(5, 1, -1, 2 ** 3)), [5, 4, 3, 2])
        self.assertEqual(list(crange(1, 5, -1, 2 ** 3)), [1, 0, 7, 6])

        self.assertEqual(list(crange(4, 4, 3, 2 ** 3)), [4, 7, 2])
        self.assertEqual(list(crange(4, 4, -3, 2 ** 3)), [4, 1, 6])

    def test_contains(self):
        self.assertTrue(6 in crange(6, 2, 2 ** 3))
        self.assertFalse(2 in crange(6, 2, 2 ** 3))
        self.assertTrue(7 in crange(4, 4, 3, 2 ** 3))
        self.assertFalse(3 in crange(4, 4, 3, 2 ** 3))
        self.assertTrue(1 in crange(4, 4, -3, 2 ** 3))
        self.assertFalse(3 in crange(4, 4, -3, 2 ** 3))


if __name__ == '__main__':
    unittest.main()
