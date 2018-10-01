PATH="$PATH:~/.dotfiles/bin"
export CLICOLOR=1

source ~/.dotfiles/conf/git-completion.bash

alias untarball="tar -xzf"
alias tarball="tar -czf"
alias ll="ls -la"
alias pyserve="python3 -m http.server"

# Using my own commands
alias findips="streamline --filter 're.match(\".*\d{1,3}\.\d{1,3}\", line)' 're.match(r\".*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*\", line).group(1)'"

prompt() {
  ################
  # Git Repo
  git_head_output="$(git symbolic-ref HEAD 2>&1)"
  if [[ $git_head_output == *"ref HEAD is not a symbolic ref"* ]]; then
    ps1_git_status="!Detached Head!"
  elif [[ $git_head_output == *"ot a git repository"* ]]; then
    ps1_git_status=""
  else 
    ps1_git_status=${git_head_output##refs/heads/}
  fi
  if [ -n "$ps1_git_status" ]; then 
    ps1_git_status="{$ps1_git_status}"
  fi

  ################
  # Virtual Env
  if [ -n "$VIRTUAL_ENV" ]; then
    ps1_virtual_env=$(basename "$VIRTUAL_ENV")
    ps1_virtual_env="($ps1_virtual_env)"
  else 
    unset ps1_virtual_env;
  fi
  

  ################
  # PS1
  export PS1="\[\e[34m\][\t] me:\[\e[96m\]$ps1_virtual_env\[\e[93m\]$ps1_git_status \[\e[39m\]\w \[\e[34m\]$\[\e[39m\] "
}

PROMPT_COMMAND=prompt

# Act like Vi, please
set -o vi
