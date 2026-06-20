"""Tests for misaki.de — German text normalization and G2P.

Unit tests (no espeak-ng required) test normalize_text_de() and helpers.
Integration tests (require espeak-ng) test DEG2P end-to-end.
"""

import pytest
from misaki.de import _int_to_de, _ordinal_stem_de, _year_de, normalize_text_de

# ── _int_to_de ───────────────────────────────────────────────────────────────


class TestIntToDe:
    def test_zero(self):
        assert _int_to_de(0) == "null"

    def test_one_standalone(self):
        assert _int_to_de(1) == "eins"

    def test_one_composition(self):
        assert _int_to_de(1, standalone=False) == "ein"

    def test_teens(self):
        assert _int_to_de(11) == "elf"
        assert _int_to_de(12) == "zwölf"
        assert _int_to_de(16) == "sechzehn"
        assert _int_to_de(17) == "siebzehn"

    def test_tens(self):
        assert _int_to_de(20) == "zwanzig"
        assert _int_to_de(30) == "dreißig"
        assert _int_to_de(70) == "siebzig"

    def test_compound(self):
        assert _int_to_de(21) == "einundzwanzig"
        assert _int_to_de(42) == "zweiundvierzig"
        assert _int_to_de(99) == "neunundneunzig"

    def test_hundreds(self):
        assert _int_to_de(100) == "einhundert"
        assert _int_to_de(256) == "zweihundertsechsundfünfzig"

    def test_thousands(self):
        assert _int_to_de(1000) == "eintausend"
        assert _int_to_de(1234) == "eintausendzweihundertvierunddreißig"

    def test_millions(self):
        assert _int_to_de(1_000_000) == "eine Million"
        assert _int_to_de(2_000_000) == "zwei Millionen"

    def test_billions(self):
        assert _int_to_de(1_000_000_000) == "eine Milliarde"

    def test_negative(self):
        assert _int_to_de(-5) == "minus fünf"


# ── _ordinal_stem_de ─────────────────────────────────────────────────────────


class TestOrdinalStemDe:
    def test_irregular(self):
        assert _ordinal_stem_de(1) == "erst"
        assert _ordinal_stem_de(2) == "zweit"
        assert _ordinal_stem_de(3) == "dritt"
        assert _ordinal_stem_de(7) == "siebt"
        assert _ordinal_stem_de(8) == "acht"

    def test_regular_under_20(self):
        assert _ordinal_stem_de(4) == "viert"
        assert _ordinal_stem_de(5) == "fünft"
        assert _ordinal_stem_de(19) == "neunzehnt"

    def test_regular_20_plus(self):
        assert _ordinal_stem_de(20) == "zwanzigst"
        assert _ordinal_stem_de(100) == "einhundertst"


# ── _year_de ─────────────────────────────────────────────────────────────────


class TestYearDe:
    def test_1900(self):
        assert _year_de(1900) == "neunzehnhundert"

    def test_1985(self):
        assert _year_de(1985) == "neunzehnhundertfünfundachtzig"

    def test_1100(self):
        assert "hundert" in _year_de(1100)

    def test_2024(self):
        assert _year_de(2024) == "zweitausendvierundzwanzig"

    def test_below_1100(self):
        # Falls through to cardinal
        assert _year_de(800) == "achthundert"


# ── normalize_text_de ────────────────────────────────────────────────────────


class TestNormalize:
    def test_empty(self):
        assert normalize_text_de("") == ""

    def test_plain_text(self):
        r = normalize_text_de("Guten Morgen, wie geht es Ihnen?")
        assert "Guten Morgen" in r

    def test_umlauts_preserved(self):
        r = normalize_text_de("Äpfel, Österreich, Überraschung, Größe")
        assert "Äpfel" in r
        assert "Österreich" in r
        assert "Überraschung" in r
        assert "Größe" in r


class TestQuotes:
    def test_german_quotes(self):
        r = normalize_text_de("Er sagte: \u201eGuten Morgen.\u201c")
        assert "\u201e" not in r
        assert "\u201c" not in r

    def test_guillemets(self):
        r = normalize_text_de("Das ist \u00abtoll\u00bb.")
        assert "\u00ab" not in r
        assert "\u00bb" not in r


class TestAbbreviations:
    def test_doktor(self):
        assert "Doktor" in normalize_text_de("Dr. Müller")

    def test_professor(self):
        assert "Professor" in normalize_text_de("Prof. Schmidt hält")

    def test_herr(self):
        # Hr. should expand to Herr (nominative), not Herrn
        r = normalize_text_de("Hr. Müller")
        assert "Herr" in r
        assert "Herrn" not in r

    def test_strasse_standalone(self):
        assert "Straße" in normalize_text_de("Str. des Friedens")

    def test_nummer(self):
        assert "Nummer" in normalize_text_de("Nr. 5 bitte")

    def test_zum_beispiel(self):
        assert "zum Beispiel" in normalize_text_de("z.B. morgen")

    def test_das_heisst(self):
        assert "das heißt" in normalize_text_de("d.h. später")

    def test_und_so_weiter(self):
        assert "und so weiter" in normalize_text_de("Äpfel usw.")

    def test_gmbh(self):
        assert "Gesellschaft" in normalize_text_de("Muster GmbH")

    def test_ag(self):
        assert "Aktiengesellschaft" in normalize_text_de("Siemens AG,")

    def test_month_jan(self):
        assert "Januar" in normalize_text_de("Jan. war kalt")

    def test_month_okt(self):
        assert "Oktober" in normalize_text_de("Okt. war schön")


class TestNumbers:
    def test_standalone_number(self):
        r = normalize_text_de("5 Katzen.")
        assert "fünf" in r
        assert "5" not in r

    def test_42(self):
        r = normalize_text_de("42 Leute.")
        assert "zweiundvierzig" in r
        assert "42" not in r

    def test_german_thousands(self):
        r = normalize_text_de("1.000 Menschen.")
        assert "tausend" in r
        assert "1.000" not in r

    def test_decimal_comma(self):
        r = normalize_text_de("36,9 Grad.")
        assert "Komma" in r
        assert "36,9" not in r

    def test_colon_separated_non_time_numbers(self):
        assert "eins:zwei" in normalize_text_de("Stand 1:2.")


class TestCurrency:
    def test_euro_before(self):
        r = normalize_text_de("kostet €10")
        assert "Euro" in r
        assert "€" not in r

    def test_euro_after(self):
        r = normalize_text_de("kostet 10€")
        assert "Euro" in r
        assert "€" not in r

    def test_euro_with_cents(self):
        r = normalize_text_de("€9,99 bitte")
        assert "Euro" in r
        assert "Cent" in r

    def test_euro_fraction_rounds_to_next_unit(self):
        r = normalize_text_de("€9,999 bitte")
        assert "zehn Euro" in r
        assert "Cent" not in r

    def test_dollar(self):
        r = normalize_text_de("$100 Rabatt")
        assert "Dollar" in r
        assert "$" not in r


class TestTimes:
    def test_full_hour(self):
        r = normalize_text_de("Um 14:00 Uhr.")
        assert "vierzehn Uhr" in r
        assert "14:00" not in r

    def test_with_minutes(self):
        assert "acht Uhr dreißig" in normalize_text_de("Um 8:30 Uhr.")

    def test_midnight(self):
        assert "null Uhr" in normalize_text_de("Um 0:00 Uhr.")

    def test_no_trailing_null(self):
        r = normalize_text_de("Um 15:00")
        assert "fünfzehn Uhr" in r
        assert "null" not in r

    def test_no_double_uhr(self):
        r = normalize_text_de("Um 14:30 Uhr")
        assert r.count("Uhr") == 1

    def test_uhr_word_boundary(self):
        r = normalize_text_de("Um 14:30 Uhrzeit beginnt es.")
        assert "vierzehn Uhr dreißigzeit" not in r
        assert "Uhrzeit" in r

    def test_invalid_hour_is_unchanged(self):
        assert "25:00 Uhr" in normalize_text_de("Um 25:00 Uhr.")

    def test_invalid_minute_is_unchanged(self):
        assert "23:99 Uhr" in normalize_text_de("Um 23:99 Uhr.")

    def test_invalid_time_does_not_replace_literal_placeholder_text(self):
        r = normalize_text_de("Token __MISAKI_DE_INVALID_TIME_0__ um 25:00 Uhr.")
        assert "__MISAKI_DE_INVALID_TIME_0__" in r
        assert "25:00 Uhr" in r

    def test_malformed_minutes_length_is_not_time(self):
        r = normalize_text_de("Um 14:300 Uhr.")
        assert "vierzehn Uhr dreißig" not in r
        assert "vierzehn" in r
        assert "dreihundert" in r

    def test_invalid_minutes_length_survives_unchanged(self):
        r = normalize_text_de("Um 25:000 Uhr.")
        assert "25:000" not in r
        assert "fünfundzwanzig" in r
        assert "null" in r


class TestDates:
    def test_christmas(self):
        r = normalize_text_de("Am 24.12.2024.")
        assert "Dezember" in r
        assert "24.12.2024" not in r

    def test_new_year(self):
        r = normalize_text_de("Am 1.1.2000.")
        assert "erste" in r
        assert "Januar" in r

    def test_german_unity(self):
        r = normalize_text_de("Am 3.10.1990.")
        assert "dritt" in r
        assert "Oktober" in r


class TestOrdinalsMidSentence:
    def test_ordinal_3(self):
        assert "dritte" in normalize_text_de("Am 3. Mai")

    def test_ordinal_1(self):
        assert "erste" in normalize_text_de("Am 1. Mai")

    def test_ordinal_20(self):
        assert "zwanzigste" in normalize_text_de("Am 20. August")


class TestYears:
    def test_1989_in_text(self):
        r = normalize_text_de("Im Jahr 1989.")
        assert "neunzehnhundert" in r
        assert "1989" not in r

    def test_2024_in_text(self):
        r = normalize_text_de("Im Jahr 2024.")
        assert "zweitausend" in r


class TestWhitespace:
    def test_double_spaces(self):
        assert "  " not in normalize_text_de("Hallo   Welt")

    def test_trimmed(self):
        r = normalize_text_de("  Hallo Welt  ")
        assert r == r.strip()

    def test_nbsp(self):
        assert "\u00a0" not in normalize_text_de("Hallo\u00a0Welt")


class TestComplexSentence:
    def test_mixed(self):
        t = "Dr. Müller kaufte am 3. Mai 2023 um 14:30 Uhr 3 Pakete für €29,99 bei der Muster GmbH."
        r = normalize_text_de(t)
        assert "Doktor" in r
        assert "Mai" in r
        assert "vierzehn Uhr dreißig" in r
        assert "Euro" in r
        assert "Gesellschaft" in r
        assert "€" not in r
        assert "Dr." not in r
        assert "14:30" not in r


# ── pronunciation overrides (no espeak-ng required) ──────────────────────────

from misaki.de import normalize_for_lookup, override_for


class TestNormalizeForLookup:
    def test_collapses_spaces(self):
        assert normalize_for_lookup("Louis Vuitton") == "louisvuitton"

    def test_casefolds(self):
        assert normalize_for_lookup("GitHub") == "github"

    def test_plus_sign_becomes_plus(self):
        assert normalize_for_lookup("Disney+") == "disneyplus"

    def test_ampersand_becomes_and(self):
        assert normalize_for_lookup("Moët & Chandon") == "moetandchandon"

    def test_at_becomes_at(self):
        assert normalize_for_lookup("user@host") == "userathost"

    def test_strips_accents(self):
        assert normalize_for_lookup("Moët") == "moet"

    def test_drops_punctuation(self):
        assert normalize_for_lookup("zero-shot") == "zeroshot"


class TestOverrideFor:
    def test_brand(self):
        assert override_for("CUDA") == "kˈuːda"

    def test_brand_case_insensitive(self):
        assert override_for("cuda") == override_for("CUDA")

    def test_en(self):
        assert override_for("GitHub") == "ɡˈɪthab"

    def test_de_foreign(self):
        assert override_for("Synthese") == "zyntˈeːzə"

    def test_joiner_token_matches_collapsed_key(self):
        # "Disney+" must resolve to the same entry as "disneyplus".
        assert override_for("Disney+") == override_for("disneyplus")
        assert override_for("Disney+") is not None

    def test_hyphen_token_matches(self):
        assert override_for("espeak-ng") is not None
        assert override_for("zero-shot") is not None

    def test_alias(self):
        # "Moët & Chandon" -> moetandchandon -> alias -> moetchandon
        assert override_for("Moët & Chandon") == override_for("moetchandon")

    def test_unknown_returns_none(self):
        assert override_for("Spaziergang") is None

    def test_priority_brand_over_en(self):
        # No key currently collides across sections, but the loader must keep
        # brand > en > de_foreign. Spot-check that a brand key resolves.
        assert override_for("kokoro") == "kˈoːkoːʁoː"


# ── integration tests (require espeak-ng) ────────────────────────────────────

try:
    from misaki.espeak import EspeakG2P

    ESPEAK_AVAILABLE = True
except (ImportError, OSError):
    ESPEAK_AVAILABLE = False


@pytest.mark.skipif(
    not ESPEAK_AVAILABLE, reason="espeak-ng or phonemizer not available"
)
class TestDEG2PIntegration:
    @pytest.fixture(autouse=True)
    def setup(self):
        from misaki.de import DEG2P

        self.g2p = DEG2P()

    def test_simple(self):
        ps, tokens = self.g2p("Hallo Welt")
        assert isinstance(ps, str)
        assert len(ps) > 0
        assert tokens is None

    def test_normalized_numbers(self):
        ps, _ = self.g2p("Es gibt 42 Katzen.")
        assert isinstance(ps, str)
        assert len(ps) > 0

    def test_normalized_date(self):
        ps, _ = self.g2p("Am 24.12.2024 ist Weihnachten.")
        assert isinstance(ps, str)
        assert len(ps) > 0

    def test_normalized_currency(self):
        ps, _ = self.g2p("Das kostet €9,99.")
        assert isinstance(ps, str)
        assert len(ps) > 0

    def test_no_override_path_matches_plain_espeak(self):
        # Text without any override word must be identical to running espeak on
        # the normalized text (no regression from the routing layer).
        text = "Guten Morgen, wie geht es Ihnen?"
        via_g2p, tok = self.g2p(text)
        direct, _ = self.g2p.espeak(normalize_text_de(text))
        assert via_g2p == direct
        assert tok is None

    def test_override_word_phonemes_are_injected(self):
        ps, _ = self.g2p("Ich nutze GitHub.")
        assert override_for("GitHub") in ps

    def test_override_in_sentence_keeps_context(self):
        ps, _ = self.g2p("Wir testen CUDA und PyTorch heute.")
        assert override_for("CUDA") in ps
        assert override_for("PyTorch") in ps

    def test_joiner_override_in_sentence(self):
        ps, _ = self.g2p("Läuft auf Disney+ heute.")
        assert override_for("Disney+") in ps

    def test_trailing_punctuation_stays_tight(self):
        # No space should be introduced before sentence-final punctuation.
        ps, _ = self.g2p("Hallo, GitHub!")
        assert ps.endswith("!")
        assert " !" not in ps
