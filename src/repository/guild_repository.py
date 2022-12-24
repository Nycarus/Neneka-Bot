import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.model import Base
from src.models.guild_model import GuildModel
from src.utils.logger import setup_logger
from src.utils.secrets import access_secret_version

class GuildRespository:
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
        self._logger = setup_logger('bot.repository.guild', '/data/discord.log')
    
    async def save(self, guild: GuildModel) -> bool:
        if (type(guild) != GuildModel):
            self._logger.error(f"Incorrect datatype: guild with type {type(guild)}")
            return False

        with self._session() as session:
            session.begin()
            try:
                session.add(guild)
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database insert error has occured with Guild.save.")
                return False
            else:
                session.commit()
                return True

    async def update(self, guild: GuildModel) -> bool:
        if (type(guild) != GuildModel):
            self._logger.error(f"Incorrect datatype: guild with type {type(guild)}")
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
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database update error has occured with Guild.update.")
                return False
            else:
                session.commit()
                return True

    async def update(self, id: int, notificationChannelID : int=None, roleID:int = None) -> bool:
        if (type(id) != int):
            self._logger.error(f"Incorrect datatype: id with type {type(id)}")
            return False

        if (type(notificationChannelID) != int):
            if (notificationChannelID != None):
                self._logger.error(f"Incorrect datatype: notificationChannelID with type {type(notificationChannelID)}")
                return False

        if (type(roleID) != int):
            if (roleID != None):
                self._logger.error(f"Incorrect datatype: roleID with type {type(roleID)}")
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
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database update error has occured with Guild.update.")
                return False
            else:
                session.commit()
                return True

    async def delete(self, guild: GuildModel) -> bool:
        if (type(guild) != GuildModel):
            self._logger.error(f"Incorrect datatype: guild with type {type(guild)}")
            return False

        with self._session() as session:
            session.begin()
            try:
                session.delete(guild)
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database delete error has occured with Guild.delete.")
                return False
            else:
                session.commit()
                return True

    async def findByID(self, id: int) -> GuildModel:
        if (type(id) != int):
            self._logger.error(f"Incorrect datatype: id with type {type(id)}")
            return None

        with self._session() as session:
            session.begin()
            try:
                result = session.query(GuildModel).filter(GuildModel.id == id).first()
            except Exception as e:
                self._logger.error(e)
                session.rollback()
                self._logger.error("Database query error has occured with Guild.findByID.")
                return None
            else:
                session.commit()
                return result