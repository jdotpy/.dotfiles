ln -sf ~/.dotfiles/conf/vimrc ~/.vimrc 
ln -sf ~/.dotfiles/conf/vim ~/.vim

printf "source ~/.dotfiles/conf/bash_config.sh" >> ~/.bashrc

# Finish by forcing a refresh
source ~/.bashrc

