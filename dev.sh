#!/usr/bin/env bash

set -e

deploy() {
  git push pancho main
}

pancho_git() {
  ssh root@pancho "cd /root/llmnews && GIT_DIR=/root/llmnews.git GIT_WORK_TREE=/root/llmnews git $@"
}

run() {
  . .env
  time python news.py
}

cmd="${1:-run}"
shift || true
$cmd "$@"
