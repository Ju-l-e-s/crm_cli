import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from decimal import Decimal

from controllers.contract_controller import ContractController
from models.contract import Contract
from exceptions import CrmInvalidValue

@pytest.fixture
def fake_dates():
    now = datetime.now()
    return now, now + timedelta(days=30)

def test_create_contract_success(session, seeded_user, fake_dates):
    controller = ContractController(session)
    start, end = fake_dates
    fake_contract = Contract(
        total_amount=Decimal("50.00"),
        remaining_amount=Decimal("50.00"),
        creation_date=start,
        end_date=end,
        is_signed=True
    )

    with patch('controllers.services.authorization.get_token_payload_or_raise',
               return_value={'role': 'gestion', 'id': seeded_user.id}), \
         patch('controllers.contract_controller.get_current_user',
               return_value=seeded_user), \
         patch('controllers.contract_controller.ContractRepository.save',
               return_value=fake_contract) as mock_save:

        result = controller.create_contract(
            client_id=1,
            amount=50,
            is_signed=True,
            end_date=start.strftime("%Y-%m-%d")
        )
        assert isinstance(result, Contract)
        assert result.total_amount == Decimal("50.00")
        mock_save.assert_called_once()