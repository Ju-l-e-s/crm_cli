from sqlalchemy.orm import Session
from typing import List, Type

from models.contract import Contract

class ContractRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, contract: Contract) -> Contract:
        """
        Insert or update a Contract in the database.
        """
        self.session.add(contract)
        self.session.commit()
        self.session.refresh(contract)
        return contract

    def list_all(self) -> list[Type[Contract]]:
        """
        Returns all contracts in the system.
        """
        return self.session.query(Contract).all()

    def list_by_commercial(self, commercial_id: int) -> list[Type[Contract]]:
        """
        Returns contracts created or owned by a specific commercial.
        """
        return self.session.query(Contract).filter(Contract.commercial_id == commercial_id).all()

    def get_by_id(self, contract_id: int) -> Type[Contract] | None:
        """
        Retrieves a contract by its ID, or None if not found.
        """
        return self.session.query(Contract).filter(Contract.id == contract_id).one_or_none()