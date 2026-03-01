import unittest
from server.parser import has_host_header


class TestHeaderParsing(unittest.TestCase):

    def test_host_present(self):
        headers = b"GET / HTTP/1.1\r\nHost: localhost:8080\r\n"
        self.assertTrue(has_host_header(headers))

    def test_host_present_with_value(self):
        headers = b"GET / HTTP/1.1\r\nHost: example.com\r\n"
        self.assertTrue(has_host_header(headers))

    def test_host_missing_request_line_only(self):
        headers = b"GET / HTTP/1.1\r\n"
        self.assertFalse(has_host_header(headers))

    def test_host_missing_other_headers_only(self):
        headers = b"GET / HTTP/1.1\r\nAccept: text/html\r\nConnection: close\r\n"
        self.assertFalse(has_host_header(headers))

    def test_host_case_insensitive(self):
        for header_name in [b"Host:", b"host:", b"HOST:", b"HoSt:"]:
            with self.subTest(header_name=header_name):
                headers = b"GET / HTTP/1.1\r\n" + header_name + b" localhost\r\n"
                self.assertTrue(has_host_header(headers))

    def test_host_with_leading_whitespace(self):
        headers = b"GET / HTTP/1.1\r\n  Host: localhost\r\n"
        self.assertTrue(has_host_header(headers))

    def test_empty_header_section(self):
        headers = b"GET / HTTP/1.1\r\n\r\n"
        self.assertFalse(has_host_header(headers))

    def test_multiple_headers_host_among_them(self):
        headers = b"GET / HTTP/1.1\r\nAccept: */*\r\nHost: localhost\r\nConnection: close\r\n"
        self.assertTrue(has_host_header(headers))

    def test_similar_header_name_not_host(self):
        headers = b"GET / HTTP/1.1\r\nX-Host: something\r\n"
        self.assertFalse(has_host_header(headers))
