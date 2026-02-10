import unittest
from server.parser import parse_path, has_malformed_percent


class TestPathParsing(unittest.TestCase):

    def test_root_path(self):
        self.assertEqual(
            parse_path(bytearray(b"/")),
            "www/index.html"
        )

    def test_valid_paths(self):
        self.assertEqual(
            parse_path(bytearray(b"/foo")),
            "www/foo"
        )
        self.assertEqual(
            parse_path(bytearray(b"/foo/bar")),
            "www/foo/bar"
        )

    def test_query_is_ignored(self):
        self.assertEqual(
            parse_path(bytearray(b"/foo?x=1")),
            "www/foo"
        )

    def test_invalid_paths(self):
        invalid = [
            b"",
            b"foo",
            b"\\evil",
            b"/..",
            b"/../secret",
            b"/a/../b",
            b"/bad%",
            b"/bad%2",
            b"/bad%2G",
            b"/%2e%2e/secret",
        ]

        for target in invalid:
            with self.subTest(target=target):
                self.assertIsNone(parse_path(bytearray(target)))

    def test_percent_validation(self):
        self.assertFalse(
            has_malformed_percent(bytearray(b"/a%20b"))
        )
        self.assertTrue(
            has_malformed_percent(bytearray(b"/bad%"))
        )
