# Getting Started with GIT
## What is Git?
### Installation
#### Linux
1. Debian
```sh
sudo apt-get install git -y
```
```sh
sudo rpm install git -y
```
```console
sudo yum install git -y
```
#### MacOSX
```sh
brew install git
```
## Basic commands
## Basic Configuration
```sh
git config user.email <youremail@example.com>
git config user.name "Your Name"
```

```ini
[user]
name = Your Name
email = <youremail@example.com>
[core]
editor = vim
pager = less -S

[color]
ui = true
diff = auto
status = auto
grep = auto
interactive = auto

[merge]
tool = vimdiff
[alias]
ci = commit
lg = log --all --abbrev-commit --decorate --graph --oneline
st = status
co = checkout
mt = mergetool

[credential]
helper = cache

[help]
autocorrect = 10
```
### Creating a new repository
### Commits
```sh
git add . # Add all files in source tree
git commit # Add files to git
git commit -m "Commit Message" # without opening your editor
```
### Commit History

```sh
git log --all --abbrev-commit --decorate --graph --oneline
```
### Branching
```sh
git checkout -b new_branch # Create and switch to new branch
git checkout master  # Go to branch named master
git checkout commithash  # Checkout the state of the repository as at the commit
#hash
```
