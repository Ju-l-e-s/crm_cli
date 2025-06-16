from unittest.mock import MagicMock, patch
from exceptions import CrmInvalidValue
from tests.conftest import _make_console

# Helpers
magic_user = MagicMock()
magic_user.id = 12
magic_user.fullname = "Bob"
magic_user.email = "bob@example.com"
magic_user.role = MagicMock(value="support")

def test_users_view_list_users(session):
    from views.user_view import UsersView

    console = _make_console()
    view = UsersView(user=MagicMock(role=MagicMock(value="gestion")), console=console, session=session)

    user_obj = magic_user
    with patch("views.user_view.UserController.list_all_users", return_value=[user_obj]) as mock_list, \
         patch("views.user_view.create_table") as mock_table:
        table_instance = MagicMock()
        mock_table.return_value = table_instance
        view.list_users()
        mock_list.assert_called_once()
        table_instance.add_row.assert_called_once_with(str(user_obj.id), user_obj.fullname, user_obj.email, user_obj.role.value)


def test_users_view_add_user_error(session):
    from views.user_view import UsersView

    console = _make_console()
    console.input.side_effect = ["", "bad", "role", "pwd"]

    view = UsersView(user=MagicMock(role=MagicMock(value="gestion")), console=console, session=session)
    with patch("views.user_view.UserController.create_user", side_effect=CrmInvalidValue("oops")) as mock_create, \
         patch("views.user_view.display_error") as mock_error:
        view.add_user()
        mock_create.assert_called_once()
        mock_error.assert_called_once()


def test_users_view_add_user_success(session):
    from views.user_view import UsersView

    console = _make_console()
    console.input.side_effect = ["Bob", "bob@example.com", "support", "Pwd123"]

    view = UsersView(user=MagicMock(role=MagicMock(value="gestion")), console=console, session=session)
    user_obj = magic_user
    with patch("views.user_view.UserController.create_user", return_value=user_obj) as mock_create, \
         patch("views.user_view.display_success") as mock_success:
        view.add_user()
        mock_create.assert_called_once_with("Bob", "bob@example.com", "support", "Pwd123")
        mock_success.assert_called_once_with(f"Created user ID {user_obj.id}")


def test_users_view_edit_user_invalid_id(session):
    from views.user_view import UsersView

    console = _make_console()
    console.input.return_value = "abc"

    view = UsersView(user=MagicMock(role=MagicMock(value="gestion")), console=console, session=session)
    with patch("views.user_view.display_error") as mock_error:
        view.edit_user()
        mock_error.assert_called_once_with("Invalid ID", clear=False)


def test_users_view_edit_user_success(session):
    from views.user_view import UsersView

    console = _make_console()
    console.input.side_effect = ["12", "", "", ""]  # keep defaults

    existing_user = magic_user
    view = UsersView(user=MagicMock(role=MagicMock(value="gestion")), console=console, session=session)
    with patch("views.user_view.UserController.get_user_by_id", return_value=existing_user) as mock_get, \
         patch("views.user_view.UserController.update_user", return_value=existing_user) as mock_update, \
         patch("views.user_view.display_success") as mock_success:
        view.edit_user()
        mock_get.assert_called_once_with(12)
        mock_update.assert_called_once_with(12, fullname=existing_user.fullname, email=existing_user.email, role=existing_user.role.value)
        mock_success.assert_called_once_with(f"Updated user ID {existing_user.id}")
