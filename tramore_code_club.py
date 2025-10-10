#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import shutil
import datetime
from pathlib import Path

# Configuration - will be replaced during setup
REPO_NAME = "tramore-code-club-python"
GITHUB_USERNAME = "GITHUB_USERNAME_PLACEHOLDER"
REPO_URL = f"https://{GITHUB_USERNAME}:GITHUB_TOKEN_PLACEHOLDER@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
WORK_DIR = os.path.expanduser("~/Desktop/TramoreCodeClub")
BACKUP_DIR = os.path.expanduser("~/Desktop/TramoreCodeClubBackup")
MAIN_BRANCH = "main"  # The main branch name

# Make sure directories exist
os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear')

def run_command(command, working_dir=None):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            text=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            cwd=working_dir
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def setup_repository_if_needed():
    """Setup or update the repository if it doesn't exist."""
    repo_path = os.path.join(WORK_DIR, REPO_NAME)
    
    # Check if repo directory exists
    if not os.path.exists(repo_path):
        # Clone the repository
        print("Setting up code storage... please wait...")
        success, _ = run_command(f"git clone {REPO_URL}", working_dir=WORK_DIR)
        if not success:
            print("Could not connect to code storage.")
            return False
        
        # Check if Git identity is set
        _, has_name = run_command("git config --get user.name", working_dir=repo_path)
        _, has_email = run_command("git config --get user.email", working_dir=repo_path)

        # If not set, use defaults
        if not has_name.strip():
            run_command(f"git config --global user.name \"Tramore Code Club\"", working_dir=repo_path)
        if not has_email.strip():
            run_command(f"git config --global user.email \"tramore.code.club@example.com\"", working_dir=repo_path)
    
    return True

def check_student_exists(student_name):
    """Check if a student already exists by checking both folder and branch."""
    # Check locally first - does the folder exist?
    safe_name = get_safe_name(student_name)
    student_folder = os.path.join(WORK_DIR, safe_name)
    
    if os.path.exists(student_folder):
        return True
    
    # Setup repo if needed to check branches
    if not setup_repository_if_needed():
        return False
    
    # Check if the branch exists remotely
    branch_name = f"student/{safe_name}"
    repo_path = os.path.join(WORK_DIR, REPO_NAME)
    
    # Update remote info first
    run_command("git fetch", working_dir=repo_path)
    
    # Check remote branches
    success, output = run_command(f"git ls-remote --heads origin {branch_name}", working_dir=repo_path)
    if success and output.strip():
        return True
    
    # Check local branches too
    success, output = run_command(f"git branch -a | grep {branch_name}", working_dir=repo_path)
    if success and output.strip():
        return True
    
    return False

def get_safe_name(student_name):
    """Get a safe folder/branch name from a student name."""
    return student_name.lower().replace(' ', '-')

def copy_all_files(src_dir, dest_dir, exclude_dirs=None):
    """Copy all files recursively from src to dest directory, excluding certain directories."""
    if exclude_dirs is None:
        exclude_dirs = ['.git']
    
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    # Copy all files, preserving directory structure
    for item in os.listdir(src_dir):
        src_item = os.path.join(src_dir, item)
        dest_item = os.path.join(dest_dir, item)
        
        if os.path.isdir(src_item):
            if item not in exclude_dirs:
                copy_all_files(src_item, dest_item, exclude_dirs)
        else:
            shutil.copy2(src_item, dest_item)

def pull_student_files(student_name, branch_name):
    """Pull the latest files for a student and sync them to their folder."""
    print(f"Getting your latest saved files... please wait...")
    
    repo_path = os.path.join(WORK_DIR, REPO_NAME)
    safe_name = get_safe_name(student_name)
    student_folder = os.path.join(WORK_DIR, safe_name)
    repo_student_folder = os.path.join(repo_path, "students", safe_name)
    
    # Ensure repository exists
    if not os.path.exists(repo_path):
        print("Setting up code storage... please wait...")
        setup_repository_if_needed()
    
    # Checkout and pull the student branch
    run_command(f"git checkout {MAIN_BRANCH}", working_dir=repo_path)  # Start from main
    run_command("git fetch origin", working_dir=repo_path)  # Get latest branches
    
    # Check if branch exists remotely
    _, output = run_command(f"git ls-remote --heads origin {branch_name}", working_dir=repo_path)
    branch_exists_remote = bool(output.strip())
    
    if branch_exists_remote:
        # Checkout the branch, creating it if needed
        success, _ = run_command(f"git checkout {branch_name} 2>/dev/null || git checkout -b {branch_name} origin/{branch_name}", working_dir=repo_path)
        if success:
            run_command(f"git pull origin {branch_name}", working_dir=repo_path)
        
        # Create student folder if it doesn't exist
        os.makedirs(student_folder, exist_ok=True)
        
        # Check if repo student folder exists after pull
        if os.path.exists(repo_student_folder):
            # Count files before copying
            file_count = sum([len(files) for _, _, files in os.walk(repo_student_folder)])
            
            # Copy all files from repo to student folder (recursive)
            copy_all_files(repo_student_folder, student_folder)
            
            if file_count > 0:
                print(f"Found {file_count} saved files!")
    
    # If there are no files yet, create default ones
    all_files = []
    for root, _, files in os.walk(student_folder):
        all_files.extend([os.path.join(root, f) for f in files])
    
    if not all_files:
        create_student_folder(student_name)

def show_welcome_screen():
    """Show the welcome screen and get student name."""
    clear_screen()
    print("="*50)
    print("     WELCOME TO TRAMORE CODE CLUB!     ")
    print("="*50)
    
    while True:
        print("\nWhat is your name?")
        student_name = input("> ").strip()
        
        if not student_name:
            print("Please enter your name.")
            continue
        
        # Create a safe branch name from student name
        safe_name = get_safe_name(student_name)
        branch_name = f"student/{safe_name}"
        
        # Check if this is a new student - ensure repository is setup first
        setup_repository_if_needed()
        is_existing_student = check_student_exists(student_name)
        
        if not is_existing_student:
            print("\nThis name doesn't have any saved work yet.")
            print("Is this your first time here? (y/n)")
            first_time = input("> ").strip().lower()
            
            if first_time == "y":
                # Create student folder automatically for new students
                create_student_folder(student_name)
                break
            else:
                print("\nLet's try again. Please enter your name exactly as before.")
                continue
        else:
            print(f"\nWelcome back, {student_name}!")
            # Pull latest code for returning students
            pull_student_files(student_name, branch_name)
            break
    
    return student_name, branch_name

def setup_repository():
    """Setup or update the repository quietly."""
    repo_path = os.path.join(WORK_DIR, REPO_NAME)
    
    # Check if repo directory exists
    if os.path.exists(repo_path):
        # Try to pull main branch
        success, _ = run_command(f"git checkout {MAIN_BRANCH} && git pull", working_dir=repo_path)
        if not success:
            print("Updating code storage... please wait...")
            # If pull fails, delete and re-clone
            shutil.rmtree(repo_path, ignore_errors=True)
            success, _ = run_command(f"git clone {REPO_URL}", working_dir=WORK_DIR)
            if not success:
                print("Could not connect to code storage.")
                return False
    else:
        # Clone the repository
        print("Setting up code storage... please wait...")
        success, _ = run_command(f"git clone {REPO_URL}", working_dir=WORK_DIR)
        if not success:
            print("Could not connect to code storage.")
            return False
    
    # Check if Git identity is set
    _, has_name = run_command("git config --get user.name", working_dir=repo_path)
    _, has_email = run_command("git config --get user.email", working_dir=repo_path)

    # If not set, use defaults
    if not has_name.strip():
        run_command(f"git config --global user.name \"Tramore Code Club\"", working_dir=repo_path)
    if not has_email.strip():
        run_command(f"git config --global user.email \"tramore.code.club@example.com\"", working_dir=repo_path)
    
    return True

def setup_student_branch(branch_name):
    """Setup the student's branch."""
    repo_path = os.path.join(WORK_DIR, REPO_NAME)
    
    # First checkout main branch and update
    run_command(f"git checkout {MAIN_BRANCH} && git pull", working_dir=repo_path)
    
    # Check if the branch exists locally
    _, output = run_command(f"git branch --list {branch_name}", working_dir=repo_path)
    branch_exists_locally = bool(output.strip())
    
    # Check if the branch exists on remote
    _, output = run_command(f"git ls-remote --heads origin {branch_name}", working_dir=repo_path)
    branch_exists_remote = bool(output.strip())
    
    if branch_exists_remote:
        # Checkout the existing branch
        run_command(f"git checkout {branch_name}", working_dir=repo_path)
        run_command(f"git pull origin {branch_name}", working_dir=repo_path)
    elif branch_exists_locally:
        # Just checkout the local branch
        run_command(f"git checkout {branch_name}", working_dir=repo_path)
    else:
        # Create a new branch from main
        run_command(f"git checkout -b {branch_name}", working_dir=repo_path)
        
    return True

def create_student_folder(student_name):
    """Create a student folder directly under the work directory."""
    safe_name = get_safe_name(student_name)
    student_folder = os.path.join(WORK_DIR, safe_name)
    
    # Create student folder if it doesn't exist
    os.makedirs(student_folder, exist_ok=True)
    
    # Create a README file for the student
    readme_path = os.path.join(student_folder, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write(f"# {student_name}'s Python Projects\n\n")
            f.write(f"This folder contains Python projects for Tramore Code Club.\n")
    
    # Create a default Python file if none exists
    python_files = list(Path(student_folder).glob("*.py"))
    if not python_files:
        default_file = os.path.join(student_folder, f"program.py")
        with open(default_file, "w") as f:
            f.write(f"""# {student_name}'s Python Program
# Created: {datetime.datetime.now().strftime("%Y-%m-%d")}

# Write your code below this line:
print("Hello, World! My name is {student_name}!")
""")
    
    return student_folder

def get_student_folder(student_name):
    """Get path to student folder."""
    safe_name = get_safe_name(student_name)
    return os.path.join(WORK_DIR, safe_name)

def count_files_by_type(folder):
    """Count files by type in a folder and its subdirectories."""
    file_counts = {
        "python": 0,
        "text": 0,
        "other": 0,
        "total": 0,
        "dirs": 0
    }
    
    for root, dirs, files in os.walk(folder):
        file_counts["dirs"] += len(dirs)
        for file in files:
            file_counts["total"] += 1
            if file.endswith('.py'):
                file_counts["python"] += 1
            elif file.endswith('.txt'):
                file_counts["text"] += 1
            else:
                file_counts["other"] += 1
    
    return file_counts

def load_student_code(student_name):
    """Load the student's code (just print the path without opening editor)."""
    student_folder = get_student_folder(student_name)
    
    # Ensure the folder exists
    if not os.path.exists(student_folder):
        create_student_folder(student_name)
    
    # Count files by type
    file_counts = count_files_by_type(student_folder)
    
    if file_counts["total"] > 0:
        print(f"\nYour folder contains:")
        print(f"- {file_counts['python']} Python file(s)")
        print(f"- {file_counts['text']} Text file(s)")
        print(f"- {file_counts['other']} Other file(s)")
        
        if file_counts["dirs"] > 0:
            print(f"- {file_counts['dirs']} folder(s)")
        
        # Show path to student folder
        print(f"\nYour working folder is: {student_folder}")
        print("Open this folder to see all your files.")
    else:
        # Create a new file
        file_path = os.path.join(student_folder, "program.py")
        with open(file_path, "w") as f:
            f.write(f"""# Python Program
# Created: {datetime.datetime.now().strftime("%Y-%m-%d")}

print("Hello from Tramore Code Club!")
""")
        print(f"\nCreated new file: {file_path}")
    
    print(f"\nYou can find your files in: {student_folder}")
    print("Open these files with your favorite editor to start coding.")
        
    return True

def save_work(student_name, branch_name):
    """Save the student's work to GitHub."""
    repo_path = os.path.join(WORK_DIR, REPO_NAME)
    safe_name = get_safe_name(student_name)
    student_folder = get_student_folder(student_name)
    
    # Check if there are any files
    all_files = []
    for root, _, files in os.walk(student_folder):
        all_files.extend([os.path.join(root, f) for f in files])
    
    if not all_files:
        print("\nNo files found to save.")
        return False
    
    # Create a backup first
    backup_folder = os.path.join(BACKUP_DIR, safe_name, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(backup_folder, exist_ok=True)
    
    # Copy entire directory structure to backup
    copy_all_files(student_folder, backup_folder)
    
    # Copy files to the repository structure
    repo_student_folder = os.path.join(repo_path, "students", safe_name)
    
    # Ensure repository structure exists
    os.makedirs(repo_student_folder, exist_ok=True)
    
    # Copy all files from student folder to repo (recursive)
    copy_all_files(student_folder, repo_student_folder)
    
    # Add all changes
    print("\nSaving your code...")
    
    # Make sure we're on the right branch
    run_command(f"git checkout {branch_name} 2>/dev/null || git checkout -b {branch_name}", working_dir=repo_path)
    
    # Stage changes in the student's folder
    success, _ = run_command(f"git add students/{safe_name}", working_dir=repo_path)
    if not success:
        print("Could not prepare your code for saving.")
        return False
    
    # Create a commit message with student name
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"Update from {student_name} on {timestamp}"
    
    # Commit changes
    success, output = run_command(f"git commit -m \"{commit_msg}\"", working_dir=repo_path)
    
    if not success:
        # Check if it's just because there are no changes
        if "nothing to commit" in output.lower():
            print("Your code is already saved!")
            return True
        else:
            print(f"Could not save your code. Error: {output}")
            return False
    
    # Push changes to GitHub on student's branch
    print("Uploading your code to safe storage...")
    success, output = run_command(f"git push -u origin {branch_name}", working_dir=repo_path)
    if not success:
        print("Could not upload your code.")
        print("Don't worry! Your code is saved on this computer.")
        print(f"Error: {output}")
        return False
    
    print("\nYour code has been saved successfully!")
    file_counts = count_files_by_type(student_folder)
    print(f"Saved {file_counts['total']} file(s) in total.")
    return True

def show_main_menu(student_name):
    """Show the main menu and get student choice."""
    clear_screen()
    print("="*50)
    print(f"          HELLO {student_name.upper()}!          ")
    print("="*50)
    print("\nWhat would you like to do today?")
    print("\n1. Load My Code")
    print("2. Save My Code")
    print("3. Exit")
    print("\nType a number and press Enter:")
    
    choice = input("> ").strip()
    return choice

def main():
    try:
        # Get student name and branch name
        student_name, branch_name = show_welcome_screen()
        
        # Setup repository quietly
        if not setup_repository():
            print("\nCould not set up code storage. Please ask your mentor for help.")
            input("\nPress Enter to exit...")
            return
            
        # Setup student's branch
        setup_student_branch(branch_name)
        
        while True:
            choice = show_main_menu(student_name)
            
            if choice == "1":
                # Load code - load files and show information
                load_student_code(student_name)
                print("\nYour code has been loaded!")
                print("\nYou can now edit your files in your preferred editor.")
                
            elif choice == "2":
                # Save code
                save_work(student_name, branch_name)
                
            elif choice == "3":
                # Exit
                print("\nThank you for coding today!")
                print("See you next time at Tramore Code Club!")
                time.sleep(1)
                sys.exit(0)
                
            else:
                print("\nPlease type 1, 2, or 3 and press Enter.")
            
            input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"\nSomething went wrong: {str(e)}")
        print("Please ask your mentor for help.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()