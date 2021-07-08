import pytest
from pycoder import auth
from unittest.mock import patch
import os


class TestAuth:

    @patch('builtins.input', lambda _: 'hoge')
    @patch('pycoder.auth.getpass', lambda _: 'fuga')
    def test_input_username_and_password(self):
        username, password = auth.input_username_and_password()
        assert username == 'hoge'
        assert password == 'fuga'

    def test_extract_csrf_token(self):
        test_src_path = ''.join(
            [
                os.path.dirname(__file__),
                '/source/csrf.html',
            ]
        )
        with open(test_src_path, 'r') as f:
            html = f.read()
        expected = 'test_val_csrf_token'
        actual = auth.extract_csrf_token(html)
        assert actual == expected
