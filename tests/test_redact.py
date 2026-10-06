import unittest

from generator.redact import redact


class RedactTest(unittest.TestCase):
    def test_key_token_obfuscated(self):
        self.assertEqual(redact("key=abcdef123456"), "key=***")

    def test_key_in_url_keeps_surrounding_text(self):
        self.assertEqual(redact('url = "https://api.tomtom.com/map?key=ABCdef_123-456&v=1"'),
                         'url = "https://api.tomtom.com/map?key=***&v=1"')

    def test_every_occurrence_obfuscated(self):
        self.assertEqual(redact("a key=AAAAAAAA1 b key=BBBBBBBB2"), "a key=*** b key=***")

    def test_short_values_left_alone(self):
        self.assertEqual(redact("key=abc and key=***"), "key=abc and key=***")


if __name__ == "__main__":
    unittest.main()
