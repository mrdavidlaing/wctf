"""Tests for main.py"""

from main import main, my_new_func


class TestMain:
    def test_main_runs_without_error(self, capsys):
        """Test that main() executes without raising exceptions"""
        main()
        captured = capsys.readouterr()
        assert "Hello from python-interview-prep!" in captured.out

    def test_main_calls_my_new_func(self, capsys):
        """Test that main() calls my_new_func"""
        main()
        captured = capsys.readouterr()
        assert "from new func" in captured.out


class TestMyNewFunc:
    def test_my_new_func_does_thing(self):
        result = my_new_func() or "foobar"
        assert "foo" in result
