from unittest.mock import MagicMock, patch
from exceptions import CrmNotFoundError, CrmInvalidValue
from tests.conftest import _make_console



def test_clients_view_list_calls_controller(session):
    """list_clients should fetch data from the controller and print a table."""
    from views.client_view import ClientsView

    mock_controller = MagicMock()
    mock_controller.list_all_clients.return_value = []

    console = _make_console()
    view = ClientsView(user=MagicMock(role=MagicMock(value="commercial")), console=console, session=session)
    # Inject mocked controller
    view.controller = mock_controller

    view.list_clients()
    mock_controller.list_all_clients.assert_called_once()
    console.print.assert_called_once()


def test_clients_view_edit_not_found_shows_error(session):
    """edit_client should call display_error when the client id is not found."""
    from views.client_view import ClientsView

    console = _make_console()
    console.input.return_value = "999"

    view = ClientsView(user=MagicMock(role=MagicMock(value="commercial")), console=console, session=session)

    with patch("views.client_view.ClientController.get_client_by_id", side_effect=CrmNotFoundError("Client")) as mock_get, \
         patch("views.client_view.display_error") as mock_display_error:
        view.edit_client()
        mock_get.assert_called_once_with(999)
        mock_display_error.assert_called_once()


def test_clients_view_add_success(session):
    from views.client_view import ClientsView

    console = _make_console()
    console.input.side_effect = [
        "John Doe", "john@example.com", "+33612345678", "Acme Corp"
    ]

    view = ClientsView(user=MagicMock(role=MagicMock(value="commercial")), console=console, session=session)
    mock_client = MagicMock(id=42)
    with patch("views.client_view.ClientController.create_client", return_value=mock_client) as mock_create, \
         patch("views.client_view.display_success") as mock_success:
        view.add_client()
        mock_create.assert_called_once_with("John Doe", "john@example.com", "+33612345678", "Acme Corp")
        mock_success.assert_called_once_with("Created client ID 42")
        assert console.input.call_count == 4


def test_clients_view_add_invalid_input(session):
    from views.client_view import ClientsView

    console = _make_console()
    console.input.side_effect = ["", "bad", "123", "Corp"]

    view = ClientsView(user=MagicMock(role=MagicMock(value="commercial")), console=console, session=session)
    with patch("views.client_view.ClientController.create_client", side_effect=CrmInvalidValue("oops")) as mock_create, \
         patch("views.client_view.display_error") as mock_error:
        view.add_client()
        mock_create.assert_called_once()
        mock_error.assert_called_once()


def test_clients_view_edit_invalid_id(session):
    from views.client_view import ClientsView

    console = _make_console()
    console.input.return_value = "abc"

    view = ClientsView(user=MagicMock(role=MagicMock(value="gestion")), console=console, session=session)
    with patch("views.client_view.display_error") as mock_error:
        view.edit_client()
        mock_error.assert_called_once_with("Invalid ID")


def test_clients_view_list_clients(session):
    from views.client_view import ClientsView

    console = _make_console()
    view = ClientsView(user=MagicMock(role=MagicMock(value="gestion")), console=console, session=session)

    client = MagicMock()
    client.id = 1
    client.fullname = "Alice"
    client.email = "alice@example.com"
    client.phone = "+33123456789"
    client.company = "ACME"
    
    with patch("views.client_view.ClientController.list_all_clients", return_value=[client]) as mock_list, \
         patch("views.client_view.create_table") as mock_table:
        tbl = MagicMock()
        mock_table.return_value = tbl
        view.list_clients()
        mock_list.assert_called_once()
        tbl.add_row.assert_called_once_with(str(client.id), client.fullname, client.email, client.phone, client.company)
