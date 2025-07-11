from datetime import datetime

import pytest
from unittest.mock import MagicMock, patch

from exceptions import CrmNotFoundError, CrmInvalidValue
from tests.conftest import make_console
import views.client_view as cv

class DummyClient:
    def __init__(self, id, fullname, email, phone, company):
        self.id = id
        self.fullname = fullname
        self.email = email
        self.phone = phone
        self.company = company
        self.created_at = datetime.now()
        self.updated_at = datetime.now()


def test_show_menu_commercial(monkeypatch):
    fake_console = make_console()
    monkeypatch.setattr(cv, 'display_menu', lambda title,
                        opts: opts.index('Add client') + 1)
    view = cv.ClientsView(fake_console)
    assert view.show_menu('commercial') == 'Add client'


def test_show_menu_support(monkeypatch):
    fake_console = make_console()
    monkeypatch.setattr(cv, 'display_menu', lambda title,
                        opts: opts.index('List clients') + 1)
    view = cv.ClientsView(fake_console)
    assert view.show_menu('support') == 'List clients'


def test_show_menu_gestion(monkeypatch,):
    fake_console = make_console()
    monkeypatch.setattr(cv, 'display_menu', lambda title,
                        opts: opts.index('Delete client') + 1)
    view = cv.ClientsView(fake_console)
    assert view.show_menu('gestion') == 'Delete client'


def test_display_client_table(monkeypatch):
    fake_console = make_console()
    monkeypatch.setattr(cv, 'console', fake_console)
    clients = [
        DummyClient(1, 'Homer Simpson', 'homer@sp.com',
                    '+33123456789', 'Duff'),
        DummyClient(2, 'Marge Simpson', 'marge@sp.com',
                    '+33987654321', 'Kwik-E-Mart'),
    ]
    view = cv.ClientsView(fake_console)
    view.display_client_table(clients)
    assert fake_console.print.called
    table = fake_console.print.call_args[0][0]
    assert getattr(table, 'title', None) == 'All Clients'
    assert table.row_count == 2


def test_prompt_new_client_success(monkeypatch):
    fake_console = make_console()
    monkeypatch.setattr(cv, 'console', fake_console)
    fake_console.input.side_effect = [
        'Barney Gumble', 'barney@sp.com', '+33011223344', "Moe's Tavern"
    ]
    view = cv.ClientsView(fake_console)
    data = view.prompt_new_client()
    assert data == {
        'fullname': 'Barney Gumble',
        'email': 'barney@sp.com',
        'phone': '+33011223344',
        'company': "Moe's Tavern"
    }


def test_prompt_client_id_valid_edit(monkeypatch):
    fake_console = make_console()
    monkeypatch.setattr(cv, 'console', fake_console)
    fake_console.input.return_value = '42'
    view = cv.ClientsView(fake_console)
    assert view.prompt_client_id(edit=True) == 42


def test_prompt_client_id_invalid_edit(monkeypatch):
    fake_console = make_console()
    monkeypatch.setattr(cv, 'console', fake_console)
    fake_console.input.return_value = 'abc'
    view = cv.ClientsView(fake_console)
    with pytest.raises(CrmInvalidValue, match='Invalid ID'):
        view.prompt_client_id(edit=True)


def test_prompt_client_id_valid_delete(monkeypatch):
    fake_console = make_console()
    monkeypatch.setattr(cv, 'console', fake_console)
    fake_console.input.return_value = '7'
    view = cv.ClientsView(fake_console)
    assert view.prompt_client_id(edit=False) == 7


def test_prompt_client_id_invalid_delete(monkeypatch):
    fake_console = make_console()
    monkeypatch.setattr(cv, 'console', fake_console)
    fake_console.input.return_value = 'xyz'
    view = cv.ClientsView(fake_console)
    with pytest.raises(CrmInvalidValue, match='Invalid ID'):
        view.prompt_client_id(edit=False)


def test_prompt_edit_client_keep_defaults(monkeypatch):
    fake_console = make_console()
    monkeypatch.setattr(cv, 'console', fake_console)
    fake_console.print = lambda msg: None
    fake_console.input.side_effect = ['', '', '', '']
    client = DummyClient(3, 'Milhouse Van Houten', 'milhouse@sp.com',
                         '+33111222333', 'Springfield Elementary')
    view = cv.ClientsView(fake_console)
    result = view.prompt_edit_client(client)
    assert result == {
        'fullname': 'Milhouse Van Houten',
        'email': 'milhouse@sp.com',
        'phone': '+33111222333',
        'company': 'Springfield Elementary'
    }


def test_prompt_delete_confirmation(monkeypatch):
    fake_console = make_console()
    monkeypatch.setattr(cv, 'console', fake_console)
    fake_console.input.return_value = 'y'
    view = cv.ClientsView(fake_console)
    assert view.prompt_delete_confirmation(5)
    fake_console.input.return_value = 'n'
    assert not view.prompt_delete_confirmation(5)


def test_show_messages(monkeypatch):
    fake_console = make_console()
    view = cv.ClientsView(fake_console)
    called = {}
    monkeypatch.setattr(cv, 'display_success',
                        lambda msg: called.setdefault('ok', msg))
    monkeypatch.setattr(cv, 'display_error',
                        lambda msg: called.setdefault('err', msg))
    monkeypatch.setattr(cv, 'display_info',
                        lambda msg: called.setdefault('info', msg))

    view.show_success('Done!')
    view.show_error('Oops!')
    view.show_info('info !')
    assert called == {'ok': 'Done!', 'err': 'Oops!', 'info': 'info !'}
