from sqlalchemy import Column, Integer, String, DateTime
from src.models.model import Base

class GuildModel(Base):
    __tablename__ = "guild"

    id = Column(Integer, primary_key=True)
    notificationChannelID = Column(Integer)
    commandChannelID = Column(Integer)