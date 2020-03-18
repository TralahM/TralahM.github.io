---
categories: git vcs
excerpt: "Getting Started with the GIT Version Control System"
---

# Getting Started with the GIT Version Control System

## What is Git?

### Installation

#### Linux
1. Debian
```sh
sudo apt-get install git -y
```
2. Redhat
```sh
sudo rpm install git -y
```
3. Using the yum package manager
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

##### Or Edit the ~/.gitconfig file on unix-based platforms

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

```sh
mkdir new_repo
cd new_repo
git init .
git remote add origin <git@your-remote-url.com:username/repo_name.git>
```

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
