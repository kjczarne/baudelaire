import unittest
from baudelaire import _main
from pathlib import Path


class TestImageDump(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.path = Path(__file__).parent / "rage.txt"

    def test_image_dump(self):
        with open(self.path, "r") as f:
            strfile = f.read()
            _main(strfile, Path("outputs"))


if __name__ == "__main__":
    unittest.main()
