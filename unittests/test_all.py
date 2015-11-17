__author__ = 'Andrei'

import unittest
from GeneralUtils_tests import InternetIOTest

class HooksConfigTest(unittest.TestCase):

    def test_hooks(self):
        self.assertTrue(True)

    def test_actual_code(self):
        from BioFlow.configs.internals_config import edge_type_filters
        self.assertEqual(edge_type_filters["Group"][0], "is_part_of_collection")

if __name__ == "__main__":
    unittest.main()