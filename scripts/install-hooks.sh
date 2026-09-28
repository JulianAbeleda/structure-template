#!/bin/sh
set -eu

repo_root=$(git rev-parse --show-toplevel)

case "${1:-install}" in
  install)
    git -C "$repo_root" config core.hooksPath .githooks
    chmod +x "$repo_root"/.githooks/*
    echo "Git hooks enabled from .githooks"
    ;;
  remove|uninstall)
    configured=$(git -C "$repo_root" config --get core.hooksPath || true)
    if [ "$configured" = ".githooks" ]; then
      git -C "$repo_root" config --unset core.hooksPath
    fi
    echo "Repository hook override removed"
    ;;
  *)
    echo "usage: scripts/install-hooks.sh [install|remove]" >&2
    exit 2
    ;;
esac
