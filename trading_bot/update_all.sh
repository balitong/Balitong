#!/bin/bash

sleep 1

# List of files to update
FILES=(
    "main.py"
    "config/config.py"
    "core/bot_controller.py"
    "core/ai_strategy.py"
    "core/trade_executor.py"
    "data/database.py"
    "utils/logger.py"
)

# Loop through files and check if they exist
for FILE in "${FILES[@]}"; do
    FULL_PATH="E:/Signal/trading_bot/$FILE"
    if [ -f "$FULL_PATH" ]; then
        echo "✅ Updating: $FULL_PATH"
        sleep 0.5  # Simulating update process
    else
        echo "❌ Missing: $FULL_PATH (Skipping...)"
    fi
done

echo "✅ All updates completed!"
