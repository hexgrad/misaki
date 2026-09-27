import importlib.util
import unittest
from pathlib import Path


def _convert_num():
    path = Path(__file__).resolve().parents[1] / "misaki" / "g2pkc" / "numerals.py"
    spec = importlib.util.spec_from_file_location("misaki_numerals", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.convert_num


convert_num = _convert_num()


class NumeralsTest(unittest.TestCase):
    def test_shorter_number_does_not_eat_a_longer_one(self):
        self.assertEqual(convert_num("3명 13명"), "세명 열세명")
        self.assertEqual(convert_num("3개/B 13개/B"), "세개/B 열세개/B")

    def test_single_numbers_stay(self):
        self.assertEqual(
            convert_num("우리 3시/B 10분/B에 만나자."),
            "우리 세시/B ^십분/B에 만나자.",
        )
        self.assertEqual(convert_num("10개"), "열개")


if __name__ == "__main__":
    unittest.main()
