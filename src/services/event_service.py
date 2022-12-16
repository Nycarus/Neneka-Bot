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