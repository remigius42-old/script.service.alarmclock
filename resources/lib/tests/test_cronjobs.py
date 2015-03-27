import unittest
from cronjobs import Job


class JobTestCase(unittest.TestCase):
    def test_conv_to_set_converts_numbers(self):
        job = Job("")
        self.assertIsInstance(job.conv_to_set(5), set)

if __name__ == '__main__':
    unittest.main()
