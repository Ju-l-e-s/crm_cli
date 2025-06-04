from typing import Type
from sqlalchemy.orm import Session
from models.client import Client


class ClientRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> Client | None:
        return self.session.query(Client).filter_by(email=email).first()

    def get_by_id(self, client_id: int) -> Client | None:
        return self.session.query(Client).filter_by(id=client_id).first()

    def save(self, client: Client) -> Client:
        try:
            self.session.add(client)
            self.session.commit()
            self.session.refresh(client)
            return client
        except Exception:
            self.session.rollback()
            raise

    def list_all(self) -> list[Type[Client]]:
        return self.session.query(Client).all()

    def list_by_commercial(self, user_id: int) -> list[Type[Client]]:
        return self.session.query(Client).filter_by(commercial_id=user_id).all()

