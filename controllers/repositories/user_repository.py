from typing import Type

from sqlalchemy.orm import Session

from models.user import User


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_email(self, email: str) -> User | None:
        return self.session.query(User).filter_by(email=email).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.session.query(User).filter_by(id=user_id).first()

    def save(self, user: User) -> User:
        try:
            self.session.add(user)
            self.session.commit()
            self.session.refresh(user)
            return user
        except Exception:
            self.session.rollback()
            raise

    def delete(self, user: User) -> None:
        try:
            self.session.delete(user)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
    def list_all(self) -> list[Type[User]]:
        return self.session.query(User).all()

