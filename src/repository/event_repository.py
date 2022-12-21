import os
from datetime import datetime
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.model import Base
from src.models.event_model import EventModel


class EventRespository:
    def __init__(self):
        load_dotenv()
        self._engine = create_engine(
            f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_NAME')}"
            )
        self._session = sessionmaker()
        self._session.configure(bind=self._engine, expire_on_commit=False)
        Base.metadata.create_all(self._engine)
    
    async def save(self, event: EventModel) -> bool:
        if (type(event) != EventModel or not event):
            print("Incorrect datatype.")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                session.add(event)
            except Exception as e:
                print (e)
                session.rollback()
                print("Database insert error has occured with Event.")
                return False
            else:
                session.commit()
                return True
        
    async def saveAll(self, events: list[EventModel]) -> bool:
        if (type(events) != list or not events):
            print("Incorrect datatype.")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                for event in events:
                    session.add(event)
            except Exception as e:
                print (e)
                session.rollback()
                print("Database insert error has occured with Event.")
                return False
            else:
                session.commit()
                return True

    async def delete(self, event: EventModel) -> bool:
        if (type(event) != EventModel or not event):
            print("Incorrect datatype.")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                session.delete(event)
            except Exception as e:
                print (e)
                session.rollback()
                print("Database delete error has occured with Event.")
                return False
            else:
                session.commit()
                return True

    async def deleteAll(self, events: list[EventModel]) -> bool:
        if (type(events) != list or not events):
            print("Incorrect datatype.")
            return False
        
        with self._session() as session:
            session.begin()
            try:
                for event in events:
                    session.delete(event)
            except Exception as e:
                print (e)
                session.rollback()
                print("Database delete error has occured with Event.")
                return False
            else:
                session.commit()
                return True

    async def findAllByID(self, id:int) -> list[EventModel]:
        if (type(id) != int):
            return None

        with self._session() as session:
            session.begin()
            try:
                results = session.query(EventModel).filter(EventModel.id == id).first()
            except Exception as e:
                print (e)
                session.rollback()
                print("Database query error has occured with Event.")
                return None
            else:
                session.commit()
                return results

    async def update(self, event: EventModel) -> bool:
        if (type(event) != EventModel):
            print("Incorrect datatype.")
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
                print (e)
                session.rollback()
                print("Database update error has occured with Event.")
                return False
            else:
                session.commit()
                return True

    async def findByName(self, name:str) -> list[EventModel]:
        if (type(name) != str):
            return None

        with self._session() as session:
            session.begin()
            try:
                results = session.query(EventModel).filter(EventModel.name == name).first()
            except Exception as e:
                print (e)
                session.rollback()
                print("Database query error has occured with Event.")
                return None
            else:
                session.commit()
                return results

    async def findByNameAndDate(self, name:str, startDate: datetime, endDate: datetime) -> list[EventModel]:
        if (type(name) != str):
            return None

        if (type(startDate) != datetime):
            return None

        if (type(endDate) != datetime):
            if (endDate != None):
                return None

        with self._session() as session:
            session.begin()
            try:
                if (endDate):
                    results = session.query(EventModel).filter(EventModel.name == name, EventModel.startDate==startDate, EventModel.endDate==endDate).first()
                else:
                    results = session.query(EventModel).filter(EventModel.name == name, EventModel.startDate==startDate, EventModel.endDate==sqlalchemy.sql.null()).first()
            except Exception as e:
                print (e)
                session.rollback()
                print("Database query error has occured with Event.")
                return None
            else:
                session.commit()
                return results
    
    async def findAllByEndDate(self, date: datetime, order:str=None) -> list[EventModel]:
        if (type(date) != datetime):
            if (date != None):
                return None

        if (type(order) != str):
            if (order != None):
                return None

        with self._session() as session:
            session.begin()
            try:
                query = session.query(EventModel)
                
                if(order == "desc"):
                    query = query.order_by(EventModel.endDate.desc())
                elif (order == "asc"):
                    query = query.order_by(EventModel.endDate.desc())

                if (date):
                    query = query.filter(EventModel.endDate==date)
                else:
                    query = query.filter(EventModel.endDate==sqlalchemy.sql.null())

                results = query.all()

            except Exception as e:
                print (e)
                session.rollback()
                print("Database query error has occured with Event.")
                return None
            else:
                session.commit()
                return results

    async def findAllByDateBetween(self, date:datetime, order:str=None) -> list[EventModel]:
        if (type(date) != datetime):
            return None
        if (type(order) != str):
            if (order != None):
                return None

        with self._session() as session:
            session.begin()
            try:
                query = session.query(EventModel).group_by(EventModel.endDate, EventModel.id)

                if(order == "desc"):
                    query = query.order_by(EventModel.endDate.desc())
                elif (order == "asc"):
                    query = query.order_by(EventModel.endDate.desc())
                
                results = query.filter(EventModel.startDate <= date, EventModel.endDate >= date).all()

            except Exception as e:
                print (e)
                session.rollback()
                print("Database query error has occured with Event.")
                return None
            else:
                session.commit()
                return results

    async def findAllByStartDateBetween(self, startDate:datetime, endDate:datetime, order:str=None) -> list[EventModel]:
        if (type(startDate) != datetime):
            return None
        if (type(endDate) != datetime):
            return None
        if (type(order) != str):
            if (order != None):
                return None

        with self._session() as session:
            session.begin()
            try:
                query = session.query(EventModel).group_by(EventModel.startDate, EventModel.endDate, EventModel.id)

                if(order == "desc"):
                    query = query.order_by(EventModel.startDate.desc())
                elif (order == "asc"):
                    query = query.order_by(EventModel.startDate.desc())
                
                results = query.filter(EventModel.startDate >= startDate, EventModel.startDate <= endDate).all()

            except Exception as e:
                print (e)
                session.rollback()
                print("Database query error has occured with Event.")
                return None
            else:
                session.commit()
                return results

    async def findAllByEndDateBetween(self, startDate:datetime, endDate:datetime, order:str=None) -> list[EventModel]:
        if (type(startDate) != datetime):
            return None
        if (type(endDate) != datetime):
            return None
        if (type(order) != str):
            if (order != None):
                return None

        with self._session() as session:
            session.begin()
            try:
                query = session.query(EventModel).group_by(EventModel.endDate, EventModel.startDate, EventModel.id)

                if(order == "desc"):
                    query = query.order_by(EventModel.endDate.desc())
                elif (order == "asc"):
                    query = query.order_by(EventModel.endDate.desc())
                
                results = query.filter(EventModel.endDate >= startDate, EventModel.endDate <= endDate).all()

            except Exception as e:
                print (e)
                session.rollback()
                print("Database query error has occured with Event.")
                return None
            else:
                session.commit()
                return results

    async def findAllByEndDateLessThanEqual(self, date:datetime, order:str=None) -> list[EventModel]:
        if (type(date) != datetime):
            return None
        if (type(order) != str):
            if (order != None):
                return None

        with self._session() as session:
            session.begin()
            try:
                query = session.query(EventModel).group_by(EventModel.endDate, EventModel.startDate, EventModel.id)

                if(order == "desc"):
                    query = query.order_by(EventModel.endDate.desc())
                elif (order == "asc"):
                    query = query.order_by(EventModel.endDate.desc())
                
                results = query.filter(EventModel.endDate <= date).all()

            except Exception as e:
                print (e)
                session.rollback()
                print("Database query error has occured with Event.")
                return None
            else:
                session.commit()
                return results