from typing import Type

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.contract import Contract


class ContractRepository:
    """Repository class for handling database operations for Contract model."""

    def __init__(self, session: Session):
        """Initialize the ContractRepository with a database session.

        Args:
            session (Session): SQLAlchemy database session.
        """
        self.session = session

    def save(self, contract: Contract) -> Contract:
        """Insert or update a Contract in the database.

        Args:
            contract (Contract): The Contract object to save.

        Returns:
            Contract: The saved Contract object with updated attributes.

        Raises:
            Exception: If there is an error during database operations.
        """
        try:
            self.session.add(contract)
            self.session.commit()
            self.session.refresh(contract)
            return contract
        except IntegrityError:
            self.session.rollback()
            raise

    def list_all(self) -> list[Type[Contract]]:
        """Retrieve all contracts from the database.

        Returns:
            list[Type[Contract]]: A list of all Contract objects.
        """
        return self.session.query(Contract).all()

    def list_by_commercial(self, commercial_id: int) -> list[Type[Contract]]:
        """Retrieve all contracts associated with a specific commercial user.

        Args:
            commercial_id (int): The ID of the commercial user.

        Returns:
            list[Type[Contract]]: A list of Contract objects associated with the commercial.
        """
        return self.session.query(Contract).filter(Contract.commercial_id == commercial_id).all()

    def get_by_id(self, contract_id: int) -> Type[Contract] | None:
        """Retrieve a contract by its ID.

        Args:
            contract_id (int): The ID of the contract to retrieve.

        Returns:
            Type[Contract] | None: The Contract object if found, None otherwise.
        """
        return self.session.query(Contract).filter(Contract.id == contract_id).one_or_none()
