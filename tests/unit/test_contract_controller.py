import pytest
from decimal import Decimal
from datetime import datetime, date
from unittest.mock import patch, MagicMock

from exceptions import CrmInvalidValue, CrmNotFoundError, CrmIntegrityError
from controllers.contract_controller import ContractController
from controllers.repositories.contract_repository import ContractRepository
from controllers.repositories.client_repository import ClientRepository
from models.contract import Contract
from models.client import Client
from tests.conftest import make_console


@pytest.fixture
def mock_auth_commercial(seeded_user_commercial):
    """Mock auth for commercial role."""
    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'commercial', 'id': seeded_user_commercial.id}):
        yield


@pytest.fixture
def mock_auth_gestion(seeded_user):
    """Mock auth for gestion role."""
    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'gestion', 'id': seeded_user.id}):
        yield


def test_create_contract_success(session, seeded_user, mock_auth_gestion):
    ctrl = ContractController(session, seeded_user, make_console())
    fake_client = Client(
        fullname="Foo", email="foo@example.com", phone="+123", company="Co", commercial_id=seeded_user.id
    )
    fake_contract = Contract(
        client_id=fake_client.id,
        commercial_id=seeded_user.id,
        total_amount=Decimal('100'),
        remaining_amount=Decimal('100'),
        creation_date=datetime.now(),
        end_date=date.today(),
        is_signed=False,
    )
    with patch.object(ClientRepository, 'get_by_id', return_value=fake_client), \
            patch.object(ContractRepository, 'save', return_value=fake_contract):
        result = ctrl._create_contract(
            client_id=fake_client.id,
            amount=Decimal('100'),
            is_signed=False,
            end_date=date.today().strftime("%Y-%m-%d")
        )
    assert isinstance(result, Contract)
    assert result.client_id == fake_client.id
    assert result.commercial_id == seeded_user.id


def test_create_contract_not_found_client(session, seeded_user, mock_auth_gestion):
    ctrl = ContractController(session, seeded_user, make_console())
    with patch.object(ClientRepository, 'get_by_id', return_value=None):
        with pytest.raises(CrmNotFoundError, match="Client"):
            ctrl._create_contract(
                client_id=999,
                amount=Decimal('50'),
                is_signed=True,
                end_date="2025-01-01"
            )


def test_create_contract_validation_error(session, seeded_user, mock_auth_gestion):
    ctrl = ContractController(session, seeded_user, make_console())
    # invalid amount
    with pytest.raises(CrmInvalidValue):
        ctrl._create_contract(
            client_id=1,
            amount=Decimal('-5'),
            is_signed=True,
            end_date="2025-01-01"
        )
    # invalid date
    fake_client = MagicMock(commercial_id=1)
    with patch.object(ClientRepository, 'get_by_id', return_value=fake_client):
        with pytest.raises(CrmInvalidValue):
            ctrl._create_contract(
                client_id=1,
                amount=Decimal('10'),
                is_signed=True,
                end_date="invalid-date"
            )


def test_get_contract_by_id_success(session, seeded_user, mock_auth_gestion):
    ctrl = ContractController(session, seeded_user, make_console())
    fake_contract = MagicMock()
    with patch.object(ContractRepository, 'get_by_id', return_value=fake_contract):
        result = ctrl.get_contract_by_id(42)
    assert result is fake_contract


def test_get_contract_by_id_not_found(session, seeded_user, mock_auth_gestion):
    ctrl = ContractController(session, seeded_user, make_console())
    with patch.object(ContractRepository, 'get_by_id', return_value=None):
        with pytest.raises(CrmNotFoundError, match="Contract"):
            ctrl.get_contract_by_id(99)


def test_update_contract_success(session, seeded_user, mock_auth_gestion):
    ctrl = ContractController(session, seeded_user, make_console())
    existing = Contract(
        client_id=1,
        commercial_id=seeded_user.id,
        total_amount=Decimal('100'),
        remaining_amount=Decimal('100'),
        creation_date=datetime.now(),
        end_date=date.today(),
        is_signed=False,
    )
    updated = Contract(
        client_id=1,
        commercial_id=seeded_user.id,
        total_amount=Decimal('200'),
        remaining_amount=Decimal('150'),
        creation_date=existing.creation_date,
        end_date=date.today(),
        is_signed=True,
    )
    with patch.object(ContractRepository, 'get_by_id', return_value=existing), \
            patch.object(ContractRepository, 'save', return_value=updated):
        result = ctrl._update_contract(
            contract_id=1,
            amount=Decimal('200'),
            remaining=Decimal('150'),
            is_signed=True,
            end_date=date.today().strftime("%Y-%m-%d")
        )
    assert isinstance(result, Contract)
    assert result.total_amount == Decimal('200')
    assert result.remaining_amount == Decimal('150')
    assert result.is_signed is True


def test_update_contract_not_found(session, seeded_user, mock_auth_gestion):
    ctrl = ContractController(session, seeded_user, make_console())
    with patch.object(ContractRepository, 'get_by_id', return_value=None):
        with pytest.raises(CrmNotFoundError, match="Contract"):
            ctrl._update_contract(
                contract_id=123,
                amount=Decimal('10'),
                is_signed=None,
                remaining=None,
                end_date=None
            )


def test_update_contract_repository_error(session, seeded_user, mock_auth_gestion):
    ctrl = ContractController(session, seeded_user, make_console())
    existing = Contract(
        client_id=1,
        commercial_id=seeded_user.id,
        total_amount=Decimal('100'),
        remaining_amount=Decimal('100'),
        creation_date=datetime.now(),
        end_date=date.today(),
        is_signed=False,
    )
    with patch.object(ContractRepository, 'get_by_id', return_value=existing), \
            patch.object(ContractRepository, 'save', side_effect=Exception("Save fail")):
        with pytest.raises(CrmIntegrityError, match="Could not update contract: Save fail"):
            ctrl._update_contract(
                contract_id=1,
                amount=Decimal('50'),
                is_signed=None,
                remaining=None,
                end_date=None
            )


def test_list_all_contracts_success(session, seeded_user_commercial):
    ctrl = ContractController(session, seeded_user_commercial, make_console())
    fake_list = [MagicMock(), MagicMock()]
    ctrl.repo.list_all = MagicMock(return_value=fake_list)
    ctrl.view.display_contract_table = MagicMock()
    ctrl.list_all_contracts()
    ctrl.view.display_contract_table.assert_called_once_with(
        fake_list, title="All Contracts")


def test_list_by_commercial_success(session, seeded_user_commercial, mock_auth_commercial):
    ctrl = ContractController(session, seeded_user_commercial, make_console())
    fake_list = [MagicMock()]
    ctrl.repo.list_by_commercial = MagicMock(return_value=fake_list)
    ctrl.view.display_contract_table = MagicMock()
    ctrl.list_by_commercial()
    ctrl.view.display_contract_table.assert_called_once_with(
        fake_list, title="My Contracts")


def test_list_unsigned_contracts(session, seeded_user_commercial, mock_auth_commercial):
    # given a mix of signed and unsigned contracts
    c1 = MagicMock(is_signed=False, remaining_amount=0)
    c2 = MagicMock(is_signed=True,  remaining_amount=10)
    c3 = MagicMock(is_signed=False, remaining_amount=5)

    ctrl = ContractController(session, seeded_user_commercial, make_console())
    # Mock out the repo call and the view
    ctrl.repo.list_all = MagicMock(return_value=[c1, c2, c3])
    ctrl.view.display_contract_table = MagicMock()

    # when
    ctrl.list_unsigned_contracts()

    # then only the unsigned ones get shown, with the right title
    ctrl.view.display_contract_table.assert_called_once_with(
        [c1, c3],
        title="Unsigned Contracts"
    )


def test_list_unpaid_contracts(session, seeded_user_commercial, mock_auth_commercial):
    # given a mix of fully-paid and partly-paid contracts
    c1 = MagicMock(is_signed=True,  remaining_amount=0)
    c2 = MagicMock(is_signed=True,  remaining_amount=20)
    c3 = MagicMock(is_signed=False, remaining_amount=5)

    ctrl = ContractController(session, seeded_user_commercial, make_console())
    # Mock out the repo call and the view
    ctrl.repo.list_all = MagicMock(return_value=[c1, c2, c3])
    ctrl.view.display_contract_table = MagicMock()

    # when
    ctrl.list_unpaid_contracts()

    # then only those with remaining_amount > 0 get shown, with the right title
    ctrl.view.display_contract_table.assert_called_once_with(
        [c2, c3],
        title="Unpaid Contracts"
    )
