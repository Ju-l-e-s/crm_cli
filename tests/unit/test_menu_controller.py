from unittest.mock import MagicMock, patch

from controllers.menu_controller import MenuController
from controllers.auth_controller import AuthController


def test_menu_controller_logout(monkeypatch):
    user = MagicMock()
    user.role.value = "commercial"
    session = MagicMock()

    monkeypatch.setattr(
        "controllers.menu_controller.get_menu_options", lambda role: [("Log out", None)])
    monkeypatch.setattr(
        "controllers.menu_controller.display_menu", lambda title, choices: 1)

    with patch.object(AuthController, "logout_flow", autospec=True) as mock_logout:
        ctrl = MenuController(session)
        result = ctrl.run_main_menu(user)

        assert result == "logout"
        mock_logout.assert_called_once_with(ctrl.auth_controller)


def test_menu_controller_quit(monkeypatch):
    user = MagicMock()
    user.role.value = "commercial"
    session = MagicMock()

    monkeypatch.setattr('builtins.input', lambda _: 'y')
    monkeypatch.setattr(
        "controllers.menu_controller.get_menu_options", lambda role: [("Quit", None)])
    monkeypatch.setattr(
        "controllers.menu_controller.display_menu", lambda title, choices: 1)

    with patch("controllers.menu_controller.display_info") as mock_info:
        ctrl = MenuController(session)
        result = ctrl.run_main_menu(user)

        assert result == "quit"
        mock_info.assert_called_once_with("Exiting. Goodbye!")
