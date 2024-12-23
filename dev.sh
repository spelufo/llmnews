#!/usr/bin/env bash

set -e

deploy() {
  if ! git diff-index --quiet HEAD --; then
    echo "Uncommitted changes, exiting."
    exit 1
  fi
  git push pancho main
  ssh root@pancho 'cd /root/llmnews && ./dev.sh install'
}

install() {
  [ $(hostname) = pancho ] || {
    echo "This script must be run on the server"
    exit 1
  }
  . .venv/bin/activate
  pip install -r requirements.txt
  cp systemd/llmnews.service /etc/systemd/system/llmnews.service
  cp systemd/llmnews.timer /etc/systemd/system/llmnews.timer
  cp systemd/llmnews_web.service /etc/systemd/system/llmnews_web.service
  touch /var/log/llmnews.log
  touch /var/log/llmnews_web.log
  chmod 644 /var/log/llmnews.log
  chmod 644 /var/log/llmnews_web.log
  systemctl daemon-reload
  systemctl enable llmnews.timer
  systemctl enable llmnews_web.service
  systemctl start llmnews.timer
  systemctl start llmnews_web.service
  systemctl status llmnews.timer
  systemctl status llmnews_web.service
}

pancho_git() {
  ssh root@pancho "cd /root/llmnews && GIT_DIR=/root/llmnews.git GIT_WORK_TREE=/root/llmnews git $@"
}

pull_db() {
  scp root@pancho:/root/llmnews/news.db ./news.db
}

run() {
  . .env
  python news.py
}

flask() {
  . .env
  flask --app website.py run
}

web() {
  . .env
  gunicorn --bind localhost:8000 website:app --log-file /dev/stdout
}

help() {
  echo "Usage: $0 <command>"
  echo ""
  echo "Development commands:"
  echo "  deploy      Deploy to the server"
  echo "  pull_db     Pull the database from the server"
  echo "  pancho_git  Run git commands on the server"
  echo ""
  echo "Server commands:"
  echo "  install     Install the service"
  echo "  run         Run the news scraper"
  echo "  web         Run the uWSGI web server"
}

cmd="${1:-help}"
shift || true
$cmd "$@"
