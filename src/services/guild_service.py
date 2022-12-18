from src.utils.database import Database
from src.models.guild import Guild
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

class GuildService:
    def __init__(self):
        self._db = Database()