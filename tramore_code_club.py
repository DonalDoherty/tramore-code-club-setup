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

def check_branch_exists(branch_name):
    """Check if a branch exists on remote."""
    repo_path = os.path.join(WORK_DIR, REPO_NAME)
    if not os.path.exists(repo_path):
        return False
        
    _, output = run_command(f"git ls-remote --heads origin {branch_name}", working_dir=repo_path)
    return bool(output.strip())

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
        branch_name = f"student/{student_name.lower().replace(' ', '-')}"
        
        # Check if this is a new student
        if not check_branch_exists(branch_name):
            print("\nThis name doesn't have any saved work yet.")
            print("Is this your first time here? (y/n)")
            first_time = input("> ").strip().lower()
            
            if first_time == "y":
                break
            else:
                print("\nLet's try again. Please enter your name exactly as before.")
                continue
        else:
            print(f"\nWelcome back, {student_name}!")
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

def ensure_student_folder(student_name):
    """Ensure the student folder exists in the repository."""
    repo_path = os.path.join(WORK_DIR, REPO_NAME)
    # Use student name directly for the folder
    safe_name = student_name.lower().replace(' ', '-')
    student_folder = os.path.join(repo_path, "students", safe_name)
    
    # Create student folder if it doesn't exist
    os.makedirs(student_folder, exist_ok=True)
    
    # Create a README file for the student
    readme_path = os.path.join(student_folder, "README.md")
    if not os.path.exists(readme_path):
        with open(readme_path, "w") as f:
            f.write(f"# {student_name}'s Python Projects\n\n")
            f.write(f"This folder contains Python projects for Tramore Code Club.\n")
    
    # Create a default Python file if none exists
    files = list(Path(student_folder).glob("*.py"))
    if not files:
        default_file = os.path.join(student_folder, f"program.py")
        with open(default_file, "w") as f:
            f.write(f"""# {student_name}'s Python Program
# Created: {datetime.datetime.now().strftime("%Y-%m-%d")}

# Write your code below this line:
print("Hello, World! My name is {student_name}!")
""")
    
    return student_folder

def open_mu_editor(folder_path, student_name):
    """Open Mu editor with the student's most recent Python file."""
    files = list(Path(folder_path).glob("*.py"))
    
    if files:
        # Find the most recently modified Python file
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        file_path = str(latest_file)
    else:
        # Create a new file
        file_path = os.path.join(folder_path, "program.py")
        with open(file_path, "w") as f:
            f.write(f"""# {student_name}'s Python Program
# Created: {datetime.datetime.now().strftime("%Y-%m-%d")}

print("Hello from Tramore Code Club!")
""")
    
    # Launch Mu editor
    print(f"\nOpening your code in Mu editor...")
    try:
        subprocess.Popen(["mu-editor", file_path], start_new_session=True)
    except FileNotFoundError:
        print("\nCould not find Mu editor. Please ask your mentor for help.")
        return False
        
    return True

def save_work(student_name, branch_name):
    """Save the student's work to GitHub."""
    repo_path = os.path.join(WORK_DIR, REPO_NAME)
    safe_name = student_name.lower().replace(' ', '-')
    student_folder = os.path.join(repo_path, "students", safe_name)
    
    # Check if there are any Python files
    files = list(Path(student_folder).glob("*.py"))
    if not files:
        print("\nNo Python files found to save.")
        return False
    
    # Create a backup first
    backup_folder = os.path.join(BACKUP_DIR, safe_name, datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    os.makedirs(backup_folder, exist_ok=True)
    for file in files:
        shutil.copy2(file, backup_folder)
    
    # Add all changes
    print("\nSaving your code...")
    
    # Stage changes in the student's folder
    success, _ = run_command(f"git add students/{safe_name}", working_dir=repo_path)
    if not success:
        print("Could not prepare your code for saving.")
        return False
    
    # Create a commit message with student name
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    commit_msg = f"Update from {student_name} on {timestamp}"
    
    # Commit changes
    success, _ = run_command(f"git commit -m \"{commit_msg}\"", working_dir=repo_path)
    if not success:
        # No changes to commit
        print("Your code is already saved!")
        return True
    
    # Push changes to GitHub on student's branch
    print("Uploading your code to safe storage...")
    success, output = run_command(f"git push -u origin {branch_name}", working_dir=repo_path)
    if not success:
        print("Could not upload your code.")
        print("Don't worry! Your code is saved on this computer.")
        return False
    
    print("\nYour code has been saved successfully!")
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
                # Load code
                student_folder = ensure_student_folder(student_name)
                if open_mu_editor(student_folder, student_name):
                    print("\nYour code has been loaded!")
                    print("\nWork on your code in the Mu editor window.")
                    print("When you're done, come back here and choose 'Save My Code'.")
                
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
        print(f"\nSomething went wrong: {e}")
        print("Please ask your mentor for help.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()