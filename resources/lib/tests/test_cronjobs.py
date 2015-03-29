# pylint: disable=missing-docstring,invalid-name,import-error

import unittest
from cronjobs import Job


class JobTestCase(unittest.TestCase):
    def test_conv_to_set_converts_numbers_to_set(self):
        job = Job("")
        self.assertIsInstance(job.conv_to_set(5), set)

if __name__ == '__main__':
    unittest.main()
