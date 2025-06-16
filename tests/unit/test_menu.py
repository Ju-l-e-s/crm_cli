"""Tests for main menu behaviours."""

from unittest.mock import MagicMock, patch
from tests.conftest import _make_console

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

def _fake_menu_return(label_to_pick):
    """Return a fake display_menu that selects the given label."""
    def _inner(_title, choices):
        return choices.index(label_to_pick) + 1  # display_menu returns 1-based index
    return _inner


def _make_user(role="commercial"):
    user = MagicMock()
    user.fullname = "John Doe"
    user.role = MagicMock(value=role)
    return user

# -----------------------------------------------------------------------------
# Tests
# -----------------------------------------------------------------------------

def test_run_main_menu_quit(monkeypatch):
    from views import menu as menu_view

    user = _make_user("commercial")
    monkeypatch.setattr(menu_view, "console", _make_console())
    monkeypatch.setattr(menu_view, "SessionLocal", MagicMock(return_value=MagicMock(close=MagicMock())))
    monkeypatch.setattr(menu_view, "display_menu", _fake_menu_return("Quit"))

    with patch("views.menu.display_info") as mock_info:
        result = menu_view.run_main_menu(user)
        assert result == "quit"
        mock_info.assert_called_once_with("Exiting. Goodbye!")


def test_run_main_menu_logout(monkeypatch):
    from views import menu as menu_view

    user = _make_user("gestion")
    monkeypatch.setattr(menu_view, "console", _make_console())
    monkeypatch.setattr(menu_view, "SessionLocal", MagicMock(return_value=MagicMock(close=MagicMock())))
    monkeypatch.setattr(menu_view, "display_menu", _fake_menu_return("Log out"))

    with patch("views.menu.logout", return_value=None) as mock_logout:
        result = menu_view.run_main_menu(user)
        assert result == "logout"
        mock_logout.assert_called_once()
