#!/usr/bin/env bash

set -e

deploy() {
  git push pancho main
  ssh root@pancho 'cd /root/llmnews && ./dev.sh install'
}

install() {
  [ $(hostname) = pancho ] || {
    echo "This script must be run on the server"
    exit 1
  }  
  cp systemd/llmnews.service /etc/systemd/system/llmnews.service
  cp systemd/llmnews.timer /etc/systemd/system/llmnews.timer
  touch /var/log/llmnews.log
  chmod 644 /var/log/llmnews.log
  systemctl daemon-reload
  systemctl enable llmnews.timer
  systemctl start llmnews.timer
  systemctl status llmnews.timer
}

pancho_git() {
  ssh root@pancho "cd /root/llmnews && GIT_DIR=/root/llmnews.git GIT_WORK_TREE=/root/llmnews git $@"
}

run() {
  . .env
  python news.py
}

web() {
  . .env
  flask --app website.py run
}

cmd="${1:-run}"
shift || true
$cmd "$@"
