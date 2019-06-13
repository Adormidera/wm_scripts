#!/bin/bash -
#title           :install.sh
#description     :Install Villegas vim and bash configurations
#author          :alejandro.villegas
#date            :20180605
#version         :0.2
#usage           :./install.sh
#notes           :Depends on the template file
#==============================================================================

TEMPLATE_FILE="$HOME/.villegas/.template"
VILLEGAS_HOME="$HOME/.villegas"
source $TEMPLATE_FILE
checkOS

VERBOSE=1
YESTOALL=0

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



inf_msg "Iniciando instalador villegas"
inf_msg "Instalando en el directorio: $HOME"
deb_msg "Instalando para el usuario: $USER"
deb_msg "Sistema Operativo: $platform"
inf_msg "Es correcto?"
yesno
[[ $? -ne 0 ]] && { err_msg "Instalacion abortada. Saliendo..."; exit; }
ok_msg "Comenzando la instalacion"

[[ -d vim_config/vim ]] && { deb_msg "Borrando datos antiguos..."; rm -Rf vim_config/vim; }

deb_msg "Descomprimiendo..."
tar xzf $VILLEGAS_HOME/vim_config/vim.tar.gz -C $VILLEGAS_HOME/ 1>/dev/null

deb_msg "Instalando Bashrc..."
if [[ $platform == "linux" ]]; then
  bashrc_target_file="$HOME/.bashrc"
  inf_msg "Instalar bashrc Maestro?"
  yesno
  [[ $? -ne 0 ]] && { war_msg "No se va a instalar Bashrc Maestro"; } || { sudo cp $HOME/.villegas/bash_config/bashrc_master /etc/bashrc; ok_msg "Bashrc Maestro instalado"; }
elif [[ $platform == "macos" ]]; then
  bashrc_target_file="$HOME/.bash_profile"
fi

if [[ -h $bashrc_target_file ]];then
    unlink $bashrc_target_file
elif [[ -f $bashrc_target_file ]]; then
    mv $bashrc_target_file ${bashrc_target_file}_old_$(date +%s)
fi
ln -s ~/.villegas/bash_config/bashrc_villegas $bashrc_target_file

deb_msg "Instalando vimrc..."
if [[ -h $HOME/.vimrc ]];then 
    unlink $HOME/.vimrc
elif [[ -f $HOME/.vimrc ]];then 
    mv $HOME/.vimrc $HOME/.vimrc_old_$(date +%s)
fi
ln -s $HOME/.villegas/vim_config/vimrc $HOME/.vimrc

deb_msg "Instalando vim..."
if [[ -h $HOME/.vim ]]; then
     unlink $HOME/.vim
elif [[ -f $HOME/.vim ]];then 
    mv $HOME/.vim .vim_old_$(date +%s)
fi
ln -s $HOME/.villegas/vim_config/vim $HOME/.vim

deb_msg "Configurando path"
[[ ! -h $HOME/grv ]] && { ln -s $HOME/.villegas/software/grv $HOME/grv; }


ok_msg "Instalacion Finalizada"
