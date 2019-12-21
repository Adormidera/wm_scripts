#!/bin/bash -
#title           :install.sh
#description     :Install Villegas vim and bash configurations
#author          :alejandro.villegas
#usage           :./install.sh
#notes           :Depends on the template file
#==============================================================================





#============================== Global Variables ==============================#
#==============================================================================#
TEMPLATE_FILE="$HOME/.villegas/.template"
VILLEGAS_HOME="$HOME/.villegas"
source $TEMPLATE_FILE
VERBOSE=1
YESTOALL=0





#============================== Init ==========================================#
#==============================================================================#
while getopts "hvqy" arg; do
  case $arg in
    h)
      cecho "$FG_YELLOW./install [OPTIONS] " 
      cecho "$FG_YELLOW   -y    - Yes to all questions $COLOR_RESET"
      cecho "$FG_YELLOW   -v    - Verbose Mode $COLOR_RESET"
      cecho "$FG_YELLOW   -q    - Quiet Mode $COLOR_RESET"
      cecho "$FG_YELLOW   -h    - Print this message $COLOR_RESET"
      exit
      ;;
    q) VERBOSE=0 ;;
    v) VERBOSE=1 ;;
    y) YESTOALL=1 ;;
  esac
done



inf_msg "Launching A.Villegas environment installer"
deb_msg "Installing config for user: $USER"
deb_msg "Operative System: $(cat /etc/os-release | grep "^NAME=" | awk -F "=" '{print $2}')"
yesno "Is correct?"
[[ $? -ne 0 ]] && { err_msg "Aborted installation. Exiting..."; exit; }
inf_msg "Beginning Installation"



# Bash Config file
##########################################################################
deb_msg "Installing Bash Config"
bashrc_target_file="$HOME/.bashrc"

if [[ -h $bashrc_target_file ]];then
    unlink $bashrc_target_file
elif [[ -f $bashrc_target_file ]]; then
    mv $bashrc_target_file ${bashrc_target_file}_old_$(date +%s)
fi

ln -s ~/.villegas/bash_config/bashrc $bashrc_target_file



# ViM Config file
##########################################################################
deb_msg "Installing ViM Config"
if [[ -h $HOME/.vimrc ]];then 
    unlink $HOME/.vimrc
elif [[ -f $HOME/.vimrc ]];then 
    mv $HOME/.vimrc $HOME/.vimrc_old_$(date +%s)
fi

ln -s $HOME/.villegas/vim_config/vimrc $HOME/.vimrc



# ViM Config file
##########################################################################
deb_msg "Installing ViM Plugins"
if [[ -h $HOME/.vim ]]; then
     unlink $HOME/.vim
elif [[ -f $HOME/.vim ]];then 
    mv $HOME/.vim .vim_old_$(date +%s)
fi

ln -s $HOME/.villegas/vim_config/vim $HOME/.vim

inf_msg "Installing ViM plugins dir"
[[ -d vim_config/vim ]] && { deb_msg "Cleanning old data"; rm -Rf vim_config/vim; }

tar xzf $VILLEGAS_HOME/vim_config/vim.tar.gz -C $VILLEGAS_HOME/ 1>/dev/null



# i3 Config
##########################################################################
deb_msg "i3wm Config"
if [[ -f $HOME/.config/i3/config ]];then 
    mv $HOME/.config/i3/config $HOME/.config/i3/config_old_$(date +%s)
fi
ln -s $HOME/.villegas/i3wm_config/i3_config $HOME/.config/i3/config


deb_msg "i3status Config"
if [[ -f $HOME/.config/i3status/config ]];then 
    mv $HOME/.config/i3status/config $HOME/.config/i3status/config_old_$(date +%s)
fi
ln -s $HOME/.villegas/i3wm_config/i3status_config $HOME/.config/i3status/config



# Finish
##########################################################################
ok_msg "Installation Finished"
