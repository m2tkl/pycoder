from pycoder import scrape
import pytest

class TestCode:

    def test_get_tasks_url(self):
        tasks_url = scrape._get_tasks_url('abc123')
        expected = 'https://atcoder.jp/contests/abc123/tasks'
        assert tasks_url == expected

