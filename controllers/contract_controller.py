from typing import List, Type
from sqlalchemy.orm import Session

from datetime import datetime
from controllers.services.auth import get_current_user
from controllers.services.authorization import requires_role, requires_ownership_or_role, get_contract_owner_id
from exceptions import CrmInvalidValue, CrmNotFoundError, CrmIntegrityError
from models.contract import Contract
from controllers.repositories.contract_repository import ContractRepository
from controllers.repositories.client_repository import ClientRepository
from controllers.validators.validators import validate_amount, validate_date
from decimal import Decimal


class ContractController:
    def __init__(self, session: Session):
        self.session = session

    @requires_role("gestion")
    def create_contract(self, client_id: int, amount: Decimal, is_signed: bool, end_date: str) -> Contract:
        """
        Creates a new contract associated with a client.

        :param client_id: ID of the client for the contract.
        :param amount: Total amount of the contract.
        :param is_signed: Signed status of the contract.
        :param end_date: End date of the contract (YYYY-MM-DD).
        :return: The created contract.
        """
        # Input validation
        total_amount = validate_amount(amount)
        end_dt = validate_date(end_date)

        # Ensure client exists
        client = ClientRepository(self.session).get_by_id(client_id)
        if not client:
            raise CrmNotFoundError("Client")


        # Build domain model
        contract = Contract(
            client_id=client_id,
            commercial_id=client.commercial_id,
            total_amount=total_amount,
            remaining_amount=total_amount,
            creation_date=datetime.now(),
            end_date=end_dt,
            is_signed=is_signed
        )
        try:
            return ContractRepository(self.session).save(contract)
        except Exception as e:
            raise CrmIntegrityError(f"Could not create contract: {e}") from e

    def list_all_contracts(self) -> List[Type[Contract]]:
        """
        Returns all contracts in the system.
        """
        return ContractRepository(self.session).list_all()

    @requires_role("commercial")
    def list_by_commercial(self) -> List[Type[Contract]]:
        """
        Lists contracts managed by the current commercial user.
        """
        user = get_current_user(self.session)
        return ContractRepository(self.session).list_by_commercial(user.id)

    def get_contract_by_id(self, contract_id: int) -> Contract:
        """
        Retrieves a contract by its ID.
        :raises CrmInvalidValue: if not found.
        """
        contract = ContractRepository(self.session).get_by_id(contract_id)
        if not contract:
            raise CrmNotFoundError("Contract")
        return contract

    @requires_ownership_or_role(get_contract_owner_id, 'gestion')
    def update_contract(self, contract_id: int, amount: Decimal = None, is_signed: bool = None, remaining: Decimal = None, end_date: str = None) -> Contract:
        """
        Updates an existing contract.

        :param contract_id: ID of the contract.
        :param amount: New total amount (optional).
        :param is_signed: New signed status (optional).
        :param remaining: New remaining amount (optional).
        :param end_date: New end date (YYYY-MM-DD, optional).
        :return: The updated contract.
        """
        repo = ContractRepository(self.session)
        contract = repo.get_by_id(contract_id)
        if not contract:
            raise CrmNotFoundError("Contract")

        # Validate and assign values
        if amount is not None:
            contract.total_amount = validate_amount(amount)
        if is_signed is not None:
            contract.is_signed = is_signed
        if remaining is not None:
            contract.remaining_amount = validate_amount(remaining)
        if end_date is not None:
            contract.end_date = validate_date(end_date)

        try:
            return repo.save(contract)
        except Exception as e:
            raise CrmIntegrityError(f"Could not update contract: {e}") from e
