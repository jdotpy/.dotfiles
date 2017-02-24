PATH="$PATH:~/.dotfiles/bin"

source ~/.dotfiles/conf/git-completion.bash

alias untarball="tar -xzf"
alias tarball="tar -czf"

prompt() {
  git_head_output="$(git symbolic-ref HEAD 2>&1)"
  
  if [[ $git_head_output == *"ref HEAD is not a symbolic ref"* ]]; then
    branch_name="!Detached Head!"
  elif [[ $git_head_output == *"Not a git repository"* ]]; then
    branch_name=""
  else 
    branch_name=${git_head_output##refs/heads/}
  fi
  if [ -n "$branch_name" ]; then 
    export PS1="\[\e[34m\][\t] me \[\e[39m\]\w\[\e[93m\] {$branch_name}\[\e[34m\]$\[\e[39m\] "
  else
    export PS1="\[\e[34m\][\t] me \[\e[39m\]\w\[\e[34m\]$\[\e[39m\] "
  fi
}

PROMPT_COMMAND=prompt
