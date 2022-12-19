from sqlalchemy import Column, BIGINT
from src.models.model import Base

class GuildModel(Base):
    __tablename__ = "guild"

    id = Column(BIGINT, primary_key=True)
    notificationChannelID = Column(BIGINT, nullable=True)
    commandChannelID = Column(BIGINT, nullable=True)