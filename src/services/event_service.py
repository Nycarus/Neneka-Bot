from src.utils.database import Database
from src.models.event import Event
from sqlalchemy import or_, and_
from datetime import datetime, timedelta

class EventService:
    def __init__(self):
        self._db = Database()

    async def cleanExpiredEvents(self) -> None:
        # Clean events where end dates have passed
        result_event = await self._db.query(Event, Event.endDate <= datetime.utcnow())
        if(result_event):
            await self._db.delete_many(result_event)
            print("Outdated events are cleaned.")

        # Clean events where start date have passed, with no end dates, and it's been a month since event started
        result_content = await self._db.query(Event, Event.startDate <= datetime.utcnow()-timedelta(days=30), Event.endDate == None)
        if(result_content):
            await self._db.delete_many(result_content)
            print("Outdated content updates are cleaned.")

        if (not (result_event or result_content)):
            print("There are no outdated events.")
    
    async def addEvents(self, events) -> bool:
        if(not events):
            return False

        # Query database to check if events already exists
        queries = [and_(Event.name==event['event'], Event.startDate==event['startDate'], Event.endDate==event['endDate']) for event in events]
        results = await self._db.query_many(Event, queries)

        if (results == None):
            print("Something has went wrong with querying for existing events.")
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
                eventModel = Event(name=event['event'], startDate=event['startDate'], endDate=event['endDate'])
            else:
                eventModel = Event(name=event['event'], startDate=event['startDate'])
            
            eventModels.append(eventModel)

            
        if (not eventModels):
            print("No new events.")
            return False

        # Insert models to db
        result = await self._db.insert_many(eventModels)
        if (result):
            print("Events are added to database successfully.")
    
    async def getCurrentEvents(self):
        currentDateUTC = datetime.utcnow()
        results = await self._db.query(Event, Event.startDate <= currentDateUTC, Event.endDate >= currentDateUTC)
        
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
        currentDateUTC = datetime.utcnow()
        results = await self._db.query(Event, Event.startDate <= currentDateUTC, Event.endDate >= currentDateUTC, Event.endDate <= currentDateUTC + timedelta(days=days))

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
        currentDateUTC = datetime.utcnow()
        results = await self._db.query(Event, Event.startDate >= currentDateUTC, Event.startDate <= currentDateUTC + timedelta(days=days))

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
