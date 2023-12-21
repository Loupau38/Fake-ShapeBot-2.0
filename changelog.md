## 21 Dec 23
- Update for alpha 15.2 : add version, update buildings and research in game infos
- Use code block for in-discord logged error messages
- Implement unknown error handling working for every command
- Potentially fix unknonw error when having a loop in the nodes of a /operation-graph graph
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