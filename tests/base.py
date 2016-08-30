import unittest

from os.path import join as pjoin


class BaseTestCase(unittest.TestCase):
    def _get_fixture(self, name):
        fixture_path = pjoin(self.fixtures_dir, name)

        with open(fixture_path, 'r') as fp:
            content = fp.read().strip()

        return content
