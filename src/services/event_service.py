from datetime import datetime, timedelta

from src.models.event_model import EventModel
from src.repository.event_repository import EventRespository
from src.utils.logger import setup_logger

class EventService:
    def __init__(self):
        self._eventRespository = EventRespository()
        self._logger = setup_logger('bot.service.event', '/data/discord.log')

    async def cleanExpiredEvents(self) -> None:
        # Clean events where end dates have passed
        result_event: list[EventModel] = await self._eventRespository.findAllByEndDateLessThanEqual(datetime.utcnow())
        if(result_event):
            await self._eventRespository.deleteAll(result_event)
            self._logger.info("Outdated events are cleaned.")
        
        # Clean events where start date have passed, with no end dates, and it's been a month since event started
        result_content: list[EventModel] = await self._eventRespository.findAllByEndDate(None)
        deletePile = []

        if(result_content):
            # Add EventModel to delete pile where startDate is 7 days ago
            for result in result_content:
                if (result.startDate <= datetime.utcnow() - timedelta(days=7)):
                    deletePile.append(result)

            if(deletePile):
                await self._eventRespository.deleteAll(deletePile)
                self._logger.info("Outdated content updates are cleaned.")

        if (not (result_event or deletePile)):
            self._logger.info("There are no outdated events.")
    
    async def addEvents(self, events) -> bool:
        if(not events):
            return False

        # Query database to check if events already exists
        results = []
        for event in events:
            results.append(await self._eventRespository.findByNameAndDate(name=event['event'], startDate=event['startDate'], endDate=event['endDate']))
        
        if (results == None or len(results) != len(events)):
            self._logger.error("Something has went wrong with querying for existing events.")
            return False

        # Converting events to database models that have not expired
        eventModels = []
        for index, event in enumerate(events):
            # Don't add event if it already exist
            if (results[index]):
                continue
            
            # Create event model
            if ('endDate' in event.keys() and event['endDate']):
                if (datetime.utcnow() > event['endDate']):
                    continue
                eventModel = EventModel(name=event['event'], startDate=event['startDate'], endDate=event['endDate'])
            else:
                # Do not add if it's 7 days old
                if (datetime.utcnow() - timedelta(days=7) > event['startDate']):
                    continue
                eventModel = EventModel(name=event['event'], startDate=event['startDate'])
            
            eventModels.append(eventModel)

        if (not eventModels):
            self._logger.info("There are no new events added.")
            return False

        # Insert models to db
        result = await self._eventRespository.saveAll(eventModels)
        if (result):
            self._logger.info("Events are added to database successfully.")
    
    async def getCurrentEvents(self):
        results = await self._eventRespository.findAllByDateBetween(date=datetime.utcnow(), order="desc")
        
        data = []
        for result in results:
            data.append({
                "name": result.name, 
                "startDate" : self.formatDiscordDate(result.startDate), 
                "endDate" : self.formatDiscordDate(result.endDate),
                "startDateRelative" : self.formatDiscordDateRelative(result.startDate), 
                "endDateRelative" : self.formatDiscordDateRelative(result.endDate)})

        return data

    async def getEventsEnding(self, days:int):
        results = await self._eventRespository.findAllByEndDateBetween(startDate=datetime.utcnow(), endDate = datetime.utcnow() + timedelta(days=days), order="desc")

        data = []
        for result in results:
            data.append({
                "name": result.name, 
                "startDate" : self.formatDiscordDate(result.startDate), 
                "endDate" : self.formatDiscordDate(result.endDate),
                "startDateRelative" : self.formatDiscordDateRelative(result.startDate), 
                "endDateRelative" : self.formatDiscordDateRelative(result.endDate)})

        return data

    async def getEventsUpcoming(self, days:int):
        results = await self._eventRespository.findAllByStartDateBetween(startDate=datetime.utcnow(), endDate = datetime.utcnow() + timedelta(days=days), order="desc")

        data = []
        for result in results:
            data.append({
                "name": result.name, 
                "startDate" : self.formatDiscordDate(result.startDate), 
                "endDate" : self.formatDiscordDate(result.endDate),
                "startDateRelative" : self.formatDiscordDateRelative(result.startDate), 
                "endDateRelative" : self.formatDiscordDateRelative(result.endDate)})

        return data

    def formatDiscordDate(self, date: datetime):
        if (not date):
            return None

        epoch_time = datetime(1970, 1, 1)
        date = date - epoch_time
        return f'<t:{int(date.total_seconds())}:f>'

    def formatDiscordDateRelative(self, date):
        if (not date):
            return None

        epoch_time = datetime(1970, 1, 1)
        date = date - epoch_time
        return f'<t:{int(date.total_seconds())}:R>'
