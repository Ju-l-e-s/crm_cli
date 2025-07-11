import pytest
from types import SimpleNamespace

from exceptions import CrmInvalidValue
from tests.conftest import make_console
import views.user_view as uv


class DummyUser:
    def __init__(self, id, fullname, email, role_value):
        self.id = id
        self.fullname = fullname
        self.email = email
        self.role = SimpleNamespace(value=role_value)


def test_show_menu_returns_correct_label(monkeypatch):
    fake_console = make_console()
    monkeypatch.setattr(uv, 'display_menu', lambda title,
                        opts: opts.index('Edit user') + 1)
    view = uv.UsersView(fake_console)
    assert view.show_menu() == 'Edit user'


def test_display_user_table():
    fake_console = make_console()
    users = [
        DummyUser(1, 'Homer Simpson', 'homer@springfield.com', 'gestion'),
        DummyUser(2, 'Marge Simpson', 'marge@springfield.com', 'support'),
    ]
    view = uv.UsersView(fake_console)
    view.display_user_table(users)
    assert fake_console.print.called
    table = fake_console.print.call_args[0][0]
    assert getattr(table, 'title', None) == 'All Users'
    assert table.row_count == 2


def test_prompt_new_user_success():
    fake_console = make_console()
    fake_console.input.side_effect = [
        'Bart Simpson', 'bart@springfield.com', 'commercial',
        'ElBarto123', 'ElBarto123'
    ]
    view = uv.UsersView(fake_console)
    data = view.prompt_new_user()
    assert data == {
        'fullname': 'Bart Simpson',
        'email': 'bart@springfield.com',
        'role': 'commercial',
        'password': 'ElBarto123'
    }


def test_prompt_new_user_password_mismatch():
    fake_console = make_console()
    fake_console.input.side_effect = [
        'Lisa Simpson', 'lisa@springfield.com', 'gestion',
        'pwd123', 'wrong'
    ]
    view = uv.UsersView(fake_console)
    with pytest.raises(CrmInvalidValue, match='Passwords do not match'):
        view.prompt_new_user()


def test_prompt_user_id_valid():
    fake_console = make_console()
    fake_console.input.return_value = '42'
    view = uv.UsersView(fake_console)
    assert view.prompt_user_id("User ID to delete") == 42


def test_prompt_user_id_invalid():
    fake_console = make_console()
    fake_console.input.return_value = 'notanumber'
    view = uv.UsersView(fake_console)
    with pytest.raises(CrmInvalidValue, match='Invalid ID'):
        view.prompt_user_id("User ID to delete")


def test_prompt_edit_user_keep_defaults():
    fake_console = make_console()
    fake_console.print = lambda msg: None
    fake_console.input.side_effect = ['', '', '', '']
    user = DummyUser(3, 'Milhouse Van Houten',
                     'milhouse@springfield.com', 'support')
    view = uv.UsersView(fake_console)
    result = view.prompt_edit_user(user)
    assert result == {
        'fullname': 'Milhouse Van Houten',
        'email': 'milhouse@springfield.com',
        'role': 'support',
        'password': ''
    }


def test_prompt_edit_user_with_password():
    fake_console = make_console()
    fake_console.print = lambda msg: None
    fake_console.input.side_effect = ['', '', '', 'pwd123', 'pwd123']
    user = DummyUser(4, 'Nelson Muntz', 'nelson@bully.com', 'commercial')
    view = uv.UsersView(fake_console)
    result = view.prompt_edit_user(user)
    assert result['password'] == 'pwd123'


def test_prompt_edit_user_password_mismatch():
    fake_console = make_console()
    fake_console.print = lambda msg: None
    fake_console.input.side_effect = ['', '', '', 'aaa', 'bbb']
    user = DummyUser(5, 'Ralph Wiggum', 'ralph@springfield.com', 'gestion')
    view = uv.UsersView(fake_console)
    with pytest.raises(CrmInvalidValue, match='Passwords do not match'):
        view.prompt_edit_user(user)


def test_prompt_delete_confirmation():
    fake_console = make_console()
    fake_console.input.return_value = 'y'
    view = uv.UsersView(fake_console)
    assert view.prompt_delete_confirmation(6)
    fake_console.input.return_value = 'n'
    assert not view.prompt_delete_confirmation(6)


def test_show_messages(monkeypatch):
    fake_console = make_console()
    view = uv.UsersView(fake_console)
    called = {}
    monkeypatch.setattr(uv, 'display_success',
                        lambda msg: called.setdefault('ok', msg))
    monkeypatch.setattr(uv, 'display_error',
                        lambda msg: called.setdefault('err', msg))
    monkeypatch.setattr(uv, 'display_info',
                        lambda msg: called.setdefault('info', msg))

    view.show_success('Great!')
    view.show_error('Oops!')
    view.show_info('info !')
    assert called == {'ok': 'Great!', 'err': 'Oops!', 'info': 'info !'}
