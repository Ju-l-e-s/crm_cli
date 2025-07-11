import pytest
from unittest.mock import MagicMock

from controllers.user_controller import UserController
from exceptions import CrmInvalidValue
from models.user import User
from models.user_role import UserRole


def test_create_valid_user(session, user_data):
    controller = UserController(session)
    user = controller.create_user(**user_data)
    assert user.id is not None
    assert user.fullname == user_data["fullname"]
    assert user.email == user_data["email"]
    assert user.role.value == user_data["role"]
    assert user.check_password(user_data["password"])


def test_create_user_duplicate_email(session):
    controller = UserController(session)
    controller.create_user(
        fullname="RandomUser One",
        email="duplicate@example.com",
        role="support",
        password="ValidPass123"
    )
    with pytest.raises(CrmInvalidValue) as excinfo:
        controller.create_user(
            fullname="RandomUser Two",
            email="duplicate@example.com",
            role="gestion",
            password="AnotherValid1"
        )
    assert "This email is already registered." in str(excinfo.value)


def test_authenticate_success(session, seeded_user):
    controller = UserController(session)
    user = controller.authenticate(seeded_user.email, "CorrectPassword123")
    assert user.email == seeded_user.email


def test_authenticate_wrong_password(session, seeded_user):
    controller = UserController(session)
    with pytest.raises(CrmInvalidValue) as excinfo:
        controller.authenticate("test@email.com", "WrongPassword123")
    assert "Wrong password" in str(excinfo.value)


def test_authenticate_user_not_found(session):
    controller = UserController(session)
    with pytest.raises(CrmInvalidValue) as excinfo:
        controller.authenticate("unknown@email.com", "AnyPass123")
    assert "User not found" in str(excinfo.value)


def test_list_all_users(session, seeded_user):
    controller = UserController(session)

    users = controller.list_all_users()

    assert isinstance(users, list)
    assert any(user.id == seeded_user.id for user in users)


def test_update_user_success(session, seeded_user):
    controller = UserController(session)

    updated = controller.update_user(
        user_id=seeded_user.id,
        fullname="Updated Name",
        email="updated@email.com",
        role="support"
    )

    assert updated.id == seeded_user.id
    assert updated.fullname == "Updated Name"
    assert updated.email == "updated@email.com"
    assert updated.role.value == "support"


def test_update_user_not_found(session):
    controller = UserController(session)

    with pytest.raises(AttributeError):
        controller.update_user(
            user_id=999,
            fullname="Any Name",
            email="email@noexist.com",
            role="gestion"
        )


@pytest.fixture
def controller(session):
    # Create controller and replace its view and repo with MagicMocks
    ctrl = UserController(session)
    ctrl.view = MagicMock()
    ctrl.repo = MagicMock()
    return ctrl


@pytest.fixture
def sample_user(session):
    # Create a real user in database for listing etc.
    user = User(fullname='Test', email='test@email.com', role=UserRole.GESTION)
    user.set_password('ValidPass123')
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# --- Test show_menu flows ---


def test_show_menu_executes_all_actions_and_handles_unknown(controller):
    # Mock view.show_menu sequence, then 'Back'
    sequence = ['List users', 'Add user',
                'Edit user', 'Delete user', 'Foo', 'Back']
    controller.view.show_menu.side_effect = sequence
    # Mock action methods
    controller.list_users = MagicMock()
    controller.add_user = MagicMock()
    controller.edit_user = MagicMock()
    controller.delete_user = MagicMock()
    # Run
    controller.show_menu()
    # Check actions called
    controller.list_users.assert_called_once()
    controller.add_user.assert_called_once()
    controller.edit_user.assert_called_once()
    controller.delete_user.assert_called_once()
    # Unknown option -> show_error
    controller.view.show_error.assert_called_once_with('Unknown option: Foo')

# --- Test list_users success/failure ---


def test_list_users_success(controller, sample_user):
    controller.list_all_users = MagicMock(return_value=[sample_user])
    controller.list_users()
    controller.view.display_user_table.assert_called_once_with([sample_user])


def test_list_users_failure(controller):
    controller.list_all_users = MagicMock(
        side_effect=CrmInvalidValue('errMSG'))
    controller.list_users()
    controller.view.show_error.assert_called_once_with('errMSG')

# --- Test add_user success, mismatch, invalid ---


def test_add_user_success(controller):
    fake_data = {'fullname': 'User test', 'email': 'email@test.com',
                 'role': 'support', 'password': 'ValidPass123'}
    ctrl_user = User(fullname='User test',
                     email='email@test.com', role=UserRole.SUPPORT)
    ctrl_user.id = 10
    controller.view.prompt_new_user = MagicMock(return_value=fake_data)
    controller.create_user = MagicMock(return_value=ctrl_user)
    controller.add_user()
    controller.view.show_success.assert_called_once_with('Created user ID 10')


def test_add_user_password_mismatch(controller):
    controller.view.prompt_new_user = MagicMock(
        side_effect=CrmInvalidValue("Passwords do not match. User creation aborted."))
    controller.add_user()
    controller.view.show_error.assert_called_once_with(
        'Passwords do not match. User creation aborted.')


def test_add_user_invalid(controller):
    fake_data = {'fullname': 'User test', 'email': 'email@test.com',
                 'role': 'support', 'password': 'ValidPass123'}
    controller.view.prompt_new_user = MagicMock(return_value=fake_data)
    controller.create_user = MagicMock(side_effect=CrmInvalidValue('foo'))
    controller.add_user()
    controller.view.show_error.assert_called_once_with('foo')

# --- Test edit_user success, mismatch, invalid ---


def test_edit_user_success(controller, sample_user):
    controller.view.prompt_user_id = MagicMock(return_value=sample_user.id)
    controller.get_user_by_id = MagicMock(return_value=sample_user)
    updates = {'fullname': 'New', 'email': 'n@e',
               'role': 'gestion', 'password': ''}
    controller.view.prompt_edit_user = MagicMock(return_value=updates)
    updated = sample_user
    updated.fullname = 'New'
    controller.update_user = MagicMock(return_value=updated)
    controller.edit_user()
    controller.view.show_success.assert_called_once_with(
        f'Updated user ID {updated.id}')


def test_edit_user_password_mismatch(controller, sample_user):
    controller.view.prompt_user_id = MagicMock(return_value=sample_user.id)
    controller.get_user_by_id = MagicMock(return_value=sample_user)
    controller.view.prompt_edit_user = MagicMock(
        side_effect=CrmInvalidValue('Bad'))
    controller.edit_user()
    controller.view.show_error.assert_called_once_with('Bad')


def test_edit_user_invalid(controller, sample_user):
    controller.view.prompt_user_id = MagicMock(return_value=sample_user.id)
    controller.get_user_by_id = MagicMock(return_value=sample_user)
    updates = {'fullname': 'x', 'email': 'x', 'role': 'x', 'password': ''}
    controller.view.prompt_edit_user = MagicMock(return_value=updates)
    controller.update_user = MagicMock(side_effect=CrmInvalidValue('error'))
    controller.edit_user()
    controller.view.show_error.assert_called_once_with('error')

# --- Test delete_user success, cancelled, invalid ---


def test_delete_user_success(controller, sample_user):
    controller.view.prompt_user_id = MagicMock(return_value=sample_user.id)
    controller.view.prompt_delete_confirmation = MagicMock(return_value=True)
    controller.get_user_by_id = MagicMock(return_value=sample_user)
    controller.delete_user_logic = MagicMock()
    controller.delete_user()
    controller.view.show_success.assert_called_once_with(
        f'User ID {sample_user.id} has been deleted.')


def test_delete_user_cancelled(controller):
    controller.view.prompt_user_id = MagicMock(return_value=1)
    controller.view.prompt_delete_confirmation = MagicMock(return_value=False)
    controller.delete_user()
    controller.view.show_info.assert_called_once_with('Operation cancelled.')


def test_delete_user_invalid(controller):
    controller.view.prompt_user_id = MagicMock(return_value=2)
    controller.view.prompt_delete_confirmation = MagicMock(return_value=True)
    controller.get_user_by_id = MagicMock(side_effect=CrmInvalidValue('nope'))
    controller.delete_user()
    controller.view.show_error.assert_called_once_with(
        'Please enter a valid user ID (number).')
