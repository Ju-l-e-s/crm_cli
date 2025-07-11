from datetime import datetime, timedelta
from decimal import Decimal

from controllers.repositories.contract_repository import ContractRepository
from models.contract import Contract

def test_contract_repository_crud(session):
    repo = ContractRepository(session)

    now = datetime.now()
    later = now + timedelta(days=30)

    contract = Contract(
        total_amount = Decimal("100.00"),
        remaining_amount = Decimal("100.00"),
        creation_date = now,
        end_date = later,
        is_signed = False,
        client_id = 1,
        commercial_id = 2
    )

    saved = repo.save(contract)
    assert saved.id is not None

    all_contracts = repo.list_all()
    assert isinstance(all_contracts, list)
    assert saved in all_contracts

    fetched = repo.get_by_id(saved.id)
    assert fetched.id == saved.id

    assert repo.get_by_id(99999) is None
