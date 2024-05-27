from colored import bg, attr

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
