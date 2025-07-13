import pytest
from exceptions import CrmNotFoundError, CrmInvalidValue
from unittest.mock import patch, MagicMock

from controllers.client_controller import ClientController
from models.client import Client
from tests.conftest import make_console


@pytest.fixture
def mock_auth(seeded_user_commercial):
    with patch('controllers.services.auth.get_current_user', return_value=seeded_user_commercial), \
        patch('controllers.services.auth.load_token', return_value="mocked_token"), \
        patch('controllers.services.auth.decode_token', return_value={
            'id': seeded_user_commercial.id,
            'role': 'commercial',
            'exp': 9999999999
        }), \
        patch('controllers.services.authorization.get_token_payload_or_raise',
              return_value={'role': 'commercial', 'id': seeded_user_commercial.id}):
        yield


def test_create_client_success(session, mock_auth, seeded_user_commercial):
    controller = ClientController(
        session, seeded_user_commercial, make_console())
    fake_client = Client(
        fullname="Martin Matin",
        email="martin@example.com",
        phone="+33612345678",
        company="ECorp",
        commercial_id=seeded_user_commercial.id
    )

    with patch('controllers.client_controller.ClientRepository.save', return_value=fake_client):
        result = controller._create_client(
            "Martin Matin",
            "martin@example.com",
            "+33 6 12 34 56 78",
            "ECorp"
        )

        assert isinstance(result, Client)
        assert result.fullname == "Martin Matin"
        assert result.email == "martin@example.com"
        assert result.commercial_id == seeded_user_commercial.id


def test_create_client_invalid_value_error(session, mock_auth, seeded_user_commercial):
    existing_client = Client(
        fullname="Existing Client",
        email="existing@example.com",
        phone="+33612345678",
        company="Existing Corp",
        commercial_id=seeded_user_commercial.id
    )
    session.add(existing_client)
    session.commit()

    controller = ClientController(
        session, seeded_user_commercial, make_console())

    with pytest.raises(CrmInvalidValue, match="Email already exists."):
        controller._create_client(
            "Bob Leponge", existing_client.email, "+1234567890", "MrKrabs"
        )

    with pytest.raises(CrmInvalidValue, match="Phone already exists."):
        controller._create_client(
            "Bob Leponge", "new@example.com", existing_client.phone, "MrKrabs"
        )


def test_list_all_clients(session, seeded_user_commercial):
    """Test that doesn't require authentication"""
    controller = ClientController(
        session, seeded_user_commercial, make_console())
    fake_list = [MagicMock(), MagicMock()]
    with patch('controllers.client_controller.ClientRepository.list_all', return_value=fake_list):
        result = controller.list_all_clients()
        assert result == fake_list


def test_list_by_commercial_success(session, mock_auth, seeded_user_commercial):
    """Test that requires authentication"""
    controller = ClientController(
        session, seeded_user_commercial, make_console())
    fake_list = [MagicMock()]
    with patch('controllers.client_controller.ClientRepository.list_by_commercial', return_value=fake_list) as mock_list:
        result = controller.list_by_commercial()
        assert result == fake_list
        mock_list.assert_called_once_with(seeded_user_commercial.id)


def test_get_client_by_id_success(session, mock_auth, seeded_user_commercial):
    """
    Test that get_client_by_id returns a client when found.
    """
    controller = ClientController(
        session, seeded_user_commercial, make_console())
    fake_client = MagicMock()
    with patch('controllers.client_controller.ClientRepository.get_by_id', return_value=fake_client) as mock_get:
        result = controller.get_client_by_id(42)
        assert result == fake_client


def test_get_client_by_id_not_found(session, mock_auth, seeded_user_commercial):
    """
    Test that get_client_by_id raises CrmNotFoundError when not found.
    """
    controller = ClientController(
        session, seeded_user_commercial, make_console())
    with patch('controllers.client_controller.ClientRepository.get_by_id', return_value=None):
        with pytest.raises(CrmNotFoundError, match="Client") as exc:
            controller.get_client_by_id(999)
    assert 'Client not found.' in str(exc.value)


def test_update_client_success(session, mock_auth, seeded_user):
    """
    Test that update_client successfully updates a client for a gestion user.
    """
    controller = ClientController(session, seeded_user, make_console())
    existing = Client(
        fullname="Old Name",
        email="old@example.com",
        phone="+1111111111",
        company="OldCorp"
    )
    updated = Client(
        fullname="New Name",
        email="new@example.com",
        phone="+1222222222",
        company="NewCorp"
    )

    with patch('controllers.services.authorization.get_token_payload_or_raise', return_value={'role': 'gestion', 'id': seeded_user.id}), \
            patch('controllers.services.auth.get_current_user', return_value=seeded_user), \
            patch('controllers.client_controller.get_client_owner_id', return_value=seeded_user.id), \
            patch('controllers.client_controller.ClientRepository.get_by_id', return_value=existing), \
            patch('controllers.client_controller.ClientRepository.save', return_value=updated) as mock_save:
        result = controller._update_client(
            client_id=1,
            fullname="New Name",
            email="new@example.com",
            phone="+33 6 01 02 03 04",
            company="NewCorp"
        )

        assert isinstance(result, Client)
        assert result.fullname == "New Name"
        assert result.email == "new@example.com"


def test_update_client_not_found(session, mock_auth, seeded_user):
    """
    Test that update_client raises CrmNotFoundError when client not found.
    """
    controller = ClientController(session, seeded_user, make_console())
    with patch('controllers.services.authorization.get_token_payload_or_raise', return_value={'role': 'gestion', 'id': seeded_user.id}), \
            patch('controllers.services.auth.get_current_user', return_value=seeded_user), \
            patch('controllers.client_controller.get_client_owner_id', return_value=seeded_user.id), \
            patch('controllers.client_controller.ClientRepository.get_by_id', return_value=None):
        with pytest.raises(CrmNotFoundError, match="Client not found.") as exc:
            controller._update_client(123, "N", "n@e.com", "+1", "C")
    assert 'Client not found.' in str(exc.value)
