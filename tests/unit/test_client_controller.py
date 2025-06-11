import pytest
from exceptions import CrmNotFoundError, CrmIntegrityError
from unittest.mock import patch, MagicMock

from controllers.client_controller import ClientController
from models.client import Client
from exceptions import CrmInvalidValue


def test_create_client_success(session, seeded_user_commercial):
    controller = ClientController(session)
    fake_client = Client(
        fullname="Martin Matin",
        email="martin@example.com",
        phone="+33612345678",
        company="ECorp"
    )

    with patch('controllers.services.authorization.get_token_payload_or_raise', return_value={'role': 'commercial', 'id': seeded_user_commercial.id}), \
         patch('controllers.services.auth.get_current_user', return_value=seeded_user_commercial), \
         patch('controllers.client_controller.ClientRepository.save', return_value=fake_client) as mock_save:
        result = controller.create_client(
            "Martin Matin",
            "martin@example.com",
            "+33 6 12 34 56 78",
            "ECorp"
        )

        assert isinstance(result, Client)
        assert result.fullname == "Martin Matin"
        assert result.email == "martin@example.com"


def test_create_client_repository_error(session, seeded_user_commercial):
    controller = ClientController(session)
    with patch('controllers.services.authorization.get_token_payload_or_raise', return_value={'role': 'commercial', 'id': seeded_user_commercial.id}), \
         patch('controllers.services.auth.get_current_user', return_value=seeded_user_commercial), \
         patch('controllers.client_controller.ClientRepository.save', side_effect=Exception('DB error')):
        with pytest.raises(CrmIntegrityError, match="Could not create client: DB error") as exc:
            controller.create_client(
                "Bob Leponge", "bob@example.com", "+1234567890", "MrKrabs"
            )


def test_list_all_clients(session):
    controller = ClientController(session)
    fake_list = [MagicMock(), MagicMock()]
    with patch('controllers.client_controller.ClientRepository.list_all', return_value=fake_list) as mock_list:
        result = controller.list_all_clients()
        assert result == fake_list


def test_list_by_commercial_success(session, seeded_user_commercial):
    controller = ClientController(session)
    fake_list = [MagicMock()]

    with patch('controllers.services.authorization.get_token_payload_or_raise', return_value={'role': 'commercial', 'id': seeded_user_commercial.id}), \
         patch('controllers.client_controller.get_current_user', return_value=seeded_user_commercial), \
         patch('controllers.client_controller.ClientRepository.list_by_commercial', return_value=fake_list) as mock_list:
        result = controller.list_by_commercial()
        assert result == fake_list


def test_get_client_by_id_success(session):
    """
    Test that get_client_by_id returns a client when found.
    """
    controller = ClientController(session)
    fake_client = MagicMock()
    with patch('controllers.client_controller.ClientRepository.get_by_id', return_value=fake_client) as mock_get:
        result = controller.get_client_by_id(42)
        assert result == fake_client


def test_get_client_by_id_not_found(session):
    """
    Test that get_client_by_id raises CrmNotFoundError when not found.
    """
    controller = ClientController(session)
    with patch('controllers.client_controller.ClientRepository.get_by_id', return_value=None):
        with pytest.raises(CrmNotFoundError, match="User not found.") as exc:
            controller.get_client_by_id(999)
    assert 'User not found.' in str(exc.value)


def test_update_client_success(session, seeded_user):
    """
    Test that update_client successfully updates a client for a gestion user.
    """
    controller = ClientController(session)
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
        result = controller.update_client(
            client_id=1,
            fullname="New Name",
            email="new@example.com",
            phone="+33 6 01 02 03 04",
            company="NewCorp"
        )

        assert isinstance(result, Client)
        assert result.fullname == "New Name"
        assert result.email == "new@example.com"


def test_update_client_not_found(session, seeded_user):
    """
    Test that update_client raises CrmNotFoundError when client not found.
    """
    controller = ClientController(session)
    with patch('controllers.services.authorization.get_token_payload_or_raise', return_value={'role': 'gestion', 'id': seeded_user.id}), \
         patch('controllers.services.auth.get_current_user', return_value=seeded_user), \
         patch('controllers.client_controller.get_client_owner_id', return_value=seeded_user.id), \
         patch('controllers.client_controller.ClientRepository.get_by_id', return_value=None):
        with pytest.raises(CrmNotFoundError, match="User not found.") as exc:
            controller.update_client(123, "N", "n@e.com", "+1", "C")
    assert 'User not found.' in str(exc.value)


def test_update_client_repository_error(session, seeded_user):
    """
    Test that update_client wraps repository exceptions into CrmIntegrityError.
    """
    controller = ClientController(session)
    client = Client(
        fullname="Old",
        email="old@e.com",
        phone="+11",
        company="Old"
    )
    with patch('controllers.services.authorization.get_token_payload_or_raise', return_value={'role': 'gestion', 'id': seeded_user.id}), \
         patch('controllers.services.auth.get_current_user', return_value=seeded_user), \
         patch('controllers.client_controller.get_client_owner_id', return_value=seeded_user.id), \
         patch('controllers.client_controller.ClientRepository.get_by_id', return_value=client), \
         patch('controllers.client_controller.ClientRepository.save', side_effect=Exception('DB fail')):
        with pytest.raises(CrmIntegrityError, match="Could not update client: DB fail") as exc:
            controller.update_client(1, "Name", "e@e.com", "+1234567", "Comp")