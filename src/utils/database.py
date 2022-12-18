import os
from dotenv import load_dotenv
import sqlalchemy
from sqlalchemy import create_engine, or_, and_
from sqlalchemy.orm import sessionmaker
from src.models.model import Base

class Database:
    """
    This class creates a data access object (DAO) to handle database operations and
    is intended to reduce boiler plate code when working with sqlalchemy.
    """
    def __init__(self):
        load_dotenv()

        self._engine = create_engine(
            f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_NAME')}"
            )
        self._session = sessionmaker()
        self._session.configure(bind=self._engine, expire_on_commit=False)
        Base.metadata.create_all(self._engine)
        print("Postgres database initialized and ready.")

    async def query(self, model: Base, *query: sqlalchemy.sql.elements.BinaryExpression) -> list[Base]:
        """
        This method queries the database within a transaction.

        Example usage: `query(Ball, Ball.name == "Ball Name", Ball.colour == "Blue")`

        :param model: the Class model that is being queried
        :param query: positional arguments that represent the binary operations of WHERE
        :return: returns a list of objects queried from the database or `None` if the query fails
        """
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
    
    async def query_many(self, model: Base, queries: list[sqlalchemy.sql.elements.BinaryExpression]) -> list[Base]:
        """
        This method does multiple queries from the database within a transaction.

        Example usage: `query(Ball, [and_(Ball.name == "Ball Name", Ball.colour == "Blue"), ...])`

        :param model: the Class model that is being queried
        :param queries: a list of positional arguments that represent the binary operations of WHERE
        :return: returns a 2D list of objects queried from the database or `None` if the query fails
        """
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

    async def insert(self, object: list[Base]) -> bool:
        """
        This method inserts an object to database within a transaction.

        Example usage: `insert(Ball, ball)`

        :param model: the Class model that is being inserted
        :param object: the model object that is being inserted
        :return: returns a boolean value representing the success of inserting the object
        """
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

    async def insert_many(self, objects: list[Base]) -> bool:
        """
        This method inserts multiple objects to database within a transaction.

        Example usage: `insert(Ball, [ball1, ball2, ball3])`

        :param model: the Class model that is being inserted
        :param object: a list of model object that are being inserted
        :return: returns a boolean value representing the success of inserting the objects
        """
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
    
    async def delete(self, object: list[Base]) -> bool:
        """
        This method deletes an object from database within a transaction.

        Example usage: `delete(Ball, ball)`

        :param model: the Class model that is being deleted
        :param object: the model object that are being deleted
        :return: returns a boolean value representing the success of deleting the row
        """
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

    async def delete_many(self, objects: list[Base]) -> bool:
        """
        This method deletes multiple objects from database within a transaction.

        Example usage: `delete(Ball, [ball1, ball2, ball3])`

        :param model: the Class model that is being deleted
        :param object: a list of model object that are being deleted
        :return: returns a boolean value representing the success of deleting the rows
        """
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