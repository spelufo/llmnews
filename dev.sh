#!/usr/bin/env bash

set -e

deploy() {
  scp news.py root@pancho:/root/llmnews/news.py
}

run() {
  python news.py
}

cmd="${1:-run}"
shift || true
$cmd "$@"
