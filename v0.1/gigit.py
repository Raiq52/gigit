import subprocess
import sys
import os
import json
from colored import fg, bg, attr

CONFIG_FILE = "gigit_config.json"

def save_config(backend_repo_path, frontend_repo_path):
    config = {
        "backend_repo_path": backend_repo_path,
        "frontend_repo_path": frontend_repo_path
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        print(f"Configuration file {CONFIG_FILE} not found. Please run 'gigit init' to set up the repository paths.")
        sys.exit(1)
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config["backend_repo_path"], config["frontend_repo_path"]

def run_command(command, repo_path, repo_type, print_output=True):
    try:
        result = subprocess.run(command, cwd=repo_path, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if print_output:
            print(highlight_text(repo_type + ":"))
            print(result.stdout)
        return result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"Error while running command: {command} in {repo_type}")
        print(f"Standard output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return e.stdout, e.stderr

def execute_git_command(command, backend_repo_path, frontend_repo_path, repo_type=None, print_output=True):
    if repo_type == "front":
        frontend_stdout, frontend_stderr = run_command(command, frontend_repo_path, "Frontend", print_output)
    elif repo_type == "back":
        backend_stdout, backend_stderr = run_command(command, backend_repo_path, "Backend", print_output)
    else:
        backend_stdout, backend_stderr = run_command(command, backend_repo_path, "Backend", print_output=False)
        frontend_stdout, frontend_stderr = run_command(command, frontend_repo_path, "Frontend", print_output=False)

        if command[1] == "commit":
            if "nothing to commit" in backend_stdout:
                print(highlight_text("Backend: nothing to commit"))
            else:
                print(highlight_text("Backend: commit successfully"))
                if print_output:
                    print(backend_stdout)

            if "nothing to commit" in frontend_stdout:
                print(highlight_text("Frontend: nothing to commit"))
            else:
                print(highlight_text("Frontend: commit successfully"))
                if print_output:
                    print(frontend_stdout)
        elif command[1] == "push":
            backend_branch_name = get_current_branch(backend_repo_path)
            frontend_branch_name = get_current_branch(frontend_repo_path)

            if "has no upstream branch" in backend_stderr:
                print(highlight_text("Backend: setting upstream branch"))
                run_command(["git", "push", "--set-upstream", "origin", backend_branch_name], backend_repo_path, "Backend")

            if "has no upstream branch" in frontend_stderr:
                print(highlight_text("Frontend: setting upstream branch"))
                run_command(["git", "push", "--set-upstream", "origin", frontend_branch_name], frontend_repo_path, "Frontend")

            backend_stdout, backend_stderr = run_command(command, backend_repo_path, "Backend", print_output=False)
            frontend_stdout, frontend_stderr = run_command(command, frontend_repo_path, "Frontend", print_output=False)

            print(highlight_text("Backend:"))
            if "Everything up-to-date" in backend_stdout:
                print("Nothing to push")
            else:
                print("Push successfully")

            print(highlight_text("Frontend:"))
            if "Everything up-to-date" in frontend_stdout:
                print("Nothing to push")
            else:
                print("Push successfully")
        else:
            if print_output:
                print(highlight_text("Backend:"))
                print(backend_stdout)
                print(highlight_text("Frontend:"))
                print(frontend_stdout)

def get_current_branch(repo_path):
    result = subprocess.run(["git", "branch", "--show-current"], cwd=repo_path, check=True, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def highlight_text(text):
    if "Frontend" in text:
        return f"{bg('green')}{text}{attr('reset')}"
    elif "Backend" in text:
        return f"{bg('red')}{text}{attr('reset')}"
    return text

def print_help():
    help_message = """
    Usage: gigit <command> [args]
    
    Commands:
      init <backend_repo_path> <frontend_repo_path>    Initialize repository paths for backend and frontend.
      front <git_command>                              Run a git command in the frontend repository.
      back <git_command>                               Run a git command in the backend repository.
      branch <branch_name>                             Create a new branch and list all branches.
      checkout <branch_name>                           Checkout a branch.
      status                                           Show the status of both repositories.
      commit -m <message>                              Commit changes in both repositories with a message.
      push                                             Push changes in both repositories.
      delete-branch <branch_name>                      Delete a branch in both repositories.
      help                                             Show this help message.

    Examples:
      gigit init ./backend ./frontend
      gigit front add .
      gigit back status
      gigit branch feature1
      gigit checkout feature1
      gigit status
      gigit commit -m "Add new feature"
      gigit push
      gigit delete-branch feature1
      gigit help
    """
    print(help_message)

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
