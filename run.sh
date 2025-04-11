#!/bin/bash

# Activate the virtual environment
source /home/momad/projects/BEMO/.venv/bin/activate

# Base path
PROJECT_ROOT="/home/momad/projects/BEMO/main"

# Script paths
declare -a scripts=(
    "server/websocket_server.py"
    "main.py"
    "task_classifier/task_classifier.py"
    "preprocessing/preprocessing.py"
    "task_handler/task_handler.py"
    "task_handler/general_questions_module/general_questions_pipeline.py"
    "task_handler/communication_module/tasks_api.py"
    "task_handler/learning_resources_module/find_learning_resources.py"
    "task_handler/smart_home_module/home_automation.py"
)

# Run each script in the background with 1-second delay between each
for script in "${scripts[@]}"; do
    echo "Starting $script..."
    python "$PROJECT_ROOT/$script" &
    sleep 1
done

echo "All scripts started."

wait
