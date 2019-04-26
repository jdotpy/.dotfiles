ln -sf ~/.dotfiles/conf/vimrc ~/.vimrc 
ln -sf ~/.dotfiles/conf/vim ~/.vim

printf "\nsource ~/.dotfiles/conf/bash_config.sh\n" >> ~/.bashrc

# Finish by forcing a refresh
source ~/.bashrc

