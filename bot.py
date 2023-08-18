import responses
import globalInfos
import blueprints
import shapeViewer
import operationGraph
import discord
import json
import sys
import traceback

async def globalLogMessage(message:str) -> None:
    if globalInfos.GLOBAL_LOG_CHANNEL is None:
        print(message)
    else:
        logChannel = await client.fetch_channel(globalInfos.GLOBAL_LOG_CHANNEL)
        await logChannel.send(message)

async def globalLogError() -> None:
    await globalLogMessage(("".join(traceback.format_exception(*sys.exc_info())))[:-1])

async def useShapeViewer(userMessage:str,sendErrors:bool) -> tuple[bool,str,discord.File|None]:
    try:

        response = responses.handleResponse(userMessage)
        msgParts = []
        hasErrors = False
        file = None

        if response is None:
            if sendErrors:
                msgParts.append("No potential shape codes detected")

        else:
            response, hasInvalid, errorMsgs = response

            if hasInvalid:
                hasErrors = True
                if sendErrors:
                    msgParts.append("\n".join(f"- {msg}" for msg in errorMsgs))

            if response is not None:

                image, spoiler, resultingShapeCodes, viewer3dLinks = response
                file = discord.File(image,"shapes.png",spoiler=spoiler)
                if resultingShapeCodes is not None:
                    msgParts.append(" ".join(f"{{{code}}}" for code in resultingShapeCodes))
                if viewer3dLinks is not None:
                    msgParts.append("\n".join(viewer3dLinks))

        responseMsg = "\n\n".join(msgParts)
        if len(responseMsg) > globalInfos.MESSAGE_MAX_LENGTH:
            responseMsg = "Message too long"

        return hasErrors, responseMsg, file

    except Exception:
        await globalLogError()
        return True, globalInfos.UNKNOWN_ERROR_TEXT if sendErrors else "", None

def isDisabledInGuild(guildId:int|None) -> bool:

    if globalInfos.RESTRICT_TO_SERVERS is None:
        return False

    if guildId in globalInfos.RESTRICT_TO_SERVERS:
        return False

    return True

def isAllowedToRunOwnerCommand(interaction:discord.Interaction) -> bool:
    if interaction.user.id in globalInfos.OWNER_USERS:
        return True
    return False

async def isAllowedToRunAdminCommand(interaction:discord.Interaction) -> bool:

    guildId = interaction.guild_id
    if guildId is None:
        return False

    if isAllowedToRunOwnerCommand(interaction):
        return True

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

def exitCommandWithoutResponse(interaction:discord.Interaction) -> bool:

    if globalPaused:
        return True

    if isDisabledInGuild(interaction.guild_id):
        return True

    return False

async def setAllServerSettings(guildId:int,property:str,value) -> None:
    global canSaveSettings

    if allServerSettings.get(guildId) is None:
        allServerSettings[guildId] = {}
    allServerSettings[guildId][property] = value

    if canSaveSettings:
        canSaveSettings = False
        with open(globalInfos.ALL_SERVER_SETTINGS_PATH,"w") as f:
            json.dump(allServerSettings,f)
        canSaveSettings = True

async def getAllServerSettings(guildId:int,property:str):

    if (allServerSettings.get(guildId) is None) or (allServerSettings[guildId].get(property) is None):
        defaultValue = globalInfos.SERVER_SETTINGS_DEFAULTS.get(property)
        if type(defaultValue) in (list,dict):
            defaultValue = defaultValue.copy()
        await setAllServerSettings(guildId,property,defaultValue)

    return allServerSettings[guildId][property]

def isValidChannelId(channel:str) -> bool:
    try:
        channelInt = int(channel)
    except ValueError:
        return False
    if (channelInt < 0) or (len(channel) > globalInfos.CHANNEL_ID_LEN):
        return False
    return True

def isValidRoleId(role:str) -> bool:
    try:
        rolelInt = int(role)
    except ValueError:
        return False
    if (rolelInt < 0) or (len(role) > globalInfos.ROLE_ID_LEN):
        return False
    return True

async def isAllowedToUsePublicFeature(initiator:discord.Message|discord.Interaction) -> bool:

    initiatorType = {discord.Message:0,discord.Interaction:1}[type(initiator)]

    authorId = initiator.author.id if initiatorType == 0 else initiator.user.id
    if authorId in globalInfos.OWNER_USERS:
        return True

    if globalPaused:
        return False

    guildId = None if initiator.guild is None else initiator.guild.id

    if isDisabledInGuild(guildId):
        return False

    if guildId is None:
        return True

    userRoles = initiator.author.roles[1:] if initiatorType == 0 else initiator.user.roles
    adminRoles = await getAllServerSettings(guildId,"adminRoles")
    for role in userRoles:
        if role.id in adminRoles:
            return True

    if await getAllServerSettings(guildId,"paused"):
        return False

    channelId = initiator.channel.id
    if await getAllServerSettings(guildId,"restrictToChannel") not in (None,channelId):
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

async def doSendReaction(message:discord.Message) -> bool:

    if message.author.id in globalInfos.OWNER_USERS:
        return True

    if globalPaused:
        return False

    guildId = None if message.guild is None else message.guild.id

    if isDisabledInGuild(guildId):
        return False

    if guildId is None:
        return True

    if await getAllServerSettings(guildId,"paused"):
        return False

    return True

def runDiscordBot() -> None:

    global client
    client = discord.Client(intents=discord.Intents.all(),activity=discord.Game("shapez 2"))
    tree = discord.app_commands.CommandTree(client)

    @client.event
    async def on_ready() -> None:
        global allServerSettings, executedOnReady
        if not executedOnReady:

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

            shapeViewer.preRenderQuadrants()

            print(f"{client.user} is now running")
            executedOnReady = True

    @client.event
    async def on_message(message:discord.Message) -> None:

        messageAuthor = message.author
        if messageAuthor == client.user:
            return

        if globalInfos.BOT_ID in (user.id for user in message.mentions):
            if await doSendReaction(message):
                await message.add_reaction("\U0001F916")

        if await isAllowedToUsePublicFeature(message):
            hasErrors, responseMsg, file = await useShapeViewer(message.content,False)
            if hasErrors:
                await message.add_reaction(globalInfos.INVALID_SHAPE_CODE_REACTION)
            if (responseMsg != "") or (file is not None):
                await message.channel.send(responseMsg,**({} if file is None else {"file":file}))

    @tree.command(name="pause",description="Admin only, pauses the bot on this server")
    async def pauseCommand(interaction:discord.Interaction) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        if await isAllowedToRunAdminCommand(interaction):
            await setAllServerSettings(interaction.guild_id,"paused",True)
            responseMsg = "Bot is now paused on this server"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)

    @tree.command(name="unpause",description="Admin only, unpauses the bot on this server")
    async def unpauseCommand(interaction:discord.Interaction) -> None:
        if exitCommandWithoutResponse(interaction):
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
        if exitCommandWithoutResponse(interaction):
            return
        await interaction.response.send_message("Please wait...",ephemeral=True)
        ogMsg = await interaction.original_response()
        if len(message) > globalInfos.SEND_LOADING_GIF_FOR_NUM_CHARS_SHAPE_VIEWER:
            await ogMsg.edit(attachments=[discord.File(globalInfos.LOADING_GIF_PATH)])
        _, responseMsg, file = await useShapeViewer(message,True)
        await ogMsg.edit(content=responseMsg,**{"attachments":[] if file is None else [file]})

    @tree.command(name="change-blueprint-version",description="Change a blueprint's version")
    @discord.app_commands.describe(blueprint="The full blueprint code",version="The blueprint version number (current latest is 1022)")
    async def changeBlueprintVersionCommand(interaction:discord.Interaction,blueprint:str,version:int) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        try:
            responseMsg = f"```{blueprints.changeBlueprintVersion(blueprint,version)}```"
        except Exception as e:
            responseMsg = f"Error happened : {e}"
        await interaction.response.send_message(responseMsg,ephemeral=True)

    @tree.command(name="member-count",description="Display the number of members in this server")
    async def MemberCountCommand(interaction:discord.Interaction) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        def fillText(text:str,desiredLen:int,align:str) -> str:
            toFill = desiredLen - len(text)
            if align == "l":
                return text + (" "*toFill)
            elif align == "r":
                return (" "*toFill) + text
            else:
                num = int(toFill/2)
                return (" "*num) + text + (" "*(toFill-num))
        if interaction.guild is None:
            responseMsg = "Not in a server"
        else:
            guild = await client.fetch_guild(interaction.guild_id,with_counts=True)
            total = guild.approximate_member_count
            online = guild.approximate_presence_count
            offline = total - online
            totalTxt, onlineTxt, offlineTxt = "Total", "Online", "Offline"
            onlineProportion = online / total
            onlinePercent = round(onlineProportion*100)
            offlinePercent = 100-onlinePercent
            onlinePercent, offlinePercent = f"{onlinePercent}%", f"{offlinePercent}%"
            online, total, offline = [str(n) for n in (online,total,offline)]
            totalMaxLen = max(len(s) for s in (total,totalTxt))
            onlineMaxLen = max(len(s) for s in (online,onlinePercent,onlineTxt))
            offlineMaxLen = max(len(s) for s in (offline,offlinePercent,offlineTxt))
            numSpaces = 20
            totalLen = onlineMaxLen + numSpaces + totalMaxLen + numSpaces + offlineMaxLen
            spaces = " "*numSpaces
            filledProgressBar = round(onlineProportion*totalLen)
            lines = [
                f"{fillText(onlineTxt,onlineMaxLen,'l')}{spaces}{fillText(totalTxt,totalMaxLen,'c')}{spaces}{fillText(offlineTxt,offlineMaxLen,'r')}",
                f"{fillText(online,onlineMaxLen,'l')}{spaces}{fillText(total,totalMaxLen,'c')}{spaces}{fillText(offline,offlineMaxLen,'r')}",
                f"{fillText(onlinePercent,onlineMaxLen,'l')}{spaces}{' '*totalMaxLen}{spaces}{fillText(offlinePercent,offlineMaxLen,'r')}",
                f"{'#'*filledProgressBar}{'-'*(totalLen-filledProgressBar)}"
            ]
            responseMsg = "\n".join(lines)
            responseMsg = f"```{responseMsg}```"
        await interaction.response.send_message(responseMsg,ephemeral=True)

    @tree.command(name="operation-graph",description="See documentation on github")
    @discord.app_commands.describe(public="Wether to send the result publicly in the channel or only to you (errors are always sent privately)",
        see_shape_vars="Wether or not to send the shape codes that were affected to every shape variable")
    async def operationGraphCommand(interaction:discord.Interaction,instructions:str,public:bool=False,see_shape_vars:bool=False) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        await interaction.response.send_message("Please wait...",ephemeral=True)
        ogMsg = await interaction.original_response()
        if len(instructions) > globalInfos.SEND_LOADING_GIF_FOR_NUM_CHARS_OP_GRAPH:
            await ogMsg.edit(attachments=[discord.File(globalInfos.LOADING_GIF_PATH)])
        responseMsg = ""
        file = None
        hasErrors = False
        try:
            valid, instructionsOrError = operationGraph.getInstructionsFromText(instructions)
            if valid:
                valid, responseOrError = operationGraph.genOperationGraph(instructionsOrError,see_shape_vars)
                if valid:
                    image, shapeVarValues = responseOrError
                    file = discord.File(image,"graph.png")
                    if see_shape_vars:
                        responseMsg = "\n".join(f"- {k} : {{{v}}}" for k,v in shapeVarValues.items())
                else:
                    responseMsg = responseOrError
                    hasErrors = True
            else:
                responseMsg = instructionsOrError
                hasErrors = True
        except Exception:
            await globalLogError()
            responseMsg = globalInfos.UNKNOWN_ERROR_TEXT
            hasErrors = True
        if hasErrors or (not public):
            await ogMsg.edit(content=responseMsg,**{"attachments":[] if file is None else [file]})
        else:
            await ogMsg.delete()
            if await isAllowedToUsePublicFeature(interaction):
                await interaction.channel.send(responseMsg,file=file)

    @tree.command(name="restrict-to-channel",description="Admin only, restricts the use of the shape viewer in public messages to one channel only")
    @discord.app_commands.describe(channel="A channel id or 0 if you want to remove a previously set channel")
    async def restrictToChannelCommand(interaction:discord.Interaction,channel:str) -> None:
        if exitCommandWithoutResponse(interaction):
            return
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

    @tree.command(name="admin-roles-add",description="Admin only, adds a role to the admin roles list")
    @discord.app_commands.describe(role="A role id")
    async def adminRolesAddCommand(interaction:discord.Interaction,role:str) -> None:
        if exitCommandWithoutResponse(interaction):
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
        if exitCommandWithoutResponse(interaction):
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
        if exitCommandWithoutResponse(interaction):
            return
        if await isAllowedToRunAdminCommand(interaction):
            adminRolesList = await getAllServerSettings(interaction.guild_id,"adminRoles")
            if adminRolesList == []:
                responseMsg = "Empty list"
            else:
                responseMsg = "\n".join(f"- <@&{int(role)}> : {int(role)}" for role in adminRolesList)
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)

    @tree.command(name="restrict-to-roles-add",description="Admin only, adds a role to the restrict to roles list")
    @discord.app_commands.describe(role="A role id")
    async def restrictToRolesAddCommand(interaction:discord.Interaction,role:str) -> None:
        if exitCommandWithoutResponse(interaction):
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
        if exitCommandWithoutResponse(interaction):
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
        if exitCommandWithoutResponse(interaction):
            return
        if await isAllowedToRunAdminCommand(interaction):
            restrictToRolesList = await getAllServerSettings(interaction.guild_id,"restrictToRoles")
            if restrictToRolesList == []:
                responseMsg = "Empty list"
            else:
                responseMsg = "\n".join(f"- <@&{int(role)}> : {int(role)}" for role in restrictToRolesList)
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)

    @tree.command(name="restrict-to-roles-set-inverted",description="Admin only, sets if the restrict to roles list should be inverted")
    @discord.app_commands.describe(inverted="If True : only users who have at least one role that isn't part of the list will be able to use public message features, if False : only users who have at least one role that is part of the list will be able to use public message features")
    async def restrictToRolesSetInvertedCommand(interaction:discord.Interaction,inverted:bool) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        if await isAllowedToRunAdminCommand(interaction):
            await setAllServerSettings(interaction.guild_id,"restrictToRolesInverted",inverted)
            responseMsg = f"'restrictToRolesInverted' parameter has been set to {inverted}"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)

    with open(globalInfos.TOKEN_PATH) as f:
        token = f.read()
    client.run(token)

executedOnReady = False
globalPaused = False
canSaveSettings = True