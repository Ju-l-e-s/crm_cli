import pytest
from decimal import Decimal
from datetime import date
from exceptions import CrmInvalidValue
from tests.conftest import make_console
from views.contract_view import ContractsView


class DummyClient:
    def __init__(self, fullname):
        self.fullname = fullname


class DummyContract:
    def __init__(self, id, client_fullname, total_amount, remaining_amount, is_signed, end_date):
        self.id = id
        self.client = DummyClient(client_fullname)
        self.total_amount = total_amount
        self.remaining_amount = remaining_amount
        self.is_signed = is_signed
        self.end_date = end_date


def test_show_menu_commercial(monkeypatch):
    fake_console = make_console()
    # Simulate choosing “List unsigned contracts”
    monkeypatch.setattr(
        'views.contract_view.display_menu',
        lambda title, opts: opts.index('List unsigned contracts') + 1
    )
    view = ContractsView(user=None, console=fake_console)
    assert view.show_menu('commercial') == 'List unsigned contracts'


def test_show_menu_gestion(monkeypatch):
    fake_console = make_console()
    # Simulate choosing “Add contract”
    monkeypatch.setattr(
        'views.contract_view.display_menu',
        lambda title, opts: opts.index('Add contract') + 1
    )
    view = ContractsView(user=None, console=fake_console)
    assert view.show_menu('gestion') == 'Add contract'


def test_display_contract_table_with_data(monkeypatch):
    fake_console = make_console()
    contracts = [
        DummyContract(1, 'Alice', Decimal('100'), Decimal('50'), True,  date(2025, 1,  1)),
        DummyContract(2, 'Bob',   Decimal('200'), Decimal('150'), False, date(2025, 6, 30)),
    ]
    printed = {}
    fake_console.print = lambda tbl: printed.setdefault('table', tbl)
    view = ContractsView(user=None, console=fake_console)

    view.display_contract_table(contracts, title="My Contracts")
    tbl = printed['table']
    assert getattr(tbl, 'title', None) == 'My Contracts'
    assert tbl.row_count == 2


def test_display_contract_table_empty(monkeypatch):
    fake_console = make_console()
    called = {}
    # intercept display_info
    monkeypatch.setattr(
        'views.contract_view.display_info',
        lambda msg, clear=False: called.setdefault('info', (msg, clear))
    )
    view = ContractsView(user=None, console=fake_console)

    view.display_contract_table([], title="Whatever")
    assert called['info'] == ("No contracts found.", False)


def test_prompt_new_contract_success(monkeypatch):
    fake_console = make_console()
    fake_console.input.side_effect = ['12', '123.45', 'y', '2025-12-31']
    view = ContractsView(user=None, console=fake_console)

    data = view.prompt_new_contract()
    assert data == {
        'client_id': 12,
        'amount':    Decimal('123.45'),
        'is_signed': True,
        'end_date':  '2025-12-31',
    }


def test_prompt_new_contract_invalid_client(monkeypatch):
    fake_console = make_console()
    fake_console.input.return_value = 'abc'
    view = ContractsView(user=None, console=fake_console)
    with pytest.raises(CrmInvalidValue, match="Client ID must be a positive integer."):
        view.prompt_new_contract()


def test_prompt_new_contract_invalid_amount(monkeypatch):
    fake_console = make_console()
    fake_console.input.side_effect = ['12', 'not-a-number', 'y', '2025-12-31']
    view = ContractsView(user=None, console=fake_console)
    with pytest.raises(CrmInvalidValue, match="Total amount must be a number."):
        view.prompt_new_contract()


def test_prompt_contract_id_valid(monkeypatch):
    fake_console = make_console()
    fake_console.input.return_value = '7'
    view = ContractsView(user=None, console=fake_console)
    assert view.prompt_contract_id() == 7


def test_prompt_contract_id_invalid(monkeypatch):
    fake_console = make_console()
    fake_console.input.return_value = 'xyz'
    view = ContractsView(user=None, console=fake_console)
    with pytest.raises(CrmInvalidValue, match="Invalid ID"):
        view.prompt_contract_id()


def test_prompt_edit_contract(monkeypatch):
    fake_console = make_console()
    fake_console.input.side_effect = ['', '300', 'y', '2026-01-01']
    dummy = DummyContract(1, 'C', Decimal('100'), Decimal('50'), False, date(2025, 1, 1))
    view = ContractsView(user=None, console=fake_console)

    result = view.prompt_edit_contract(dummy)
    assert result == {
        'amount':    None,
        'remaining': Decimal('300'),
        'is_signed': True,
        'end_date':  '2026-01-01',
    }


def test_show_messages(monkeypatch):
    fake_console = make_console()
    view = ContractsView(user=None, console=fake_console)
    called = {}
    # intercept display_success / display_error
    monkeypatch.setattr(
        'views.contract_view.display_success',
        lambda msg: called.setdefault('ok', msg)
    )
    monkeypatch.setattr(
        'views.contract_view.display_error',
        lambda msg: called.setdefault('err', msg)
    )

    view.show_success('Yay!')
    view.show_error('Oops!')
    assert called == {'ok': 'Yay!', 'err': 'Oops!'}
