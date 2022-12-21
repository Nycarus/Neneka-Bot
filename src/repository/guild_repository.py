import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.model import Base
from src.models.guild_model import GuildModel

class GuildRespository:
    def __init__(self):
        load_dotenv()
        self._engine = create_engine(
            f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_NAME')}"
            )
        self._session = sessionmaker()
        self._session.configure(bind=self._engine, expire_on_commit=False)
        Base.metadata.create_all(self._engine)
    
    async def save(self, guild: GuildModel) -> bool:
        if (type(guild) != GuildModel):
            return False

        with self._session() as session:
            session.begin()
            try:
                session.add(guild)
            except Exception as e:
                print (e)
                session.rollback()
                print("Database insert error has occured with Guild.")
                return False
            else:
                session.commit()
                return True

    async def update(self, guild: GuildModel) -> bool:
        if (type(guild) != GuildModel):
            return False

        with self._session() as session:
            session.begin()
            try:
                update = {}
                if (guild.notificationChannelID):
                    update["notificationChannelID"] = guild.notificationChannelID
                if (guild.roleID):
                    update["roleID"] = guild.roleID

                session.query(GuildModel).filter(GuildModel.id == guild.id).update(update)
                
            except Exception as e:
                print (e)
                session.rollback()
                print("Database update error has occured with Guild.")
                return False
            else:
                session.commit()
                return True

    async def update(self, id: int, notificationChannelID : int=None, roleID:int = None) -> bool:
        if (type(id) != int):
            return False

        if (type(notificationChannelID) != int):
            if (notificationChannelID != None):
                return False

        if (type(roleID) != int):
            if (roleID != None):
                return False

        with self._session() as session:
            session.begin()
            try:
                update = {}
                if (notificationChannelID):
                    update["notificationChannelID"] = notificationChannelID
                if (roleID):
                    update["roleID"] = roleID

                session.query(GuildModel).filter(GuildModel.id == id).update(update)
            except Exception as e:
                print (e)
                session.rollback()
                print("Database update error has occured with Guild.")
                return False
            else:
                session.commit()
                return True

    async def delete(self, guild: GuildModel) -> bool:
        if (type(guild) != GuildModel):
            return False

        with self._session() as session:
            session.begin()
            try:
                session.delete(guild)
            except Exception as e:
                print (e)
                session.rollback()
                print("Database delete error has occured with Guild.")
                return False
            else:
                session.commit()
                return True

    async def findByID(self, id: int) -> GuildModel:
        if (type(id) != int):
            return None

        with self._session() as session:
            session.begin()
            try:
                result = session.query(GuildModel).filter(GuildModel.id == id).first()
            except Exception as e:
                print (e)
                session.rollback()
                print("Database query error has occured with Guild.")
                return None
            else:
                session.commit()
                return result