import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import sessionmaker
from src.models.model import Base

class Database:
    def __init__(self):
        load_dotenv()

        self._engine = create_engine(
            f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_NAME')}"
            )
        self._session = sessionmaker()
        self._session.configure(bind=self._engine)
        Base.metadata.create_all(self._engine)
        print("Postgres database initialized and ready.")

    async def query(self, model, *query):
        with self._session() as session:
            session.begin()
            try:
                if(query):
                    results = session.query(model).filter(*query).all()
                else:
                    results = session.query(model).all()
            except Exception as e:
                print (e)
                session.rollback()
                print("Database query error has occured.")
                return None
            else:
                session.commit()
                return results
    
    async def query_many(self, model, queries):
        with self._session() as session:
            session.begin()
            try:
                if(queries):
                    results = []
                    for query in queries:
                        results.append(session.query(model).filter(*query).first())
                else:
                    raise Exception("Query is null.")
            except Exception as e:
                print (e)
                session.rollback()
                print("Database query error has occured.")
                return None
            else:
                session.commit()
                return results

    async def insert(self, object):
        with self._session() as session:
            session.begin()
            try:
                session.add(object)
            except:
                session.rollback()
                print("Database insertion error has occured.")
                return False
            else:
                session.commit()
                return True

    async def insert_many(self, objects):
        with self._session() as session:
            session.begin()
            try:
                for object in objects:
                    session.add(object)
            except:
                session.rollback()
                print("Database insertion error has occured.")
                return False
            else:
                session.commit()
                return True
    
    async def delete(self, object):
        with self._session() as session:
            session.begin()
            try:
                session.delete(object)
            except:
                session.rollback()
                print("Database deletion error has occured.")
                return False
            else:
                session.commit()
                return True

    async def delete_many(self, objects):
        with self._session() as session:
            session.begin()
            try:
                for object in objects:
                    session.delete(object)
            except:
                session.rollback()
                print("Database deletion error has occured.")
                return False
            else:
                session.commit()
                return True