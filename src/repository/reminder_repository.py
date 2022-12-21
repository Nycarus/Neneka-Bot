import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.model import Base
from src.models.reminder_model import ReminderModel


class ReminderRespository:
    def __init__(self):
        load_dotenv()
        self._engine = create_engine(
            f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_NAME')}"
            )
        self._session = sessionmaker()
        self._session.configure(bind=self._engine, expire_on_commit=False)
        Base.metadata.create_all(self._engine)

    async def save(self, reminder: ReminderModel) -> bool:
        if (type(reminder) != ReminderModel or not reminder):
            print("Incorrect datatype.")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                session.add(reminder)
            except Exception as e:
                print (e)
                session.rollback()
                print("Database insert error has occured with reminder.")
                return False
            else:
                session.commit()
                return True

    async def deleteAll(self, reminders: list[ReminderModel]) -> bool:
        if (type(reminders) != list or not reminders):
            print("Incorrect datatype.")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                for reminder in reminders:
                    session.delete(reminder)
            except Exception as e:
                print (e)
                session.rollback()
                print("Database delete error has occured with Reminder.")
                return False
            else:
                session.commit()
                return True

    async def findAllByDateLessThanEqual(self, date:datetime) -> list[ReminderModel]:
        if (type(date) != datetime or not date):
            return None

        with self._session() as session:
            session.begin()
            try:
                results = session.query(ReminderModel).filter(ReminderModel.endDate <= date).all()
            except Exception as e:
                print (e)
                session.rollback()
                print("Database query error has occured with Reminder.")
                return None
            else:
                session.commit()
                return results