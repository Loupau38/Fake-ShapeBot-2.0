import discord
import responses
import globalInfos
import blueprints
import json
async def globalLogMessage(message:str,client:discord.Client) -> None:
    if globalInfos.GLOBAL_LOG_CHANNEL is None:
        print(message)
    else:
        logChannel = await client.fetch_channel(globalInfos.GLOBAL_LOG_CHANNEL)
        await logChannel.send(message)
async def sendMessage(message:discord.message.Message,userMessage:str,client:discord.Client,guildId:int|None) -> None:
    try:
        response = responses.handleResponse(userMessage)
        if response is not None:
            response, hasInvalid, errorMsgs = response
            if hasInvalid:
                await message.add_reaction("\u2753")
            if response is not None:
                imagePath, spoiler = response
                await message.channel.send(file=discord.File(imagePath,"shapes.png",spoiler=spoiler))
    except Exception as e:
        await globalLogMessage(f"Exception happened : {e}",client)
def isAllowedToRunOwnerCommand(interaction:discord.Interaction) -> bool:
    if interaction.user.id in globalInfos.OWNER_USERS:
        return True
    return False
async def isAllowedToRunAdminCommand(interaction:discord.Interaction) -> bool:
    if isAllowedToRunOwnerCommand(interaction):
        return True
    guildId = interaction.guild_id
    if guildId is None:
        return False
    if interaction.user.guild_permissions.administrator:
        return True
    if allServerSettings.get(guildId) is None:
        return False
    userRoles = interaction.user.roles[1:]
    adminRoles = await getAllServerSettings(guildId,"adminRoles")
    for role in userRoles:
        if role.id in adminRoles:
            return True
    return False
async def setAllServerSettings(guildId:int,property:str,value) -> None:
    if allServerSettings.get(guildId) is None:
        allServerSettings[guildId] = {}
    allServerSettings[guildId][property] = value
    with open(globalInfos.ALL_SERVER_SETTINGS_PATH,"w") as f:
        json.dump(allServerSettings,f)
async def getAllServerSettings(guildId:int,property:str):
    if (allServerSettings.get(guildId) is None) or (allServerSettings[guildId].get(property) is None):
        defaultValue = globalInfos.SERVER_SETTINGS_DEFAULTS.get(property)
        if type(defaultValue) in (list,dict):
            defaultValue = defaultValue.copy()
        await setAllServerSettings(guildId,property,defaultValue)
    return allServerSettings[guildId][property]
def runDiscordBot() -> None:
    global client
    client = discord.Client(intents=discord.Intents.all())
    tree = discord.app_commands.CommandTree(client)
    @client.event
    async def on_ready() -> None:
        global allServerSettings
        await tree.sync()
        try:
            with open(globalInfos.ALL_SERVER_SETTINGS_PATH) as f:
                allServerSettings = json.load(f)
        except FileNotFoundError:
            allServerSettings = {}
            with open(globalInfos.ALL_SERVER_SETTINGS_PATH,"w") as f:
                json.dump(allServerSettings,f)
        newAllServerSettings = {}
        for k,v in allServerSettings.items():
            newAllServerSettings[int(k)] = v
        allServerSettings = newAllServerSettings
        print(f"{client.user} is now running")
    @client.event
    async def on_message(message:discord.message.Message) -> None:
        messageAuthor = message.author
        if messageAuthor == client.user:
            return
        async def doSendMessage(message:discord.Message) -> bool:
            if message.author.id in globalInfos.OWNER_USERS:
                return True
            if globalPaused:
                return False
            if message.guild is None:
                return True
            guildId = message.guild.id
            userRoles = message.author.roles[1:]
            adminRoles = await getAllServerSettings(guildId,"adminRoles")
            for role in userRoles:
                if role.id in adminRoles:
                    return True
            if await getAllServerSettings(guildId,"paused"):
                return False
            if await getAllServerSettings(guildId,"restrictToChannel") not in (None,message.channel.id):
                return False
            restrictToRoles = await getAllServerSettings(guildId,"restrictToRoles")
            if restrictToRoles == []:
                return True
            restrictToRolesInverted = await getAllServerSettings(guildId,"restrictToRolesInverted")
            for role in userRoles:
                roleInRestrictToRoles = role.id in restrictToRoles
                if restrictToRolesInverted and (not roleInRestrictToRoles):
                    return True
                if (not restrictToRolesInverted) and roleInRestrictToRoles:
                    return True
            return False
        userMessage = str(message.content)
        if message.guild is None:
            guildId = None
        else:
            guildId = message.guild.id
        if globalInfos.BOT_ID in (user.id for user in message.mentions):
            doSendReaction = False
            if message.author.id in globalInfos.OWNER_USERS:
                doSendReaction = True
            elif not globalPaused:
                if guildId is None:
                    doSendReaction = True
                elif (not await getAllServerSettings(guildId,"paused")):
                    doSendReaction = True
            if doSendReaction:
                await message.add_reaction("\U0001F916")
        if await doSendMessage(message):
            await sendMessage(message,userMessage,client,guildId)
    @tree.command(name="pause",description="Admin only, pauses the bot on this server")
    async def pauseCommand(interaction:discord.Interaction) -> None:
        if globalPaused:
            return
        if await isAllowedToRunAdminCommand(interaction):
            await setAllServerSettings(interaction.guild_id,"paused",True)
            responseMsg = "Bot is now paused on this server"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
    @tree.command(name="unpause",description="Admin only, unpauses the bot on this server")
    async def unpauseCommand(interaction:discord.Interaction) -> None:
        if globalPaused:
            return
        if await isAllowedToRunAdminCommand(interaction):
            await setAllServerSettings(interaction.guild_id,"paused",False)
            responseMsg = "Bot is now unpaused on this server"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
    @tree.command(name="stop",description="Owner only, stops the bot")
    async def stopCommand(interaction:discord.Interaction) -> None:
        allowedToStop = isAllowedToRunOwnerCommand(interaction)
        if allowedToStop:
            responseMsg = "Stopping bot"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
        if allowedToStop:
            await client.close()
    @tree.command(name="global-pause",description="Owner only, globally pauses the bot")
    async def globalPauseCommand(interaction:discord.Interaction) -> None:
        global globalPaused
        if isAllowedToRunOwnerCommand(interaction):
            globalPaused = True
            responseMsg = "Bot is now globally paused"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
    @tree.command(name="global-unpause",description="Owner only, globally unpauses the bot")
    async def globalUnpauseCommand(interaction:discord.Interaction) -> None:
        global globalPaused
        if isAllowedToRunOwnerCommand(interaction):
            globalPaused = False
            responseMsg = "Bot is now globally unpaused"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
    @tree.command(name="view-shapes",description="View shapes, useful if the bot says a shape code is invalid and you want to know why")
    @discord.app_commands.describe(message="The message like you would normally send it")
    async def viewShapesCommand(interaction:discord.Interaction,message:str) -> None:
        if globalPaused:
            return
        try:
            response = responses.handleResponse(message)
            if response is None:
                await interaction.response.send_message("No potential shape codes detected",ephemeral=True)
            else:
                response, hasInvalid, errorMsgs = response
                if hasInvalid:
                    await interaction.response.send_message(", ".join(errorMsgs),ephemeral=True)
                else:
                    imagePath, spoiler = response
                    await interaction.response.send_message(
                        ", ".join(errorMsgs),
                        file=discord.File(imagePath,"shapes.png",spoiler=spoiler),ephemeral=True)
        except Exception as e:
            await globalLogMessage(f"Exception happened : {e}",client)
    @tree.command(name="restrict-to-channel",description="Admin only, restricts the use of the shape viewer in public messages to one channel only")
    @discord.app_commands.describe(channel="A channel id or 0 if you want to remove a previously set channel")
    async def restrictToChannelCommand(interaction:discord.Interaction,channel:str) -> None:
        if globalPaused:
            return
        def isValidChannelId(channel:str) -> bool:
            try:
                channelInt = int(channel)
            except ValueError:
                return False
            if (channelInt < 0) or (len(channel) > globalInfos.CHANNEL_ID_LEN):
                return False
            return True
        if await isAllowedToRunAdminCommand(interaction):
            if isValidChannelId(channel):
                if int(channel) == 0:
                    await setAllServerSettings(interaction.guild_id,"restrictToChannel",None)
                    responseMsg = "'restrictToChannel' parameter cleared"
                else:
                    await setAllServerSettings(interaction.guild_id,"restrictToChannel",int(channel))
                    responseMsg = f"'restrictToChannel' parameter set to <#{channel}>"
            else:
                responseMsg = "Not a valid channel id"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
    def isValidRoleId(role:str) -> bool:
        try:
            rolelInt = int(role)
        except ValueError:
            return False
        if (rolelInt < 0) or (len(role) > globalInfos.ROLE_ID_LEN):
            return False
        return True
    @tree.command(name="admin-roles-add",description="Admin only, adds a role to the admin roles list")
    @discord.app_commands.describe(role="A role id")
    async def adminRolesAddCommand(interaction:discord.Interaction,role:str) -> None:
        if globalPaused:
            return
        if await isAllowedToRunAdminCommand(interaction):
            if isValidRoleId(role):
                roleInt = int(role)
                adminRolesList = await getAllServerSettings(interaction.guild_id,"adminRoles")
                if len(adminRolesList) >= globalInfos.MAX_ROLES_PER_LIST:
                    responseMsg = f"Can't have more than {globalInfos.MAX_ROLES_PER_LIST} roles per list"
                else:
                    if roleInt in adminRolesList:
                        responseMsg = f"<@&{roleInt}> is already in the list"
                    else:
                        adminRolesList.append(roleInt)
                        await setAllServerSettings(interaction.guild_id,"adminRoles",adminRolesList)
                        responseMsg = f"Added <@&{roleInt}> to the admin roles list"
            else:
                responseMsg = "Not a valid role id"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
    @tree.command(name="admin-roles-remove",description="Admin only, removes a role from the admin roles list")
    @discord.app_commands.describe(role="A role id")
    async def adminRolesRemoveCommand(interaction:discord.Interaction,role:str) -> None:
        if globalPaused:
            return
        if await isAllowedToRunAdminCommand(interaction):
            if isValidRoleId(role):
                roleInt = int(role)
                adminRolesList = await getAllServerSettings(interaction.guild_id,"adminRoles")
                if roleInt in adminRolesList:
                    adminRolesList.remove(roleInt)
                    await setAllServerSettings(interaction.guild_id,"adminRoles",adminRolesList)
                    responseMsg = f"Removed <@&{roleInt}> from the admin roles list"
                else:
                    responseMsg = "Role is not present in the list"
            else:
                responseMsg = "Not a valid role id"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
    @tree.command(name="admin-roles-view",description="Admin only, see the list of admin roles")
    async def adminRolesViewCommand(interaction:discord.Interaction) -> None:
        if globalPaused:
            return
        if await isAllowedToRunAdminCommand(interaction):
            adminRolesList = await getAllServerSettings(interaction.guild_id,"adminRoles")
            if adminRolesList == []:
                responseMsg = "Empty list"
            else:
                responseMsg = "\n".join(f"<@&{int(role)}> : {int(role)}" for role in adminRolesList)
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
    @tree.command(name="restrict-to-roles-add",description="Admin only, adds a role to the restrict to roles list")
    @discord.app_commands.describe(role="A role id")
    async def restrictToRolesAddCommand(interaction:discord.Interaction,role:str) -> None:
        if globalPaused:
            return
        if await isAllowedToRunAdminCommand(interaction):
            if isValidRoleId(role):
                roleInt = int(role)
                restrictToRolesList = await getAllServerSettings(interaction.guild_id,"restrictToRoles")
                if len(restrictToRolesList) >= globalInfos.MAX_ROLES_PER_LIST:
                    responseMsg = f"Can't have more than {globalInfos.MAX_ROLES_PER_LIST} roles per list"
                else:
                    if roleInt in restrictToRolesList:
                        responseMsg = f"<@&{roleInt}> is already in the list"
                    else:
                        restrictToRolesList.append(roleInt)
                        await setAllServerSettings(interaction.guild_id,"restrictToRoles",restrictToRolesList)
                        responseMsg = f"Added <@&{roleInt}> to the restrict to roles list"
            else:
                responseMsg = "Not a valid role id"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
    @tree.command(name="restrict-to-roles-remove",description="Admin only, removes a role from the restrict to roles list")
    @discord.app_commands.describe(role="A role id")
    async def restrictToRolesRemoveCommand(interaction:discord.Interaction,role:str) -> None:
        if globalPaused:
            return
        if await isAllowedToRunAdminCommand(interaction):
            if isValidRoleId(role):
                roleInt = int(role)
                restrictToRolesList = await getAllServerSettings(interaction.guild_id,"restrictToRoles")
                if roleInt in restrictToRolesList:
                    restrictToRolesList.remove(roleInt)
                    await setAllServerSettings(interaction.guild_id,"restrictToRoles",restrictToRolesList)
                    responseMsg = f"Removed <@&{roleInt}> from the restrict to roles list"
                else:
                    responseMsg = "Role is not present in the list"
            else:
                responseMsg = "Not a valid role id"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
    @tree.command(name="restrict-to-roles-view",description="Admin only, see the list of restrict to roles")
    async def restrictToRolesViewCommand(interaction:discord.Interaction) -> None:
        if globalPaused:
            return
        if await isAllowedToRunAdminCommand(interaction):
            restrictToRolesList = await getAllServerSettings(interaction.guild_id,"restrictToRoles")
            if restrictToRolesList == []:
                responseMsg = "Empty list"
            else:
                responseMsg = "\n".join(f"<@&{int(role)}> : {int(role)}" for role in restrictToRolesList)
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
    @tree.command(name="restrict-to-roles-set-inverted",description="Admin only, sets if the restrict to roles list should be inverted")
    @discord.app_commands.describe(inverted="If True : only users who have at least one role that isn't part of the list will be able to use public message features, if False : only users who have at least one role that is part of the list will be able to use public message features")
    async def restrictToRolesSetInvertedCommand(interaction:discord.Interaction,inverted:bool) -> None:
        if globalPaused:
            return
        if await isAllowedToRunAdminCommand(interaction):
            await setAllServerSettings(interaction.guild_id,"restrictToRolesInverted",inverted)
            responseMsg = f"'restrictToRolesInverted' parameter has been set to {inverted}"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)
    @tree.command(name="change-blueprint-version",description="Change a blueprint's version")
    @discord.app_commands.describe(blueprint="The full blueprint code",version="The blueprint version number (current latest is 1019)")
    async def changeBlueprintVersionCommand(interaction:discord.Interaction,blueprint:str,version:int) -> None:
        if globalPaused:
            return
        try:
            responseMsg = f"```{blueprints.changeBlueprintVersion(blueprint,version)}```"
        except Exception as e:
            responseMsg = f"Exception happened : {e}"
        await interaction.response.send_message(responseMsg,ephemeral=True)
    with open(globalInfos.TOKEN_PATH) as f:
        token = f.read()
    client.run(token)
globalPaused = False