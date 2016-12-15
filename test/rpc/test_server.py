import unittest

from rpc.server import _resolve_dotted_attribute, _prefetch_variable_names


class A:
    def __init__(self):
        self.variable1 = 'variable1 of class A'
        self.variable2 = 'variable2 of class A'


class B:
    def __init__(self):
        self.variable1 = 'variable1 of class B'
        self.variable2 = 'variable2 of class B'


class Test:
    def __init__(self):
        self.variable1 = 'v1'
        self._variable2 = 'v2'
        self.__variable3 = 'v3'
        self.variable4 = A()
        self.variable5 = B()

    def method1(self):
        return 'm1'

    def _method2(self):
        return 'm2'

    def __method3(self):
        return 'm3'

    @classmethod
    def method4(self):
        return 'm4'

    @property
    def method5(self):
        return 'm5'


class TestServer(unittest.TestCase):
    def test_resolve_dotted_attributes(self):
        t = Test()

        # resolve own self
        self.assertEqual(t, _resolve_dotted_attribute(t, 'self'))

        # resolve attributes (instance variables)
        self.assertEqual(t.variable1, _resolve_dotted_attribute(t, 'variable1'))
        self.assertEqual(t._variable2, _resolve_dotted_attribute(t, '_variable2'))
        self.assertRaises(AttributeError, lambda: _resolve_dotted_attribute(t, '__variable3'))
        self.assertEqual(t.variable4, _resolve_dotted_attribute(t, 'variable4'))
        self.assertEqual(t.variable5, _resolve_dotted_attribute(t, 'variable5'))

        # resolve attributes (instance methods)
        self.assertEqual(t.method1(), _resolve_dotted_attribute(t, 'method1')())
        self.assertEqual(t._method2(), _resolve_dotted_attribute(t, '_method2')())
        self.assertRaises(AttributeError, lambda: _resolve_dotted_attribute(t, '__method3')())
        self.assertEqual(t.method4(), _resolve_dotted_attribute(t, 'method4')())
        self.assertEqual(t.method5, _resolve_dotted_attribute(t, 'method5'))

    def test_prefetch(self):
        t = Test()

        # prefetch variable names of the instance
        self.assertIn('variable1', _prefetch_variable_names(t, 'self'))
        self.assertNotIn('_variable2', _prefetch_variable_names(t, 'self'))
        self.assertNotIn('__variable3', _prefetch_variable_names(t, 'self'))
        self.assertIn('variable4', _prefetch_variable_names(t, 'self'))
        self.assertIn('variable5', _prefetch_variable_names(t, 'self'))

        # prefetch variable names of the inner variable
        self.assertIn('variable1', _prefetch_variable_names(t, 'variable4'))
        self.assertIn('variable2', _prefetch_variable_names(t, 'variable4'))
        self.assertIn('variable1', _prefetch_variable_names(t, 'variable5'))
        self.assertIn('variable2', _prefetch_variable_names(t, 'variable5'))


if __name__ == '__main__':
    unittest.main()
