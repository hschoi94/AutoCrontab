import os

use_paths = lambda dir_path: {
    "config": os.path.join(dir_path, "config"),  # configure files
    "env_temp": os.path.join(dir_path, "env_temp"),  # remote env, test env
    "input": os.path.join(dir_path, "input"),
    "result": os.path.join(dir_path, "result"),
    "scheduler": os.path.join(dir_path, "scheduler"),
    "backup": os.path.join(dir_path, "backup"),  # backup: file_name_{add_task_time}.tar
    "workspace": os.path.join(dir_path, "workspace"),
    "logs": os.path.join(dir_path, "logs"),
}


run_file = "run.sh"
workspace_history = "history.txt"
