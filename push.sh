#!/bin/bash
# push.sh — add everything, prompt for commit message, push to main

set -e

echo ""
read -p "Commit message: " message

if [ -z "$message" ]; then
  echo "No message entered. Aborting."
  exit 1
fi

git add .
git commit -m "$message"
git push -u origin main

echo ""
echo "Done."
