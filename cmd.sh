#!/bin/bash

set -e

if [ "$ENV" = "DEV" ]; then
  echo "Running Development Server"
  exec python "app.py"
fi
