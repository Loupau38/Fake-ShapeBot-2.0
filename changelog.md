## 15 Feb 24
- Update for alpha 15.3 demo pins : add modified version name in game infos
- Make blueprints module blueprint objects' encode functions private
- Update shape viewer response formatting
  - Fix `:` in links not being escaped
- Implement cache for /research-viewer with level=0 and node=0
- Add level number above levels in research viewer
- Separate milestone from sidegoals in research viewer
- Change shape viewer layer size reduction amount
- Change bot name to 'Fake ShapeBot 2'
- Change `utils.sepInGroupsNumber()` function code to use builtin f-string formatter
- Fix /operation-graph pin pushing operation not making unsupported quadrants fall
- Fix decoding blueprints with item producers producing fluid crates causing an error
- Fix type of an island or building entry's rotation being `int` instead of `utils.Rotation` when decoding blueprints
- Fix blueprint encoding using 4 spaces as indent in the JSON while the game uses 2

## 11 Jan 24
- Update for alpha 15.3 demo : add version in game infos

## 08 Jan 24
- Update for alpha 15.2 demo : add version in game infos
- Add changelog link to readme
- Rename user displayed term 'island' to 'platform'
- Add platform unit count and blueprint cost to /blueprint-info
- Change /blueprint-info response format
- Add exception name to most error messages triggered by an `except Exception`

## 06 Jan 24
- In blueprints module, move tile dict representation creation from decoding part to building or island blueprint object creation
- Use set instead of dict for overlapping tiles check in blueprint decoding
- In blueprints module, move building blueprint creation from island blueprint from decoding part to blueprint object creation
- Remove some repeated code for building/island blueprint decoding in `decodeBlueprint()` function
- Use different coding approach for at least a bit complex slash commands reducing indentation levels and `else:` count
- Rename `toJSON()` blueprint encoding functions to `encode()`
- On blueprint encoding error, precise in which of the two parts the error happened
- Add /blueprint-creator command
  - Add latest major version constant to version module of game infos
  - Separate latest public and latest patreon-only game versions into two constants
  - When a blueprint building entry that should have additional data is created without any, it will now get its default
- Fix blueprints module producing error when decoding blueprints containing train stations older than alpha 15.2
- Fix `bot.globalLogMessage()` not acting correctly if the message is more than 2000 characters
- Fix /change-blueprint-version command returning error messages in code blocks (again)
- Fix not accounting for fluid producers actually saving their color with the `color-` prefix in blueprints
- Fix constant signal generated fluid value not being represented like a fluid producer's generated fluid
- Fix blueprint encoding not omitting keys

## 04 Jan 24
- Add shapez 1 discord server invite /msg message
- Update readme formatting
- Update game infos islands version to alpha 15.2
- Use prettier syntax to import game infos modules
- Blueprint encoding now omits keys when possible
- In blueprint decoding error messages, when a Pos is mentioned, specify if it's raw or rectified
- `safenString()` in public /msg command
- Move some repeated code for getting blueprint code from string or file in slash commands into a function
- Move repeated code for getting a command response into a function
  - Remove now unused `utils.handleMsgTooLong()` function
- Remove unused variable in `utils.decodedFormatToDiscordFormat()`
- Add support for decoding building additional data in blueprints
  - Add decode and encode string with length functions to utils module
  - Add `isShapeCodeValid()` function to shape code generator module
    - Move the checks for if the shape code is valid from the `generateShapeCodes()` function into their own functions

## 21 Dec 23
- Update for alpha 15.2 : add version, update buildings and research in game infos
- Use code block for in-discord logged error messages
- Implement unknown error handling working for every command
- Potentially fix unknown error when having a loop in the nodes of a /operation-graph graph
- Fix /change-blueprint-version command returning error messages in code blocks

## 17 Dec 23
- Add /msg command with disambiguation screenshot message
- Overhaul server settings system :
  - Rename general term 'server settings' to 'guild settings' to better match discord's internal naming
  - Move guild settings handling to its own module
  - Fix not having a check in role list admin commands to verify that a role has been passed when using the 'add' or 'remove' subcommands
- Use (prettier) builtin methods in blueprint decoding code
- Move some code out of the `on_ready()` event
- Add note in readme for slash commands response type
- Make game infos load functions private
- Fix readme saying the bot will only react with alpha versions of blueprints (post-alpha versions support is planned)

## 16 Dec 23
- Update for alpha 15.1 demo : add version in game infos
- Regroup the `discord.utils.escape_mentions()` used in public shape viewer, /operation-graph and /research-viewer into a `safenString()` function

## 12 Dec 23
- Update for alpha 15 demo : add version in game infos

## 11 Dec 23
- Reintroduce changelog to better see progress on this project
- Update for alphas : 12 demo, 13 demo, 13.5 demo, 13.6 demo, 13.7 demo, 14 demo, 14.1 demo, 14.2 demo, 14.3 demo : add versions in game infos
- Added filtered game infos for extra features and easier updating between game versions
- Big overhaul to the blueprints module, only user visible changes should be:
  - Better error messages
  - Accurate blueprint size
  - Both building scale and island scale size in island blueprints
- Separated building counts in categories and subcategories in /blueprint-info with advanced=true
- Added research viewer
- Added util function to add thousands separators in numbers, used in /research-viewer goal shape amount and /blueprint-info building/island counts
- Allow for other characters than "0" or "1" when using the +struct parameter in shape viewer to account for the differing behavior of pins and crystals
- Fixed uncolored not being listed in readme
- Fixed error when viewing shape codes that all resulted in empty shapes
- General code refactoring : lots of things moved around but hopefully still functions the same