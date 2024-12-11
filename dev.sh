#!/usr/bin/env bash

set -e

deploy() {
  if [[ -n $(git status --porcelain) ]]; then
    read -p "There are uncommitted changes. Continue with deployment? [y/N] " response
    if [[ ! $response =~ ^[Yy]$ ]]; then
      echo "Deployment cancelled"
      exit 1
    fi
  fi
  deployment_name="deploy_$(date +%Y-%m-%d)_$(git rev-parse --short HEAD).tar.gz"
  git archive --format=tar.gz HEAD > $deployment_name
  scp $deployment_name root@pancho:/root/llmnews/$deployment_name
  ssh root@pancho "cd /root/llmnews && tar xzf $deployment_name && rm $deployment_name"
  mv $deployment_name deployments/
}

run() {
  python news.py
}

cmd="${1:-run}"
shift || true
$cmd "$@"
