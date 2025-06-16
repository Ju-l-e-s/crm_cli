import datetime
from decimal import Decimal
from unittest.mock import MagicMock, patch


from exceptions import CrmInvalidValue, CrmNotFoundError
from tests.conftest import _make_console

# Tests for list_all & list_mine
def test_contracts_view_list_all_empty(session):
    from views.contract_view import ContractsView

    console = _make_console()
    view = ContractsView(user=MagicMock(role=MagicMock(
        value="gestion")), console=console, session=session)

    with patch("views.contract_view.ContractController.list_all_contracts", return_value=[]), \
            patch("views.contract_view.display_info") as mock_info:
        view.list_all()
        mock_info.assert_called_once_with("No contracts found.", clear=False)


def test_contracts_view_list_all_with_data(session):
    from views.contract_view import ContractsView

    contract = MagicMock()
    contract.id = 1
    contract.client_id = 2
    contract.total_amount = Decimal("100")
    contract.remaining_amount = Decimal("0")
    contract.is_signed = True
    contract.end_date = datetime.date(2025, 12, 31)

    console = _make_console()
    contract = MagicMock()
    contract.id = 1
    contract.client_id = 2
    contract.total_amount = Decimal("100")
    contract.remaining_amount = Decimal("0")
    contract.is_signed = True
    contract.end_date = datetime.date(2025, 12, 31)
    
    view = ContractsView(user=MagicMock(role=MagicMock(
        value="gestion")), console=console, session=session)

    with patch("views.contract_view.ContractController.list_all_contracts", return_value=[contract]) as mock_list, \
            patch("views.contract_view.create_table") as mock_table:
        table_instance = MagicMock()
        mock_table.return_value = table_instance
        view.list_all()
        mock_list.assert_called_once()
        table_instance.add_row.assert_called_once_with(
            str(contract.id), str(contract.client_id), f"{contract.total_amount}", f"{contract.remaining_amount}", str(
                contract.is_signed), str(contract.end_date.strftime("%Y-%m-%d"))
        )


def test_contracts_view_list_mine_empty(session):
    from views.contract_view import ContractsView

    console = _make_console()
    view = ContractsView(user=MagicMock(role=MagicMock(
        value="commercial")), console=console, session=session)
    with patch("views.contract_view.ContractController.list_by_commercial", return_value=[]), \
            patch("views.contract_view.display_info") as mock_info:
        view.list_mine()
        mock_info.assert_called_once_with(
            "You don't have any contracts.", clear=False)


def test_contracts_view_add_success(session):
    from views.contract_view import ContractsView

    console = _make_console()
    console.input.side_effect = ["2", "150", "n", "2026-01-01"]
    view = ContractsView(user=MagicMock(role=MagicMock(
        value="gestion")), console=console, session=session)

    mock_contract = MagicMock(id=99)
    with patch("views.contract_view.ContractController.create_contract", return_value=mock_contract) as mock_create, \
            patch("views.contract_view.display_success") as mock_success:
        view.add_contract()
        mock_create.assert_called_once_with(
            2, Decimal("150"), False, "2026-01-01")
        mock_success.assert_called_once_with("Created contract ID 99")


def test_contracts_view_add_invalid_client_error(session):
    """If client does not exist, controller should raise CrmNotFoundError and view shows error."""
    from views.contract_view import ContractsView

    console = _make_console()
    console.input.side_effect = ["1", "100", "y", "2025-12-31"]
    view = ContractsView(user=MagicMock(role=MagicMock(
        value="gestion")), console=console, session=session)

    with patch("views.contract_view.ContractController.create_contract", side_effect=CrmNotFoundError("Client")) as mock_create, \
            patch("views.contract_view.display_error") as mock_display_error:
        view.add_contract()
        mock_create.assert_called_once()
        mock_display_error.assert_called_once()
        assert console.input.call_count == 4


def test_contracts_view_add_contract_error(session):
    """If input validation fails (CrmInvalidValue), view should show error."""
    from views.contract_view import ContractsView

    console = _make_console()
    console.input.side_effect = ["3", "100", "y", "2025-12-31"]
    view = ContractsView(user=MagicMock(role=MagicMock(
        value="gestion")), console=console, session=session)
    with patch("views.contract_view.ContractController.create_contract", side_effect=CrmInvalidValue("bad")) as mock_create, \
            patch("views.contract_view.display_error") as mock_error:
        view.add_contract()
        mock_create.assert_called_once()
        mock_error.assert_called_once()

# Tests for edit_contract
def test_contracts_view_edit_contract_not_found(session):
    from views.contract_view import ContractsView

    console = _make_console()
    console.input.return_value = "5"
    view = ContractsView(user=MagicMock(role=MagicMock(
        value="gestion")), console=console, session=session)
    with patch("views.contract_view.ContractController.get_contract_by_id", side_effect=CrmNotFoundError("no")) as mock_get, \
            patch("views.contract_view.display_error") as mock_error:
        view.edit_contract()
        mock_get.assert_called_once_with(5)
        mock_error.assert_called_once()


def test_contracts_view_edit_invalid_id(session):
    from views.contract_view import ContractsView

    console = _make_console()
    console.input.return_value = "xyz"
    view = ContractsView(user=MagicMock(role=MagicMock(
        value="gestion")), console=console, session=session)
    with patch("views.contract_view.display_error") as mock_error:
        view.edit_contract()
        mock_error.assert_called_once_with("Invalid ID")
