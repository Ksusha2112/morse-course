import pytest

from app.morse import MORSE_TABLE, REVERSE_TABLE, decode, encode


class TestEncode:
    @pytest.mark.parametrize("text,expected", [
        ("SOS", "... --- ..."),
        ("sos", "... --- ..."),
        ("Привет", ".--. .-. .. .-- . -"),
        ("Hello world", ".... . .-.. .-.. --- / .-- --- .-. .-.. -.."),
        ("АБВ", ".- -... .--"),
        ("123", ".---- ..--- ...--"),
        ("0", "-----"),
    ])
    def test_known_values(self, text, expected):
        assert encode(text) == expected

    def test_word_separator(self):
        result = encode("a b")
        assert " / " in result

    def test_unknown_char_replaced(self):
        assert encode("x@y") == "-..- ? -.--"

    def test_digits_and_punctuation(self):
        assert encode("5") == "....."
        assert encode("?") == "..--.."

    def test_empty_string(self):
        assert encode("") == ""

    def test_only_spaces(self):
        assert encode("   ") == ""

    def test_multiple_spaces_between_words(self):
        assert encode("a   b") == encode("a b")

    def test_mixed_alphabets(self):
        result = encode("АB")
        assert result == ".- -..."


class TestDecode:
    @pytest.mark.parametrize("morse,expected", [
        ("... --- ...", "SOS"),
        # Кириллица и латиница имеют общие коды, поэтому декодер
        # возвращает латинские эквиваленты (первое вхождение в таблице).
        (".--. .-. .. .-- . -", "PRIWET"),
        ("... --- ... / ... --- ...", "SOS SOS"),
        (".-", "A"),
        ("-----", "0"),
    ])
    def test_known_values(self, morse, expected):
        assert decode(morse) == expected

    def test_slash_separates_words(self):
        assert decode(".../---/...") == "S O S"

    def test_decode_unknown_code(self):
        assert "?" in decode("........")

    def test_empty_string(self):
        assert decode("") == ""

    def test_slash_separates_words_alt(self):
        assert decode(".../---/...") == "S O S"


class TestRoundTrip:
    @pytest.mark.parametrize("text", [
        "SOS", "HELLO WORLD 123", "MORSE CODE",
    ])
    def test_encode_then_decode_latin(self, text):
        assert decode(encode(text)) == text.upper()

    @pytest.mark.parametrize("text", ["ПРИВЕТ МИР", "АЗБУКА МОРЗЕ"])
    def test_encode_then_decode_cyrillic_no_loss(self, text):
        # Коды кириллицы и латиницы частично совпадают, поэтому при
        # декодировании буквы могут заменяться латинскими эквивалентами.
        # Важно, что структура слов сохраняется и буквы не теряются.
        decoded = decode(encode(text))
        assert len(decoded.split()) == len(text.split())
        assert "?" not in decoded

    def test_tables_consistent(self):
        for code, char in REVERSE_TABLE.items():
            assert MORSE_TABLE[char] == code
