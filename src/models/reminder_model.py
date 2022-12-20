from sqlalchemy import Column, BIGINT, String, DateTime
from src.models.model import Base

class ReminderModel(Base):
    __tablename__ = "reminder"

    id = Column(BIGINT, primary_key=True)
    description = Column(String)
    endDate = Column(DateTime)
    startDate = Column(DateTime)
    userID = Column(BIGINT)
    channelID = Column(BIGINT, nullable=True)
    guildID = Column(BIGINT, nullable=True)