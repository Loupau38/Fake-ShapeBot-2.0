<h2>Fake ShapeBot 2.0</h2>

v1.0
<br>
<br>
<br>
Put your shape code and parameters in `{}`

Shapes :

- Colorable :
  - C : Circle
  - R : Rectangle/Square
  - W : Windmill/Fan
  - S : Star/Spike
- Uncolorable :
  - P : Pin
  - c : Crystal
  - \- : Nothing

Colors :

- r : Red
- g : Green
- b : Blue
- c : Cyan
- p/m : Purple/Magenta
- y : Yellow
- w : White
- k : Black
- \- : Nothing

Parameters :

Each parameter must have a `+` in front of it

- +struct : Use `0` and `1` in your shape code and they will be replaced by nothing or a circle with the color depending on the layer
- +fill : For each layer, if it contains one quadrant, that quadrant will be repeated 4 times, if two quadrants, they will be repeated 2 times
- +lfill : Same as `fill` but with layers instead of quadrants
- +cut : Will cut the shape in half and show the two resulting shapes
- +qcut : Same as `cut` but will cut the shape in 4 instead of 2
- +lsep : Will separate each layer of the shape

Note : `cut` and `qcut` are mutually exclusive

Additional features :

- If the shape code starts with either `level`, `lvl` or `m` followed by a number, it will produce the shape for the corresponding milestone
- Shape expansion : Colorable shapes (like `C`) not followed by a color will have `u` appended (`Cu`), uncolorable shapes (like `P` or `-`) not followed by `-` will have `-` appended (`P-` or `--`)

No matter in which order you put your parameters in your shape code, they will be executed in the following order :<br>
milestone shapes, lfill, struct, shape expansion, fill, lsep, cut/qcut

Display parameters :

Display parameters must be put outside of the `{}`, have a `/` in front of them and have a `:` separating the parameter name from the value (if there is one)

- /size:80 : will control the width and height in pixels of each shape (default:56, min:10, max:100)
- /spoiler : will mark the resulting image as spoiler
- /result : will additionally send the generated shape codes
- /3d : will additionally send links to [DontMash's 3D shape viewer](https://shapez.soren.codes/shape)

Note : shapes with more than 4 layers and/or with more/less than 4 quadrants per layer are supported
<br>
<br>
<br>
Slash commands
<br>
<br>
Public commands :

- /view-shapes [message] : will trigger the shape viewer like a regular message but will send the response back only to you and will also include any error messages
- /change-blueprint-version [blueprint] [version] : Changes a blueprint's version and returns the new code

Admin commands :

- Pausing :<br>
  While paused, the bot will not send any public messages on the server
  - /pause : pauses the bot
  - /unpause : unpauses the bot
- Restrict to channel :<br>
  The bot will only send public messages on the channel it is restricted to
  - /restrict-to-channel [channel] : Sets the channel ID to restrict the bot to, use 0 to clear this parameter and not restrict the bot to any channel
- Restrict to roles :<br>
  If 'restrictToRolesInverted' is false, only users who have at least one role part of the 'restrictToRoles' list will be able to make the bot send public messages. If true, only users who have at least one role that isn't part of the list will be able to. In both cases, if the list is empty, every user will be able to.
  - /restrict-to-roles-add [role] : adds a role ID to the list
  - /restrict-to-roles-remove [role] : removes a role ID from the list
  - /restrict-to-roles-view : view the 'restrictToRoles' list
  - /restrict-to-roles-set-inverted [inverted] : sets the 'restrictToRolesInverted' parameter
- Admin roles :<br>
  Only users who have a role part of the 'adminRoles' list or who have the administrator permission will be able to use admin commands
  - /admin-roles-add [role] : adds a role ID to the list
  - /admin-roles-remove [role] : removes a role ID from the list
  - /admin-roles-view : view the 'adminRoles' list

Owner commands :

- /global-pause : pauses the bot globally
- /global-unpause : unpauses the bot globally
- /stop : stops the bot