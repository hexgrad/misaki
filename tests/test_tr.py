import importlib.util
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "misaki" / "tr.py"

spec = importlib.util.spec_from_file_location(
    "misaki_tr",
    MODULE_PATH,
)

tr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tr)

normalize_text_tr = tr.normalize_text_tr
_int_to_tr = tr._int_to_tr


class TestTurkishNumbers(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(
            _int_to_tr(0),
            "sıfır",
        )

    def test_teens(self):
        self.assertEqual(
            _int_to_tr(13),
            "on üç",
        )

    def test_tens(self):
        self.assertEqual(
            _int_to_tr(42),
            "kırk iki",
        )

    def test_hundred(self):
        self.assertEqual(
            _int_to_tr(100),
            "yüz",
        )

    def test_hundreds(self):
        self.assertEqual(
            _int_to_tr(235),
            "iki yüz otuz beş",
        )

    def test_one_thousand(self):
        self.assertEqual(
            _int_to_tr(1000),
            "bin",
        )

    def test_year(self):
        self.assertEqual(
            _int_to_tr(2026),
            "iki bin yirmi altı",
        )

    def test_large_number(self):
        self.assertEqual(
            _int_to_tr(1_250_000),
            "bir milyon iki yüz elli bin",
        )


class TestTurkishNormalization(unittest.TestCase):
    def test_plain_number(self):
        self.assertEqual(
            normalize_text_tr(
                "42 kişi geldi."
            ),
            "kırk iki kişi geldi.",
        )

    def test_date(self):
        self.assertEqual(
            normalize_text_tr(
                "Bugün 13.08.2026."
            ),
            "Bugün on üç Ağustos iki bin yirmi altı.",
        )

    def test_time(self):
        self.assertEqual(
            normalize_text_tr(
                "Toplantı 14:30'da."
            ),
            "Toplantı on dört otuz'da.",
        )

    def test_percent(self):
        self.assertEqual(
            normalize_text_tr(
                "Verim %35 oldu."
            ),
            "Verim yüzde otuz beş oldu.",
        )

    def test_decimal(self):
        self.assertEqual(
            normalize_text_tr(
                "Basınç 3,5 bar."
            ),
            "Basınç üç virgül beş bar.",
        )

    def test_temperature(self):
        self.assertEqual(
            normalize_text_tr(
                "Sıcaklık 24°C."
            ),
            "Sıcaklık yirmi dört derece santigrat.",
        )

    def test_kw(self):
        self.assertEqual(
            normalize_text_tr(
                "35 kW kapasite."
            ),
            "otuz beş kilovat kapasite.",
        )

    def test_kw_suffix(self):
        self.assertEqual(
            normalize_text_tr(
                "35 kW'lık sistem."
            ),
            "otuz beş kilovatlık sistem.",
        )

    def test_turkish_lira(self):
        self.assertEqual(
            normalize_text_tr(
                "Fiyat ₺1.250,50."
            ),
            "Fiyat bin iki yüz elli Türk lirası elli kuruş.",
        )

    def test_abbreviation(self):
        self.assertEqual(
            normalize_text_tr(
                "Dr. Ahmet geldi."
            ),
            "Doktor Ahmet geldi.",
        )

    def test_engineering_sentence(self):
        self.assertEqual(
            normalize_text_tr(
                "Pompa 35 kW ve basınç 8,2 bar."
            ),
            "Pompa otuz beş kilovat ve basınç sekiz virgül iki bar.",
        )


if __name__ == "__main__":
    unittest.main()
