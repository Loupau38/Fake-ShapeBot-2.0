import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = ""
del os

import responses
import globalInfos
import blueprints
import shapeViewer
import operationGraph
import utils
import gameInfos
import researchViewer
import guildSettings

import discord
import json
import sys
import traceback
import io
import typing

async def globalLogMessage(message:str) -> None:
    if globalInfos.GLOBAL_LOG_CHANNEL is None:
        print(message)
    else:
        logChannel = client.get_channel(globalInfos.GLOBAL_LOG_CHANNEL)
        await logChannel.send(message)

async def globalLogError() -> None:
    await globalLogMessage(("".join(traceback.format_exception(*sys.exc_info())))[:-1])

async def useShapeViewer(userMessage:str,sendErrors:bool) -> tuple[bool,str,tuple[discord.File,int]|None]:
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

                (image, imageSize), spoiler, resultingShapeCodes, viewer3dLinks = response
                file = discord.File(image,"shapes.png",spoiler=spoiler)
                if resultingShapeCodes is not None:
                    msgParts.append(" ".join(f"{{{code}}}" for code in resultingShapeCodes))
                if viewer3dLinks is not None:
                    msgParts.append("\n".join(viewer3dLinks))

        responseMsg = "\n\n".join(msgParts)
        if len(responseMsg) > globalInfos.MESSAGE_MAX_LENGTH:
            responseMsg = globalInfos.MESSAGE_TOO_LONG_TEXT

        return hasErrors, responseMsg, (None if file is None else (file, imageSize))

    except Exception:
        await globalLogError()
        return True, globalInfos.UNKNOWN_ERROR_TEXT if sendErrors else "", None

def isDisabledInGuild(guildId:int|None) -> bool:

    if globalInfos.RESTRICT_TO_SERVERS is None:
        return False

    if guildId in globalInfos.RESTRICT_TO_SERVERS:
        return False

    return True

def exitCommandWithoutResponse(interaction:discord.Interaction) -> bool:

    if globalPaused:
        return True

    if isDisabledInGuild(interaction.guild_id):
        return True

    return False

class PermissionLvls:

    PUBLIC_FEATURE = 0
    REACTION = 1
    PRIVATE_FEATURE = 2
    ADMIN = 3
    OWNER = 4

async def hasPermission(requestedLvl:int,*,message:discord.Message|None=None,interaction:discord.Interaction|None=None) -> bool:

    if message is not None:

        userId = message.author.id
        channelId = message.channel.id
        if message.guild is None:
            guildId = None
        else:
            guildId = message.guild.id
            userRoles = message.author.roles[1:]
            adminPerm = message.author.guild_permissions.administrator

    elif interaction is not None:

        userId = interaction.user.id
        channelId = interaction.channel_id
        guildId = interaction.guild_id
        if interaction.guild is not None:
            userRoles = interaction.user.roles[1:]
            adminPerm = interaction.user.guild_permissions.administrator

    else:
        raise ValueError("No message or interaction in 'hasPermission' function")

    if (guildId is None) and (requestedLvl == PermissionLvls.ADMIN):
        return False

    if userId in globalInfos.OWNER_USERS:
        return True
    else:
        if requestedLvl == PermissionLvls.OWNER:
            return False

    if globalPaused:
        return False

    if isDisabledInGuild(guildId):
        return False

    if guildId is None:
        return requestedLvl < PermissionLvls.ADMIN

    curGuildSettings = await guildSettings.getGuildSettings(guildId)

    if adminPerm:
        isAdmin = True
    else:
        isAdmin = False
        adminRoles = curGuildSettings["adminRoles"]
        for role in userRoles:
            if role.id in adminRoles:
                isAdmin = True
                break
    if isAdmin:
        if requestedLvl <= PermissionLvls.ADMIN:
            return True
    else:
        if requestedLvl == PermissionLvls.ADMIN:
            return False

    if requestedLvl == PermissionLvls.PRIVATE_FEATURE:
        return True

    if curGuildSettings["paused"]:
        return False

    if requestedLvl == PermissionLvls.REACTION:
        return True

    # requestedLvl = public feature

    if curGuildSettings["restrictToChannel"] not in (None,channelId):
        return False

    restrictToRoles = curGuildSettings["restrictToRoles"]
    if restrictToRoles == []:
        return True

    restrictToRolesInverted = curGuildSettings["restrictToRolesInverted"]
    for role in userRoles:
        roleInRestrictToRoles = role.id in restrictToRoles
        if restrictToRolesInverted and (not roleInRestrictToRoles):
            return True
        if (not restrictToRolesInverted) and roleInRestrictToRoles:
            return True

    return False

def msgToFile(msg:str,filename:str,guild:discord.Guild|None) -> discord.File|None:
    msgBytes = msg.encode()
    if isFileTooBig(len(msgBytes),guild):
        return None
    return discord.File(io.BytesIO(msgBytes),filename)

async def decodeAttachment(file:discord.Attachment) -> str|None:
    try:
        fileBytes = await file.read()
        fileStr = fileBytes.decode()
    except Exception:
        return None
    return fileStr

def isFileTooBig(fileSize:int,guild:discord.Guild|None) -> bool:
    if guild is None:
        return fileSize > globalInfos.DEFAULT_MAX_FILE_SIZE
    return fileSize > guild.filesize_limit

def detectBPVersion(potentialBPCodes:list[str]) -> list[str|int]|None:

    versions = []

    for bp in potentialBPCodes:

        try:
            version = blueprints.getBlueprintVersion(bp)
        except blueprints.BlueprintError:
            continue

        versionReaction = gameInfos.versions.versionNumToReactions(version)

        if versionReaction is None:
            continue

        versions.append(versionReaction)

    if len(versions) != 1:
        return None

    return versions[0]

def safenString(string:str) -> str:
    return discord.utils.escape_mentions(string)

##################################################

def runDiscordBot() -> None:

    global client, msgCommandMessages

    client = discord.Client(intents=discord.Intents.all(),activity=discord.Game("shapez 2"))
    tree = discord.app_commands.CommandTree(client)

    shapeViewer.preRenderQuadrants()

    with open(globalInfos.MSG_COMMAND_MESSAGES_PATH,encoding="utf-8") as f:
        msgCommandMessages = json.load(f)

    @client.event
    async def on_ready() -> None:
        global executedOnReady
        if not executedOnReady:
            await tree.sync()
            print(f"{client.user} is now running")
            executedOnReady = True

    @client.event
    async def on_message(message:discord.Message) -> None:

        if message.author == client.user:
            return

        if await hasPermission(PermissionLvls.PUBLIC_FEATURE,message=message):
            hasErrors, responseMsg, file = await useShapeViewer(message.content,False)
            if hasErrors:
                await message.add_reaction(globalInfos.INVALID_SHAPE_CODE_REACTION)
            if (responseMsg != "") or (file is not None):
                if file is not None:
                    file, fileSize = file
                    if isFileTooBig(fileSize,message.guild):
                        file = discord.File(globalInfos.IMAGE_FILE_TOO_BIG_PATH)
                responseMsg = safenString(responseMsg)
                await message.channel.send(responseMsg,**({} if file is None else {"file":file}))

        if await hasPermission(PermissionLvls.REACTION,message=message):

            if globalInfos.BOT_ID in (user.id for user in message.mentions):
                await message.add_reaction(globalInfos.BOT_MENTIONED_REACTION)

            msgContent = message.content
            for file in message.attachments:
                fileContent = await decodeAttachment(file)
                if fileContent is None:
                    continue
                msgContent += fileContent

            bpReactions = detectBPVersion(blueprints.getPotentialBPCodesInString(msgContent))
            if bpReactions is not None:
                for reaction in bpReactions:
                    if type(reaction) == int:
                        reaction = client.get_emoji(reaction)
                    await message.add_reaction(reaction)

    class RegisterCommandType:
        SINGLE_CHANNEL = "singleChannel"
        ROLE_LIST = "roleList"

    def registerAdminCommand(type_:str,cmdName:str,guildSettingsKey:str,cmdDesc:str="") -> None:

        if type_ == RegisterCommandType.SINGLE_CHANNEL:

            @tree.command(name=cmdName,description=cmdDesc)
            @discord.app_commands.describe(channel="The channel. Don't provide this parameter to clear it")
            async def generatedCommand(interaction:discord.Interaction,channel:discord.TextChannel|discord.Thread|None=None) -> None:
                if exitCommandWithoutResponse(interaction):
                    return
                if await hasPermission(PermissionLvls.ADMIN,interaction=interaction):
                    if channel is None:
                        setParamTo = None
                        responseMsgEnd = "cleared"
                    else:
                        setParamTo = channel.id
                        responseMsgEnd = f"set to {channel.mention}"
                    await guildSettings.setGuildSetting(interaction.guild_id,guildSettingsKey,setParamTo)
                    responseMsg = f"'{guildSettingsKey}' parameter {responseMsgEnd}"
                else:
                    responseMsg = globalInfos.NO_PERMISSION_TEXT
                await interaction.response.send_message(responseMsg,ephemeral=True)

        elif type_ == RegisterCommandType.ROLE_LIST:

            @tree.command(name=cmdName,description=f"{globalInfos.ADMIN_ONLY_BADGE} modifys the '{guildSettingsKey}' list")
            @discord.app_commands.describe(role="Only provide this if using 'add' or 'remove' subcommand")
            async def generatedCommand(interaction:discord.Interaction,
                operation:typing.Literal["add","remove","view","clear"],role:discord.Role|None=None) -> None:
                if exitCommandWithoutResponse(interaction):
                    return
                if await hasPermission(PermissionLvls.ADMIN,interaction=interaction):

                    roleList = (await guildSettings.getGuildSettings(interaction.guild_id))[guildSettingsKey]

                    if (operation in ("add","remove")) and (role is None):
                        responseMsg = "A role must be provided when using the 'add' or 'remove' subcommand"

                    elif operation == "add":

                        if len(roleList) >= globalInfos.MAX_ROLES_PER_LIST:
                            responseMsg = f"Can't have more than {globalInfos.MAX_ROLES_PER_LIST} roles per list"
                        else:
                            if role.id in roleList:
                                responseMsg = f"{role.mention} is already in the list"
                            else:
                                roleList.append(role.id)
                                await guildSettings.setGuildSetting(interaction.guild_id,guildSettingsKey,roleList)
                                responseMsg = f"Added {role.mention} to the '{guildSettingsKey}' list"

                    elif operation == "remove":

                        if role.id in roleList:
                            roleList.remove(role.id)
                            await guildSettings.setGuildSetting(interaction.guild_id,guildSettingsKey,roleList)
                            responseMsg = f"Removed {role.mention} from the '{guildSettingsKey}' list"
                        else:
                            responseMsg = "Role is not present in the list"

                    elif operation == "view":

                        roleList = [interaction.guild.get_role(r) for r in roleList]
                        if roleList== []:
                            responseMsg = "Empty list"
                        else:
                            responseMsg = "\n".join(f"- {role.mention} : {role.id}" for role in roleList)

                    elif operation == "clear":

                        await guildSettings.setGuildSetting(interaction.guild_id,guildSettingsKey,[])
                        responseMsg = f"'{guildSettingsKey}' list cleared"

                    else:
                        responseMsg = "Unknown operation"
                else:
                    responseMsg = globalInfos.NO_PERMISSION_TEXT
                await interaction.response.send_message(responseMsg,ephemeral=True)

        else:
            print(f"Unknown type : '{type_}' in 'registerAdminCommand' function")

    @tree.command(name="stop",description=f"{globalInfos.OWNER_ONLY_BADGE} stops the bot")
    async def stopCommand(interaction:discord.Interaction) -> None:
        if await hasPermission(PermissionLvls.OWNER,interaction=interaction):
            try:
                await interaction.response.send_message("Stopping bot",ephemeral=True)
            except Exception:
                print("Error while attempting to comfirm bot stopping")
            await client.close()
        else:
            await interaction.response.send_message(globalInfos.NO_PERMISSION_TEXT,ephemeral=True)

    @tree.command(name="global-pause",description=f"{globalInfos.OWNER_ONLY_BADGE} globally pauses the bot")
    async def globalPauseCommand(interaction:discord.Interaction) -> None:
        global globalPaused
        if await hasPermission(PermissionLvls.OWNER,interaction=interaction):
            globalPaused = True
            responseMsg = "Bot is now globally paused"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)

    @tree.command(name="global-unpause",description=f"{globalInfos.OWNER_ONLY_BADGE} globally unpauses the bot")
    async def globalUnpauseCommand(interaction:discord.Interaction) -> None:
        global globalPaused
        if await hasPermission(PermissionLvls.OWNER,interaction=interaction):
            globalPaused = False
            responseMsg = "Bot is now globally unpaused"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)

    @tree.command(name="pause",description=f"{globalInfos.ADMIN_ONLY_BADGE} pauses the bot on this server")
    async def pauseCommand(interaction:discord.Interaction) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        if await hasPermission(PermissionLvls.ADMIN,interaction=interaction):
            await guildSettings.setGuildSetting(interaction.guild_id,"paused",True)
            responseMsg = "Bot is now paused on this server"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)

    @tree.command(name="unpause",description=f"{globalInfos.ADMIN_ONLY_BADGE} unpauses the bot on this server")
    async def unpauseCommand(interaction:discord.Interaction) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        if await hasPermission(PermissionLvls.ADMIN,interaction=interaction):
            await guildSettings.setGuildSetting(interaction.guild_id,"paused",False)
            responseMsg = "Bot is now unpaused on this server"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)

    registerAdminCommand(RegisterCommandType.SINGLE_CHANNEL,
        "restrict-to-channel",
        "restrictToChannel",
        f"{globalInfos.ADMIN_ONLY_BADGE} restricts the use of the bot in public messages to one channel only")

    registerAdminCommand(RegisterCommandType.ROLE_LIST,"admin-roles","adminRoles")

    registerAdminCommand(RegisterCommandType.ROLE_LIST,"restrict-to-roles","restrictToRoles")

    @tree.command(name="restrict-to-roles-set-inverted",description=f"{globalInfos.ADMIN_ONLY_BADGE} sets if the restrict to roles list should be inverted")
    @discord.app_commands.describe(inverted="If True : only users who have at least one role that isn't part of the list will be able to use public message features, if False : only users who have at least one role that is part of the list will be able to use public message features")
    async def restrictToRolesSetInvertedCommand(interaction:discord.Interaction,inverted:bool) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        if await hasPermission(PermissionLvls.ADMIN,interaction=interaction):
            await guildSettings.setGuildSetting(interaction.guild_id,"restrictToRolesInverted",inverted)
            responseMsg = f"'restrictToRolesInverted' parameter has been set to {inverted}"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)

    @tree.command(name="view-shapes",description="View shapes, useful if the bot says a shape code is invalid and you want to know why")
    @discord.app_commands.describe(message="The message like you would normally send it")
    async def viewShapesCommand(interaction:discord.Interaction,message:str) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        await interaction.response.defer(ephemeral=True)
        if await hasPermission(PermissionLvls.PRIVATE_FEATURE,interaction=interaction):
            _, responseMsg, file = await useShapeViewer(message,True)
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
            file = None
        kwargs = {}
        if file is not None:
            file, fileSize = file
            if isFileTooBig(fileSize,interaction.guild):
                file = discord.File(globalInfos.IMAGE_FILE_TOO_BIG_PATH)
            kwargs["file"] = file
        await interaction.followup.send(responseMsg,**kwargs)

    @tree.command(name="change-blueprint-version",description="Change a blueprint's version")
    @discord.app_commands.describe(blueprint="The full blueprint code",
        version="The blueprint version number (latest public : {}, latest patreon only : {})".format(*gameInfos.versions.LATEST_GAME_VERSIONS),
        blueprint_file="A file containing a blueprint code if it's too big to paste it directly (fill in the 'blueprint' parameter with dummy character(s))")
    async def changeBlueprintVersionCommand(interaction:discord.Interaction,blueprint:str,version:int,blueprint_file:discord.Attachment|None=None) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        if await hasPermission(PermissionLvls.PRIVATE_FEATURE,interaction=interaction):
            if blueprint_file is None:
                toProcessBlueprint = blueprint
            else:
                toProcessBlueprint = await decodeAttachment(blueprint_file)
            if toProcessBlueprint is None:
                responseMsg = "Error while processing file"
            else:
                try:
                    responseMsg = blueprints.changeBlueprintVersion(toProcessBlueprint,version)
                except blueprints.BlueprintError as e:
                    responseMsg = f"Error happened : {e}"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        if len(responseMsg)+6 > globalInfos.MESSAGE_MAX_LENGTH:
            file = msgToFile(responseMsg,"blueprint.txt",interaction.guild)
            if file is None:
                kwargs = {"content" : "Response too big"}
            else:
                kwargs = {"file" : file}
        else:
            kwargs = {"content" : f"```{responseMsg}```"}
        await interaction.response.send_message(ephemeral=True,**kwargs)

    @tree.command(name="member-count",description="Display the number of members in this server")
    async def MemberCountCommand(interaction:discord.Interaction) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        def fillText(text:str,desiredLen:int,align:str) -> str:
            if align == "l":
                return text.ljust(desiredLen)
            if align == "r":
                return text.rjust(desiredLen)
            return text.center(desiredLen)
        if await hasPermission(PermissionLvls.PRIVATE_FEATURE,interaction=interaction):
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
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        await interaction.response.send_message(responseMsg,ephemeral=True)

    @tree.command(name="operation-graph",description="See documentation on github")
    @discord.app_commands.describe(public="Errors will be sent publicly if this is True! Sets if the result is sent publicly in the channel",
        see_shape_vars="Wether or not to send the shape codes that were affected to every shape variable")
    async def operationGraphCommand(interaction:discord.Interaction,instructions:str,public:bool=False,see_shape_vars:bool=False) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        file = None
        hasErrors = False # unused but kept just in case
        if await hasPermission(PermissionLvls.PUBLIC_FEATURE if public else PermissionLvls.PRIVATE_FEATURE,interaction=interaction):
            await interaction.response.defer(ephemeral=not public)
            try:
                valid, instructionsOrError = operationGraph.getInstructionsFromText(instructions)
                if valid:
                    valid, responseOrError = operationGraph.genOperationGraph(instructionsOrError,see_shape_vars)
                    if valid:
                        (image, imageSize), shapeVarValues = responseOrError
                        file = discord.File(image,"graph.png")
                        if see_shape_vars:
                            responseMsg = "\n".join(f"- {k} : {{{v}}}" for k,v in shapeVarValues.items())
                        else:
                            responseMsg = ""
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
        else:
            await interaction.response.defer(ephemeral=True)
            responseMsg = globalInfos.NO_PERMISSION_TEXT
            hasErrors = True
        responseMsg = utils.handleMsgTooLong(responseMsg.render(public) if type(responseMsg) == utils.OutputString else responseMsg)
        kwargs = {}
        if file is not None:
            if isFileTooBig(imageSize,interaction.guild):
                file = discord.File(globalInfos.IMAGE_FILE_TOO_BIG_PATH)
            kwargs["file"] = file
        if public:
            responseMsg = safenString(responseMsg)
        await interaction.followup.send(responseMsg,**kwargs)

    @tree.command(name="blueprint-info",description="Get a blueprint's version, building count and size")
    @discord.app_commands.describe(blueprint="The full blueprint code",
        blueprint_file="A file containing a blueprint code if it's too big to paste it directly (fill in the 'blueprint' parameter with dummy character(s))")
    async def blueprintInfoCommand(interaction:discord.Interaction,blueprint:str,advanced:bool=False,blueprint_file:discord.Attachment|None=None) -> None:

        def formatCounts(bp:blueprints.BuildingBlueprint|blueprints.IslandBlueprint|None,name:str) -> str:
            output = f"\n**{name} counts :**\n"
            if bp is None:
                output += "None"
            else:
                if type(bp) == blueprints.BuildingBlueprint:
                    counts = bp.getBuildingCounts()
                    lines = []
                    for v,ivc in gameInfos.buildings.getCategorizedBuildingCounts(counts).items():
                        lines.append(f"- `{gameInfos.buildings.allVariantLists[v].title}` : `{utils.sepInGroupsNumber(sum(sum(iv.values()) for iv in ivc.values()))}`")
                        for iv,bc in ivc.items():
                            lines.append(f"  - `{gameInfos.buildings.allInternalVariantLists[iv].title}` : `{utils.sepInGroupsNumber(sum(bc.values()))}`")
                            for b,c in bc.items():
                                lines.append(f"    - `{b}` : `{utils.sepInGroupsNumber(c)}`")
                    output += "\n".join(lines)
                else:
                    counts = bp.getIslandCounts()
                    output += "\n".join(f"- `{k}` : `{utils.sepInGroupsNumber(v)}`" for k,v in counts.items())
            return output

        if exitCommandWithoutResponse(interaction):
            return

        if await hasPermission(PermissionLvls.PRIVATE_FEATURE,interaction=interaction):

            if blueprint_file is None:
                toProcessBlueprint = blueprint
            else:
                toProcessBlueprint = await decodeAttachment(blueprint_file)
            if toProcessBlueprint is None:
                responseMsg = "Error while processing file"

            else:
                try:

                    bp = blueprints.decodeBlueprint(toProcessBlueprint)

                    versionTxt = gameInfos.versions.versionNumToText(bp.version,advanced)
                    if versionTxt is None:
                        versionTxt = "Unknown"
                    elif advanced:
                        versionTxt = f"[{', '.join(f'`{txt}`' for txt in versionTxt)}]"
                    else:
                        versionTxt = f"`{versionTxt}`"

                    responseParts = [
                        f"Version : `{bp.version}` / {versionTxt}",
                        f"Blueprint type : `{bp.type}`"
                    ]

                    sizes = []

                    if bp.buildingBP is not None:
                        buildingCount = bp.buildingBP.getBuildingCount()
                        buildingSize = bp.buildingBP.getSize()
                        sizes.append(f"Building size : `{buildingSize.width}`x`{buildingSize.height}`x`{buildingSize.depth}`")
                        responseParts.append(f"Building count : `{utils.sepInGroupsNumber(buildingCount)}`")

                    if bp.islandBP is not None:
                        islandCount = bp.islandBP.getIslandCount()
                        islandSize = bp.islandBP.getSize()
                        sizes.append(f"Island size : `{islandSize.width}`x`{islandSize.height}`")
                        responseParts.append(f"Island count : `{utils.sepInGroupsNumber(islandCount)}`")

                    responseParts.extend(sizes)
                    responseMsg = ", ".join(responseParts)

                    if advanced:
                        responseMsg += formatCounts(bp.buildingBP,"Buildings")
                        responseMsg += formatCounts(bp.islandBP,"Islands")

                except blueprints.BlueprintError as e:
                    responseMsg = f"Error happened : {e}"
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT

        if len(responseMsg) > globalInfos.MESSAGE_MAX_LENGTH:
            file = msgToFile(responseMsg,"infos.txt",interaction.guild)
            if file is None:
                kwargs = {"content" : "Response too big"}
            else:
                kwargs = {"file" : file}
        else:
            kwargs = {"content" : responseMsg}

        await interaction.response.send_message(ephemeral=True,**kwargs)

    @tree.command(name="research-viewer",description="View the research tree")
    @discord.app_commands.describe(
        level="The level to view, starting from 1",
        node="The node to view, starting from 1. The 'level' parameter must be set to a value",
        public="Errors will be sent publicly if this is True! Sets if the result is sent publicly in the channel")
    async def researchViewerCommand(interaction:discord.Interaction,level:int=0,node:int=0,public:bool=False) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        file = None
        responseMsg = ""
        if await hasPermission(PermissionLvls.PUBLIC_FEATURE if public else PermissionLvls.PRIVATE_FEATURE,interaction=interaction):
            await interaction.response.defer(ephemeral=not public)
            try:
                if node != 0:
                    if level == 0:
                        responseMsg = "Error : 'node' parameter provided but not 'level' parameter"
                    elif level < 1 or level > len(gameInfos.research.reserachTree):
                        responseMsg = "Error : invalid level"
                    else:
                        curLevel = gameInfos.research.reserachTree[level-1]
                        if node < 1 or node > len(curLevel.sideGoals)+1:
                            responseMsg = "Error : invalid node"
                        else:
                            file, fileSize = researchViewer.renderNode(level-1,node-1)
                            curNode = curLevel.milestone if node == 1 else curLevel.sideGoals[node-2]
                            desc = utils.decodedFormatToDiscordFormat(utils.decodeUnityFormat(curNode.desc))
                            desc = "\n".join(f"> {l}" for l in desc.split("\n"))
                            if curNode.unlocks == []:
                                unlocks = "<Nothing>"
                            else:
                                unlocks = ", ".join(f"`{u}`" for u in curNode.unlocks)
                            lines = [
                                f"- **Name** : {utils.decodedFormatToDiscordFormat(utils.decodeUnityFormat(curNode.title))}",
                                f"- **Id** : `{curNode.id}`",
                                f"- **Description** :\n{desc}",
                                f"- **Goal Shape** : `{curNode.goalShape}` x{utils.sepInGroupsNumber(curNode.goalAmount)}",
                                f"- **Unlocks** :\n> {unlocks}",
                                f"- **Lock/Unlock commands** :",
                                f"> ```research.set {curNode.id} 0```",
                                f"> ```research.set {curNode.id} 1```"
                            ]
                            responseMsg = "\n".join(lines)
                elif level != 0:
                    if level < 1 or level > len(gameInfos.research.reserachTree):
                        responseMsg = "Error : invalid level"
                    else:
                        file, fileSize = researchViewer.renderLevel(level-1)
                else:
                    file, fileSize = researchViewer.renderTree()
            except Exception:
                await globalLogError()
                responseMsg = globalInfos.UNKNOWN_ERROR_TEXT
        else:
            await interaction.response.defer(ephemeral=True)
            responseMsg = globalInfos.NO_PERMISSION_TEXT
        kwargs = {}
        if file is not None:
            if isFileTooBig(fileSize,interaction.guild):
                file = discord.File(globalInfos.IMAGE_FILE_TOO_BIG_PATH)
            else:
                file = discord.File(file,"researchTree.png")
            kwargs["file"] = file
        if public:
            responseMsg = safenString(responseMsg)
        await interaction.followup.send(responseMsg,**kwargs)

    @tree.command(name="msg",description="Public by default ! A command for shortcuts to messages")
    @discord.app_commands.describe(msg="The message id",public="Wether to send the message publicly or not")
    @discord.app_commands.choices(msg=[discord.app_commands.Choice(name=id,value=id) for id in msgCommandMessages.keys()])
    async def msgCommand(interaction:discord.Interaction,msg:discord.app_commands.Choice[str],public:bool=True) -> None:
        if exitCommandWithoutResponse(interaction):
            return
        if await hasPermission(PermissionLvls.PUBLIC_FEATURE if public else PermissionLvls.PRIVATE_FEATURE,interaction=interaction):
            responseMsg = msgCommandMessages[msg.value]
            ephemeral = not public
        else:
            responseMsg = globalInfos.NO_PERMISSION_TEXT
            ephemeral = True
        await interaction.response.send_message(responseMsg,ephemeral=ephemeral)

    with open(globalInfos.TOKEN_PATH) as f:
        token = f.read()
    client.run(token)

executedOnReady = False
globalPaused = False
msgCommandMessages:dict[str,str]