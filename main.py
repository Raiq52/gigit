import sys
import os
import subprocess  # Ajout de l'importation du module subprocess
from config import save_config, load_config
from commands import execute_git_command
from utils import print_help

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "help":
        print_help()
        sys.exit(0)

    if command == "init":
        if len(args) != 2:
            print("Usage: gigit init <backend_repo_path> <frontend_repo_path>")
            sys.exit(1)
        backend_repo_path = args[0]
        frontend_repo_path = args[1]
        if not os.path.isdir(backend_repo_path):
            print(f"Backend repository path does not exist: {backend_repo_path}")
            sys.exit(1)
        if not os.path.isdir(frontend_repo_path):
            print(f"Frontend repository path does not exist: {frontend_repo_path}")
            sys.exit(1)
        save_config(backend_repo_path, frontend_repo_path)
        print(f"Configuration saved: backend={backend_repo_path}, frontend={frontend_repo_path}")
        sys.exit(0)

    backend_repo_path, frontend_repo_path = load_config()

    if command == "status":
        git_command = ["git", command] + args
    elif command == "front":
        git_command = ["git"] + args
        execute_git_command(git_command, backend_repo_path, frontend_repo_path, repo_type="front")
        sys.exit(0)
    elif command == "back":
        git_command = ["git"] + args
        execute_git_command(git_command, backend_repo_path, frontend_repo_path, repo_type="back")
        sys.exit(0)
    else:
        git_command = ["git", command] + args

    if command in ["branch", "checkout", "status", "commit", "push", "delete-branch"]:
        if command == "branch" and len(args) == 1:
            new_branch = args[0]
            execute_git_command(["git", "branch", new_branch], backend_repo_path, frontend_repo_path, print_output=False)
            execute_git_command(["git", "branch"], backend_repo_path, frontend_repo_path)
        elif command == "checkout" and len(args) == 1:
            branch_name = args[0]
            try:
                execute_git_command(["git", "checkout", branch_name], backend_repo_path, frontend_repo_path, print_output=False)
            except subprocess.CalledProcessError:
                print("Untracked files or changes present. Stashing changes.")
                execute_git_command(["git", "stash", "--include-untracked"], backend_repo_path, frontend_repo_path, print_output=False)
                execute_git_command(["git", "checkout", branch_name], backend_repo_path, frontend_repo_path, print_output=False)
                print("Restoring stashed changes.")
                execute_git_command(["git", "stash", "pop"], backend_repo_path, frontend_repo_path, print_output=False)
            execute_git_command(["git", "branch"], backend_repo_path, frontend_repo_path)
        elif command == "delete-branch" and len(args) == 1:
            branch_name = args[0]
            execute_git_command(["git", "branch", "-d", branch_name], backend_repo_path, frontend_repo_path, print_output=False)
            execute_git_command(["git", "branch"], backend_repo_path, frontend_repo_path)
        else:
            execute_git_command(git_command, backend_repo_path, frontend_repo_path)
    else:
        print(f"Unknown command: {command}")
        print_help()
