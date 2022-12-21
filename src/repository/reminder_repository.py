import os
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.model import Base
from src.models.reminder_model import ReminderModel
from src.utils.logger import setup_logger

class ReminderRespository:
    def __init__(self):
        load_dotenv()
        self._engine = create_engine(
            f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_NAME')}"
            )
        self._session = sessionmaker()
        self._session.configure(bind=self._engine, expire_on_commit=False)
        Base.metadata.create_all(self._engine)
        self._logger = setup_logger('bot.repository.reminder', '/data/discord.log')

    async def save(self, reminder: ReminderModel) -> bool:
        if (type(reminder) != ReminderModel or not reminder):
            self._logger.error(f"Incorrect datatype: reminder with type {type(reminder)}")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                session.add(reminder)
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database insert error has occured with Reminder.save.")
                return False
            else:
                session.commit()
                return True

    async def deleteAll(self, reminders: list[ReminderModel]) -> bool:
        if (type(reminders) != list or not reminders):
            self._logger.error(f"Incorrect datatype: reminders with type {type(reminders)}")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                for reminder in reminders:
                    session.delete(reminder)
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database delete error has occured with Reminder.deleteAll.")
                return False
            else:
                session.commit()
                return True

    async def findAllByUserID(self, id:int) -> list[ReminderModel]:
        if (type(id) != int or not id):
            self._logger.error(f"Incorrect datatype: id with type {type(id)}")
            return None

        with self._session() as session:
            session.begin()
            try:
                results = session.query(ReminderModel).filter(ReminderModel.userID == id).all()
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database query error has occured with Reminder.findAllByUserID.")
                return None
            else:
                session.commit()
                return results

    async def findAllByDateLessThanEqual(self, date:datetime) -> list[ReminderModel]:
        if (type(date) != datetime or not date):
            self._logger.error(f"Incorrect datatype: date with type {type(date)}")
            return None

        with self._session() as session:
            session.begin()
            try:
                results = session.query(ReminderModel).filter(ReminderModel.endDate <= date).all()
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database query error has occured with Reminder.findAllByDateLessThanEqual.")
                return None
            else:
                session.commit()
                return results