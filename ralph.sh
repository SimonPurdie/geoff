#!/bin/bash

# Config
PROMPT_FILE="PROMPT.md"
AGENT_NAME="ralph"
SLEEP_TIME=2  # seconds between runs
HASH_FILE=".last_hash"
STUCK_COUNT=0
MAX_STUCK=2  # stop if stuck twice in a row

# Helper: compute hash of the entire repo
compute_hash() {
  # Use git if repo exists, else fallback to find
  if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git ls-files -s | sha1sum
  else
    find . -type f ! -path "./.git/*" -exec sha1sum {} + | sort | sha1sum
  fi
}

# Initialize
PREV_HASH=""

while true; do
  echo "---------------------------"
  echo "Running Ralph at $(date)"
  
  # Run Ralph headless and stream output
  opencode run "$(cat "$PROMPT_FILE")" --log-level INFO 2>&1 | tee ralph_output.log

  # Compute new hash
  NEW_HASH=$(compute_hash | awk '{print $1}')
  echo "Repo hash: $NEW_HASH"

  # Compare with previous
  if [[ "$NEW_HASH" == "$PREV_HASH" ]]; then
    STUCK_COUNT=$((STUCK_COUNT+1))
    echo "No changes detected. Stuck count: $STUCK_COUNT/$MAX_STUCK"
    if [[ $STUCK_COUNT -ge $MAX_STUCK ]]; then
      echo "No changes for $MAX_STUCK iterations. Exiting loop."
      exit 0
    fi
  else
    STUCK_COUNT=0
    echo "Changes detected. Resetting stuck count."
  fi

  PREV_HASH="$NEW_HASH"
  sleep $SLEEP_TIME
done
