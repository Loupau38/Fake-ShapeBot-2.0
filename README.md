# Fake ShapeBot 2.0

## Shape viewer :

Put your shape code and parameters in `{}`

### Shapes :

- Colorable :
  - C : Circle
  - R : Rectangle/Square
  - W : Windmill/Fan
  - S : Star/Spike
  - c : Crystal
- Uncolorable :
  - P : Pin
  - \- : Nothing

### Colors :

- r : Red
- g : Green
- b : Blue
- c : Cyan
- p/m : Purple/Magenta
- y : Yellow
- w : White
- k : Black
- \- : Nothing

### Parameters :

Each parameter must have a `+` in front of it

- +struct : Use `0` and `1` in your shape code and they will be replaced by nothing or a circle with the color depending on the layer
- +fill : For each layer, if it contains one quadrant, that quadrant will be repeated 4 times, if two quadrants, they will be repeated 2 times
- +lfill : Same as `fill` but with layers instead of quadrants
- +cut : Will cut the shape in half and show the two resulting shapes
- +qcut : Same as `cut` but will cut the shape in 4 instead of 2
- +lsep : Will separate each layer of the shape

Note : `cut` and `qcut` are mutually exclusive

### Additional features :

- If the shape code starts with either `level`, `lvl` or `m` followed by a number, it will produce the shape for the corresponding milestone
- Shape expansion : Colorable shapes (like `C`) not followed by a color will have `u` appended (`Cu`), uncolorable shapes (like `P` or `-`) not followed by `-` will have `-` appended (`P-` or `--`)

No matter in which order you put your parameters in your shape code, they will be executed in the following order :\
milestone shapes, lfill, struct, shape expansion, fill, lsep, cut/qcut

### Display parameters :

Display parameters must be put outside of the `{}`, have a `/` in front of them and have a `:` separating the parameter name from the value (if there is one)

- /size:80 : Will control the width and height in pixels of each shape (default:56, min:10, max:100)
- /spoiler : Will mark the resulting image as spoiler
- /result : Will additionally send the generated shape codes
- /3d : Will additionally send links to [DontMash's 3D shape viewer](https://shapez.soren.codes/shape)

Note : shapes with more than 4 layers and/or with more/less than 4 quadrants per layer are supported

## Slash commands

### Public commands :

- /view-shapes [message] : Will trigger the shape viewer like a regular message but will send the response back only to you and will also include any error messages
- /change-blueprint-version [blueprint] [version] [blueprint_file=None] : Changes a blueprint's version and returns the new code. If the blueprint code is too big to be pasted, provide a file containing it in the 'blueprint_file' parameter and fill in the 'blueprint' parameter with dummy character(s)
- /member-count : Displays the member count of the server it is executed in (with additional info such as online/offline count and percentage)
- /operation-graph [instructions] [public=False] [see_shape_vars=False] : See the [/operation-graph documentation](https://github.com/Loupau38/Fake-ShapeBot-2.0/blob/main/operationGraphDoc.md)
- /blueprint-info [blueprint] [advanced=False] [blueprint_file=None] : Will give the version, type, building count, island count and size of the given blueprint. If 'advanced' is set to True, will also give the individual counts for every building and islands. If the blueprint code is too big to be pasted, provide a file containing it in the 'blueprint_file' parameter and fill in the 'blueprint' parameter with dummy character(s)

### Admin commands :

- Pausing :\
  While paused, the bot will not send any public messages on the server
  - /pause : Pauses the bot
  - /unpause : Unpauses the bot
- Restrict to channel :\
  The bot will only send public messages on the channel it is restricted to
  - /restrict-to-channel [channel] : Sets the channel to restrict the bot to, don't include this parameter to clear it and not restrict the bot to any channel
- Restrict to roles :\
  If 'restrictToRolesInverted' is false, only users who have at least one role part of the 'restrictToRoles' list will be able to make the bot send public messages. If true, only users who have at least one role that isn't part of the list will be able to. In both cases, if the list is empty, every user will be able to.
  - /restrict-to-roles [operation] [role=None] : Modifys the 'restrictToRoles' list depending on the 'operation' parameter value :
    - add : Adds a role to the list
    - remove : Removes a role from the list
    - view : View the list
    - clear : Clears the list
  - /restrict-to-roles-set-inverted [inverted] : Sets the 'restrictToRolesInverted' parameter
- Admin roles :\
  Only users who have a role part of the 'adminRoles' list or who have the administrator permission will be able to use admin commands
  - /admin-roles : Modifys the 'adminRoles' list depending on the 'operation' parameter value :
    - add : Adds a role to the list
    - remove : Removes a role from the list
    - view : View the list
    - clear : Clears the list

### Owner commands :

- /global-pause : Pauses the bot globally
- /global-unpause : Unpauses the bot globally
- /stop : Stops the bot

## Small additional features :

- If the bot is mentioned, it should react with `:robot:`
- If one (and only one) blueprint code is detected in a message and its attached files, the bot will react with the alpha version of that blueprint