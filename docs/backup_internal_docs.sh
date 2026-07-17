#!/bin/bash
# Snapshot CLAUDE.md + docs/ onto the private 'internal-docs' branch (origin only).
# Run after editing internal docs: bash docs/backup_internal_docs.sh
set -euo pipefail
cd "$(dirname "$0")/.."
export GIT_INDEX_FILE=$(mktemp -u)
git add -f CLAUDE.md docs
TREE=$(git write-tree)
PARENT=$(git rev-parse -q --verify internal-docs 2>/dev/null || true)
if [ -n "$PARENT" ]; then
  COMMIT=$(git commit-tree "$TREE" -p "$PARENT" -m "internal docs snapshot $(date +%F)")
else
  COMMIT=$(git commit-tree "$TREE" -m "internal docs snapshot $(date +%F)")
fi
rm -f "$GIT_INDEX_FILE"; unset GIT_INDEX_FILE
git branch -f internal-docs "$COMMIT"
git push origin internal-docs -f
echo "internal-docs -> $COMMIT (pushed to origin only)"
