from src.repository.reminder_repository import ReminderRespository
from src.models.reminder_model import ReminderModel
import discord
from datetime import datetime

class ReminderService:
    def __init__(self):
        self._reminderRepository = ReminderRespository()

    async def addReminder(self, date:datetime, description:str, userID: int, guildID: int=None, channelID: int=None):
        reminder = ReminderModel(startDate=datetime.utcnow(), endDate=date, description=description, userID=userID, guildID=guildID, channelID=channelID)
        result = await self._reminderRepository.save(reminder)
        return result

    async def getAndDeleteOldReminders(self):
        reminders = await self._reminderRepository.findAllByDateLessThanEqual(date=datetime.utcnow())
        
        if (not reminders):
            return None
        
        result = await self._reminderRepository.deleteAll(reminders)

        if (result):
            return reminders
        else:
            return None
