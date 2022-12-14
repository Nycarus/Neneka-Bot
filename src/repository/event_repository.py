import os
from datetime import datetime
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.model import Base
from src.models.event_model import EventModel
from src.utils.logger import setup_logger
from src.utils.secrets import access_secret_version

class EventRespository:
    def __init__(self):
        load_dotenv()
        if (int(os.environ.get("PRODUCTION", 0)) == 1):
            postgres_user = access_secret_version('POSTGRES_USER')
            postgres_password = access_secret_version('POSTGRES_PASSWORD')
            postgres_host = access_secret_version('POSTGRES_HOST')
            postgres_port = access_secret_version('POSTGRES_PORT')
            postgres_name = access_secret_version('POSTGRES_NAME')
            self._engine = create_engine( f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_name}")
        else:
            self._engine = create_engine(
                f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_NAME')}"
                )
        self._session = sessionmaker()
        self._session.configure(bind=self._engine, expire_on_commit=False)
        Base.metadata.create_all(self._engine)
        self._logger = setup_logger('bot.repository.event', '/data/discord.log')
    
    async def save(self, event: EventModel) -> bool:
        if (type(event) != EventModel or not event):
            self._logger.error(f"Incorrect datatype: event with type {type(event)}")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                session.add(event)
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database insert error has occured with Event.save.")
                return False
            else:
                session.commit()
                return True
        
    async def saveAll(self, events: list[EventModel]) -> bool:
        if (type(events) != list or not events):
            self._logger.error(f"Incorrect datatype: events with type {type(events)}")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                for event in events:
                    session.add(event)
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database insert error has occured with Event.saveAll.")
                return False
            else:
                session.commit()
                return True

    async def delete(self, event: EventModel) -> bool:
        if (type(event) != EventModel or not event):
            self._logger.error(f"Incorrect datatype: event with type {type(event)}")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                session.delete(event)
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database delete error has occured with Event.delete.")
                return False
            else:
                session.commit()
                return True

    async def deleteAll(self, events: list[EventModel]) -> bool:
        if (type(events) != list or not events):
            self._logger.error(f"Incorrect datatype: events with type {type(events)}")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                for event in events:
                    session.delete(event)
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database delete error has occured with Event.deleteAll.")
                return False
            else:
                session.commit()
                return True

    async def findAllByID(self, id:int) -> list[EventModel]:
        if (type(id) != int):
            self._logger.error(f"Incorrect datatype: id with type {type(id)}")
            return None

        with self._session() as session:
            session.begin()
            try:
                results = session.query(EventModel).filter(EventModel.id == id).first()
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database query error has occured with Event.findAllByID.")
                return None
            else:
                session.commit()
                return results

    async def update(self, event: EventModel) -> bool:
        if (type(event) != EventModel):
            self._logger.error(f"Incorrect datatype: event with type {type(event)}")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                update = {}
                if (event.name):
                    update["name"] = event.name
                if (event.startDate):
                    update["startDate"] = event.startDate
                if (event.endDate):
                    update["endDate"] = event.endDate

                session.query(EventModel).filter(EventModel.id==event.id).update(update)
                
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database update error has occured with Event.update.")
                return False
            else:
                session.commit()
                return True

    async def findByName(self, name:str) -> list[EventModel]:
        if (type(name) != str):
            self._logger.error(f"Incorrect datatype: name with type {type(name)}")
            return None

        with self._session() as session:
            session.begin()
            try:
                results = session.query(EventModel).filter(EventModel.name == name).first()
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database query error has occured with Event.findByName.")
                return None
            else:
                session.commit()
                return results

    async def findByNameAndDate(self, name:str, startDate: datetime, endDate: datetime) -> list[EventModel]:
        if (type(name) != str):
            self._logger.error(f"Incorrect datatype: name with type {type(name)}")
            return None

        if (type(startDate) != datetime):
            self._logger.error(f"Incorrect datatype: startDate with type {type(startDate)}")
            return None

        if (type(endDate) != datetime):
            if (endDate != None):
                self._logger.error(f"Incorrect datatype: endDate with type {type(endDate)}")
                return None

        with self._session() as session:
            session.begin()
            try:
                if (endDate):
                    results = session.query(EventModel).filter(EventModel.name == name, EventModel.startDate==startDate, EventModel.endDate==endDate).first()
                else:
                    results = session.query(EventModel).filter(EventModel.name == name, EventModel.startDate==startDate, EventModel.endDate==sqlalchemy.sql.null()).first()
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database query error has occured with Event.findByNameAndDate.")
                return None
            else:
                session.commit()
                return results
    
    async def findAllByEndDate(self, date: datetime, order:str=None) -> list[EventModel]:
        if (type(date) != datetime):
            if (date != None):
                self._logger.error(f"Incorrect datatype: date with type {type(date)}")
                return None

        if (type(order) != str):
            if (order != None):
                self._logger.error(f"Incorrect datatype: order with type {type(order)}")
                return None

        with self._session() as session:
            session.begin()
            try:
                query = session.query(EventModel)
                
                if(order == "desc"):
                    query = query.order_by(EventModel.endDate.desc())
                elif (order == "asc"):
                    query = query.order_by(EventModel.endDate.asc())

                if (date):
                    query = query.filter(EventModel.endDate==date)
                else:
                    query = query.filter(EventModel.endDate==sqlalchemy.sql.null())

                results = query.all()

            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database query error has occured with Event.findAllByEndDate.")
                return None
            else:
                session.commit()
                return results

    async def findAllByDateBetween(self, date:datetime, order:str=None) -> list[EventModel]:
        if (type(date) != datetime):
            self._logger.error(f"Incorrect datatype: date with type {type(date)}")
            return None
        if (type(order) != str):
            if (order != None):
                self._logger.error(f"Incorrect datatype: order with type {type(order)}")
                return None

        with self._session() as session:
            session.begin()
            try:
                query = session.query(EventModel).group_by(EventModel.endDate, EventModel.id)

                if(order == "desc"):
                    query = query.order_by(EventModel.endDate.desc())
                elif (order == "asc"):
                    query = query.order_by(EventModel.endDate.asc())
                
                results = query.filter(EventModel.startDate <= date, EventModel.endDate >= date).all()

            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database query error has occured with Event.findAllByDateBetween.")
                return None
            else:
                session.commit()
                return results

    async def findAllByStartDateBetween(self, startDate:datetime, endDate:datetime, order:str=None) -> list[EventModel]:
        if (type(startDate) != datetime):
            self._logger.error(f"Incorrect datatype: startDate with type {type(startDate)}")
            return None
        if (type(endDate) != datetime):
            self._logger.error(f"Incorrect datatype: endDate with type {type(endDate)}")
            return None
        if (type(order) != str):
            if (order != None):
                self._logger.error(f"Incorrect datatype: order with type {type(order)}")
                return None

        with self._session() as session:
            session.begin()
            try:
                query = session.query(EventModel).group_by(EventModel.startDate, EventModel.endDate, EventModel.id)

                if(order == "desc"):
                    query = query.order_by(EventModel.startDate.desc())
                elif (order == "asc"):
                    query = query.order_by(EventModel.startDate.asc())
                
                results = query.filter(EventModel.startDate >= startDate, EventModel.startDate <= endDate).all()

            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database query error has occured with Event.findAllByStartDateBetween.")
                return None
            else:
                session.commit()
                return results

    async def findAllByEndDateBetween(self, startDate:datetime, endDate:datetime, order:str=None) -> list[EventModel]:
        if (type(startDate) != datetime):
            self._logger.error(f"Incorrect datatype: startDate with type {type(startDate)}")
            return None
        if (type(endDate) != datetime):
            self._logger.error(f"Incorrect datatype: endDate with type {type(endDate)}")
            return None
        if (type(order) != str):
            if (order != None):
                self._logger.error(f"Incorrect datatype: order with type {type(order)}")
                return None

        with self._session() as session:
            session.begin()
            try:
                query = session.query(EventModel).group_by(EventModel.endDate, EventModel.startDate, EventModel.id)

                if(order == "desc"):
                    query = query.order_by(EventModel.endDate.desc())
                elif (order == "asc"):
                    query = query.order_by(EventModel.endDate.asc())
                
                results = query.filter(EventModel.endDate >= startDate, EventModel.endDate <= endDate).all()

            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database query error has occured with Event.findAllByEndDateBetween.")
                return None
            else:
                session.commit()
                return results

    async def findAllByEndDateLessThanEqual(self, date:datetime, order:str=None) -> list[EventModel]:
        if (type(date) != datetime):
            self._logger.error(f"Incorrect datatype: date with type {type(date)}")
            return None
        if (type(order) != str):
            if (order != None):
                self._logger.error(f"Incorrect datatype: order with type {type(order)}")
                return None

        with self._session() as session:
            session.begin()
            try:
                query = session.query(EventModel).group_by(EventModel.endDate, EventModel.startDate, EventModel.id)

                if(order == "desc"):
                    query = query.order_by(EventModel.endDate.desc())
                elif (order == "asc"):
                    query = query.order_by(EventModel.endDate.asc())
                
                results = query.filter(EventModel.endDate <= date).all()

            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database query error has occured with Event.findAllByEndDateLessThanEqual.")
                return None
            else:
                session.commit()
                return results