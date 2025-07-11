from unittest.mock import patch, MagicMock

from controllers.auth_controller import AuthController
from exceptions import CrmInvalidValue


def test_auth_controller_login_success(session, seeded_user):
    console = MagicMock()
    console.input.side_effect = ["tester@example.com", "Password123"]

    with patch("views.auth_view.console", console), \
            patch("controllers.auth_controller.get_credentials", return_value=("tester@example.com", "Password123")), \
            patch("controllers.auth_controller.show_login_success") as mock_success, \
            patch("controllers.auth_controller.UserController") as MockUserCtrl:

        instance = MockUserCtrl.return_value
        instance.authenticate.return_value = seeded_user

        auth_ctrl = AuthController(session)
        user = auth_ctrl.login_flow()

        assert user is seeded_user
        mock_success.assert_called_once_with(seeded_user)


def test_auth_controller_login_invalid_credentials(session):
    console = MagicMock()
    console.input.side_effect = ["wrong@example.com", "WrongPwd"]

    with patch("views.auth_view.console", console), \
            patch("controllers.auth_controller.get_credentials", return_value=("wrong@example.com", "WrongPwd")), \
            patch("controllers.auth_controller.show_login_error") as mock_error, \
            patch("controllers.auth_controller.UserController") as MockUserCtrl:

        instance = MockUserCtrl.return_value
        instance.authenticate.side_effect = CrmInvalidValue(
            "Invalid credentials")

        auth_ctrl = AuthController(session)
        user = auth_ctrl.login_flow()

        assert user is None
        mock_error.assert_called_once_with("Invalid credentials")
