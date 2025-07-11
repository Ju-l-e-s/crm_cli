from controllers.repositories.client_repository import ClientRepository
from models.client import Client


def test_client_repository_get_by_email(session, seeded_user_commercial):
    repo = ClientRepository(session)
    client = Client(
        fullname="Test Client",
        email="client@email.com",
        commercial_id=seeded_user_commercial.id
    )
    repo.save(client)

    result = repo.get_by_email("client@email.com")
    assert result is not None
    assert result.fullname == "Test Client"


def test_get_client_by_email_not_found(session):
    repo = ClientRepository(session)
    result = repo.get_by_email("nonexistent@email.com")
    assert result is None


def test_get_client_by_id(session, seeded_user_commercial):
    repo = ClientRepository(session)
    client = Client(
        fullname="Client",
        email="client2@email.com",
        commercial_id=seeded_user_commercial.id
    )
    saved = repo.save(client)

    result = repo.get_by_id(saved.id)
    assert result is not None
    assert result.email == "client2@email.com"


def test_get_client_by_id_not_found(session):
    repo = ClientRepository(session)
    result = repo.get_by_id(999)
    assert result is None


def test_save_client_returns_client(session, seeded_user_commercial):
    repo = ClientRepository(session)
    client = Client(
        fullname="Client Save",
        email="save@email.com",
        commercial_id=seeded_user_commercial.id
    )
    saved = repo.save(client)
    assert saved is not None
    assert saved.id is not None


def test_list_all_clients(session, seeded_user_commercial):
    repo = ClientRepository(session)
    client = Client(
        fullname="Client One",
        email="clientone@email.com",
        commercial_id=seeded_user_commercial.id
    )
    repo.save(client)
    clients = repo.list_all()
    assert len(clients) >= 1


def test_list_by_commercial(session, seeded_user_commercial):
    repo = ClientRepository(session)
    client = Client(
        fullname="Client Two",
        email="clienttwo@email.com",
        commercial_id=seeded_user_commercial.id
    )
    repo.save(client)
    clients = repo.list_by_commercial(seeded_user_commercial.id)
    assert len(clients) >= 1
    assert all(c.commercial_id == seeded_user_commercial.id for c in clients)
    

def test_delete_client(session, seeded_user_commercial):
    repo = ClientRepository(session)
    client = Client(
        fullname="Client Delete",
        email="delete@email.com",
        commercial_id=seeded_user_commercial.id
    )
    saved = repo.save(client)
    repo.delete(saved)
    result = repo.get_by_id(saved.id)
    assert result is None

def test_delete_client_not_found(session, seeded_user_commercial):
    repo = ClientRepository(session)
    client = Client(
        fullname="Client Delete",
        email="delete@email.com",
        commercial_id=seeded_user_commercial.id
    )
    saved = repo.save(client)
    repo.delete(saved)
    result = repo.get_by_id(saved.id)
    assert result is None
    

def test_get_client_by_phone(session, seeded_user_commercial):
    repo = ClientRepository(session)
    client = Client(
        fullname="Client Phone",
        email="phone@email.com",
        phone="1234567890",
        commercial_id=seeded_user_commercial.id
    )
    saved = repo.save(client)
    result = repo.get_by_phone(saved.phone)
    assert result is not None
    assert result.phone == "1234567890"
    
def test_get_client_by_phone_not_found(session, seeded_user_commercial):
    repo = ClientRepository(session)
    result = repo.get_by_phone("1234567890")
    assert result is None
