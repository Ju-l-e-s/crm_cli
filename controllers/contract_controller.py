from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from config.sentry_logging import capture_event
from controllers.repositories.client_repository import ClientRepository
from controllers.repositories.contract_repository import ContractRepository
from controllers.services.authorization import (
    get_contract_owner_id,
    requires_ownership_or_role,
    requires_role,
)
from controllers.validators.validators import validate_amount, validate_date
from exceptions import CrmInvalidValue, CrmIntegrityError, CrmNotFoundError, CrmForbiddenAccessError
from models.contract import Contract
import views.contract_view as contract_view


class ContractController:
    """
    Controller for contract management flows: list, add, edit.
    """

    def __init__(self, session: Session, current_user: Any, console: Any) -> None:
        """
        Initialize the ContractController.

        Args:
            session (Session): Database session.
            current_user: The currently authenticated user.
            console: Console interface for I/O operations.
        """
        self.session = session
        self.current_user = current_user
        self.console = console
        self.repo = ContractRepository(session)
        self.client_repo = ClientRepository(session)
        self.view = contract_view.ContractsView(current_user, console)

    def show_menu(self) -> None:
        """
        Display the contracts menu and loop until 'Back' is chosen.
        """
        while True:
            choice = self.view.show_menu(self.current_user.role.value)
            if choice == "List all contracts":
                self.console.clear()
                self.list_all_contracts()
            elif choice == "List my contracts":
                self.console.clear()
                self.list_by_commercial()
            elif choice == "List unsigned contracts":
                self.console.clear()
                self.list_unsigned_contracts()
            elif choice == "List unpaid contracts":
                self.console.clear()
                self.list_unpaid_contracts()
            elif choice == "Add contract":
                self.console.clear()
                self.add_contract()
            elif choice == "Edit contract":
                self.console.clear()
                self.edit_contract()
            elif choice == "Back":
                break

    def list_all_contracts(self) -> None:
        """
        List all contracts (all roles).
        """
        ctrs = self.repo.list_all()
        self.view.display_contract_table(ctrs, title="All Contracts")

    @requires_role("commercial")
    def list_by_commercial(self) -> None:
        """
        List contracts for the current commercial user.
        """
        ctrs = self.repo.list_by_commercial(self.current_user.id)
        self.view.display_contract_table(ctrs, title="My Contracts")

    @requires_role("commercial")
    def list_unsigned_contracts(self) -> None:
        """
        List all unsigned contracts for the current commercial user.
        """
        ctrs = self.repo.list_all()
        filtered = [c for c in ctrs if not c.is_signed]
        self.view.display_contract_table(filtered, title="Unsigned Contracts")

    @requires_role("commercial")
    def list_unpaid_contracts(self) -> None:
        """
        List all contracts not yet fully paid for the current commercial user.
        """
        ctrs = self.repo.list_all()
        filtered = [c for c in ctrs if c.remaining_amount > 0]
        self.view.display_contract_table(filtered, title="Unpaid Contracts")

    @requires_role("gestion")
    def add_contract(self) -> None:
        """
        Prompt and create a new contract, then display result or error.
        """
        try:
            data = self.view.prompt_new_contract()
            contract = self._create_contract(**data)
            capture_event("Contract created", level="info",
                          contract_id=contract.id)
            self.view.show_success(f"Created contract ID {contract.id}")
        except (CrmInvalidValue, CrmNotFoundError) as e:
            capture_event("Contract creation failed",
                          level="error", reason=str(e))
            self.view.show_error(str(e))

    @requires_role("gestion")
    def _create_contract(
        self,
        client_id: int,
        amount: Decimal,
        is_signed: bool,
        end_date: str
    ) -> Contract | None:
        """
        Create a new contract in the database.

        Args:
            client_id: ID of the client.
            amount: Total amount of the contract.
            is_signed: Whether the contract is signed.
            end_date: End date (YYYY-MM-DD).

        Returns:
            Contract: The created Contract.

        Raises:
            CrmInvalidValue: If any field is invalid.
            CrmNotFoundError: If the client does not exist.
            CrmIntegrityError: If saving fails.
        """
        total_amount = validate_amount(amount)
        end_dt = validate_date(end_date)

        client = self.client_repo.get_by_id(client_id)
        if not client:
            raise CrmNotFoundError("Client")

        contract = Contract(
            client_id=client_id,
            commercial_id=client.commercial_id,
            total_amount=total_amount,
            remaining_amount=total_amount,
            creation_date=datetime.now(),
            end_date=end_dt,
            is_signed=is_signed,
        )
        try:
            return self.repo.save(contract)
        except CrmIntegrityError as e:
            capture_event("Contract creation failed",
                          level="error", reason=str(e))
            self.view.show_error(str(e))

    def get_contract_by_id(self, contract_id: int) -> Contract:
        """
        Retrieve a single contract by ID or raise if not found.

        Args:
            contract_id: ID of the contract.

        Returns:
            Contract: The found Contract.

        Raises:
            CrmNotFoundError: If no contract with that ID exists.
        """
        contract = self.repo.get_by_id(contract_id)
        if not contract:
            raise CrmNotFoundError("Contract")
        return contract

    def edit_contract(self) -> None:
        """
        Prompt and update an existing contract, then display result or error.
        """
        try:
            cid = self.view.prompt_contract_id()
            contract = self.get_contract_by_id(cid)
            data = self.view.prompt_edit_contract(contract)
            updated = self._update_contract(contract_id=cid, **data)
            capture_event("Contract updated", level="info",
                          contract_id=updated.id)
            self.view.show_success(f"Updated contract ID {updated.id}")
        except (CrmInvalidValue, CrmNotFoundError) as e:
            capture_event("Contract update failed",
                          level="error", reason=str(e))
            self.view.show_error(str(e))
        except CrmForbiddenAccessError as e:
            capture_event("Contract update failed",
                          level="error", reason=str(e))
            self.view.show_error("You can only update your own contracts.")


    @requires_ownership_or_role(get_contract_owner_id, 'gestion')
    def _update_contract(
        self,
        contract_id: int,
        amount: Decimal = None,
        is_signed: bool = None,
        remaining: Decimal = None,
        end_date: str = None
    ) -> Contract:
        """
        Update an existing contract.

        Args:
            contract_id: ID of the contract to update.
            amount: Total amount of the contract.
            is_signed: Whether the contract is signed.
            remaining: Remaining amount of the contract.
            end_date: End date (YYYY-MM-DD).

        Returns:
            Contract: The updated Contract.

        Raises:
            CrmInvalidValue: If any field is invalid.
            CrmNotFoundError: If the contract does not exist.
            CrmIntegrityError: If saving fails.
        """
        repo = self.repo
        contract = repo.get_by_id(contract_id)
        if not contract:
            raise CrmNotFoundError("Contract")

        if amount is not None:
            contract.total_amount = validate_amount(amount)
        if remaining is not None:
            contract.remaining_amount = validate_amount(remaining)
        if is_signed is not None:
            contract.is_signed = is_signed
        if end_date is not None:
            contract.end_date = validate_date(end_date)

        try:
            return self.repo.save(contract)
        except Exception as e:
            raise CrmIntegrityError(f"Could not update contract: {e}") from e
