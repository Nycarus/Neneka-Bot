from src.repository.guild_repository import GuildRespository
from src.models.guild_model import GuildModel

class GuildService:
    def __init__(self):
        self._guildRepository = GuildRespository()

    async def addGuild(self, id: int):
        result = await self._guildRepository.findByID(id)
        
        if (not result):
            guild = GuildModel(id=id)
            return await self._guildRepository.save()
        
        return False

    async def addGuild(self, id: int, notificationChannelID : int=None, commandChannelID : int=None):
        result = await self._guildRepository.findByID(id)
        # Add guild if it does not exist
        if (not result):
            guild = GuildModel(id=id, notificationChannelID=notificationChannelID, commandChannelID=commandChannelID)
            return await self._guildRepository.save(guild)
        
        return False

    async def updateGuild (self, id: int, notificationChannelID : int = None, commandChannelID : int = None):
        result = await self._guildRepository.update(id=id, notificationChannelID=notificationChannelID, commandChannelID=commandChannelID)

        # check if guild exist, then create one if there is no guild
        if (not result):
            result = await self.addGuild(id=id, notificationChannelID=notificationChannelID, commandChannelID=commandChannelID)

        return result