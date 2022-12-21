from src.repository.guild_repository import GuildRespository
from src.models.guild_model import GuildModel

class GuildService:
    def __init__(self):
        self._guildRepository = GuildRespository()

    async def addGuild(self, id: int, notificationChannelID: int=None, roleID:int=None) -> bool:
        result = await self._guildRepository.findByID(id)

        # Guild exist
        if (result):
            return False

        # Create new guild
        guild = GuildModel(id=id, notificationChannelID=notificationChannelID, roleID=roleID)
        result_guild = await self._guildRepository.save(guild)
        
        return result_guild

    async def updateGuild (self, id: int, notificationChannelID:int = None, roleID:int = None) -> bool:
        result = await self._guildRepository.findByID(id)
        
        # check if guild exist, then create one if there is no guild
        if (result):
            return await self._guildRepository.update(id=id, notificationChannelID=notificationChannelID, roleID=roleID)
        else:
            return await self.addGuild(id=id, notificationChannelID=notificationChannelID, roleID=roleID)

    async def deleteGuild (self, id:int) -> bool:
        result = await self._guildRepository.findByID(id)

        if (result):
            return await self._guildRepository.delete(result)
        
        return False

    async def getServerSettings (self, id: int):
        result = await self._guildRepository.findByID(id=id)
        if (result):
            return {"notificationChannelID": result.notificationChannelID, "roleID": result.roleID}
        else:
            return None