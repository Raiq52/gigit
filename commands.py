import subprocess
from utils import highlight_text

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
            handle_commit(backend_stdout, frontend_stdout, print_output)
        elif command[1] == "push":
            handle_push(command, backend_repo_path, frontend_repo_path, backend_stderr, frontend_stderr, print_output)
        else:
            if print_output:
                print(highlight_text("Backend:"))
                print(backend_stdout)
                print(highlight_text("Frontend:"))
                print(frontend_stdout)

def handle_commit(backend_stdout, frontend_stdout, print_output):
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

def handle_push(command, backend_repo_path, frontend_repo_path, backend_stderr, frontend_stderr, print_output):
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

def get_current_branch(repo_path):
    result = subprocess.run(["git", "branch", "--show-current"], cwd=repo_path, check=True, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()
