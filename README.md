# Adormidera Ricing Framework (ARF)
Adormidera Ricing Framework is designed to create and customize tilling window
manager (I3wm) using different graphic add-ons like: i3status, i3blocks and polybar.

## Basic install
```sh
bash ./install.sh
```

## Every Script requirements
Every script included in this project must follow a few rules to be
used/configured properly for each graphic add-on supported by ARF.

## Environment Variables
Env variables is for this project the main way to configure the desired
behaviour (colors, thresholds, icons...) for the user

### Mandatory Env Vars
These vars must be used in every script
* `ARF_COLOR`: Requires a HEX color to be used as default color output of the script. By default, the color is: "#1070FF"

### Optional Env Vars
These vars could be used in every script
* `ARF_ICON`: Defines the icon to be placed next to the script returned value (e.g. " "). It could be empty if you don't want to use any icon.

### Thresholds Env Vars
Use these vars if your script admits thresholds
* `ARF_WARN_LIMIT`: Default value 70%
* `ARF_ERR_LIMIT`: Default value 90%

### Color Env Vars
If the script uses thresholds, probably you want also to modify the color output
for each status. To do it, use the following vars:
* `ARF_OK_COLOR`: Default value: '#1FC40D'
* `ARF_WARN_COLOR`: Default value: '#FFA600'
* `ARF_ERR_COLOR`: Default value: '#DE1212'

