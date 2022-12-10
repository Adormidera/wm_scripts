#!/bin/bash
# Adormidera Installer


## Vars
################################################################################
SCRIPT_DIR=$(cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd)
CONFIG_DIR="$HOME/.config/adormidera"


## Basic functions
################################################################################
function cecho (){
  echo -e "$1"
}
function ok_msg () {
  cecho "[OK] - $@"
}
function inf_msg () {
  cecho "[--] - $@"
}
function war_msg () {
  cecho "[WR] - $@"
}
function err_msg () {
  cecho "[ER] - $@"
}

function yesno () {
  [[ $YESTOALL -eq 1 ]] && { return 0; }
  read -p  "Are you sure? (Y/N)" OPT
  # Convert to lowercase to reduce matching options
  if [ $(echo "$OPT" | tr '[:upper:]' '[:lower:]') == "y" ]; then
    return 0
  else
    return 1
  fi
}



## Install
################################################################################

# Creating config dirs
inf_msg "Creating config directories..."
if [[ -d $cfd ]]; then
  war_msg "Adormidera config dir ($CONFIG_DIR) already exists for this user: $USER"
else
  mkdir -p $CONFIG_DIR
  ok_msg "Config dir:$CONFIG_DIR crated"
fi


# Copying files
inf_msg "Copying config files"
for item in "scripts" "config"; do
  ok_msg "Linking $item dir"
  ln -s $SCRIPT_DIR/$item $CONFIG_DIR/$item 2>/dev/null
done


# Adding "arf" CLI
# TODO

ok_msg "Done"
