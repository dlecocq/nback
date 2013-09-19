'''Basic tests surrounding nback'''

import unittest
from nback import Nback


class TestNback(unittest.TestCase):
    def test_basic(self):
        '''We should be able to get at the very least, a sequence'''
        nback = Nback(3, 5, 5, {1: 2, 2: 4})
        print nback.sequence(range(100))
        self.assertTrue(False)
