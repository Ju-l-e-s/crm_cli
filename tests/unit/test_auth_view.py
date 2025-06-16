from unittest.mock import patch
from exceptions import CrmInvalidValue

# Tests for loginw
def test_auth_view_login_success(session, seeded_user):
    from views import auth_view

    with patch("views.auth_view.Prompt.ask", return_value="tester@example.com"), \
         patch("views.auth_view.getpass", return_value="Password123"), \
         patch("views.auth_view.UserController.authenticate", return_value=seeded_user):
        user = auth_view.prompt_login()
        assert user is not None


def test_auth_view_login_invalid_credentials(session):
    from views import auth_view

    with patch("views.auth_view.Prompt.ask", return_value="wrong@example.com"), \
         patch("views.auth_view.getpass", return_value="WrongPwd"), \
         patch("views.auth_view.UserController.authenticate", side_effect=CrmInvalidValue("Invalid creds")), \
         patch("views.auth_view.display_error") as mock_display_error:
        user = auth_view.prompt_login()
        assert user is None
        mock_display_error.assert_called_once()

# Test logout
def test_auth_view_logout_displays_success(session):
    from views import auth_view

    with patch("views.auth_view.display_info") as mock_info, \
         patch("views.auth_view.console.clear") as mock_clear:
        auth_view.logout()
        mock_info.assert_called_once_with("\nLogout successful\n")
        mock_clear.assert_called_once()
