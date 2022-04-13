#!/bin/bash

# Stop on errors
set -e

usage() {
  echo "Usage: $0 (create|destroy|reset)"
}

create() {
  if [ -f var/haidm.db ]; then
    echo "Error: database already exists"
    exit 1
  fi

  mkdir -p var
  sqlite3 var/haidm.db < sql/schema.sql
}

destroy() {
  rm -rf var/haidm.db
}

if [ $# -ne 1 ]; then
  usage
  exit 1
fi

# Parse argument.  $1 is the first argument
case $1 in
  "create")
    create
    ;;

  "destroy")
    destroy
    ;;

  "reset")
    read -p "Continue (y/n)?" -n 1 -r choice
    case "$choice" in
      y|Y)
        destroy
        create
        echo
        ;;
      n|N)
        echo
        ;;
      *)
        echo "invalid"
        ;;
    esac
    ;;

  *)
    usage
    exit 1
    ;;
esac
