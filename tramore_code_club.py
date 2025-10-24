#!/usr/bin/env python3

import os
import sys
import subprocess
import time
import shutil
import datetime
import logging
from pathlib import Path
from typing import Tuple, Optional, Dict

# Configuration - will be replaced during setup
REPO_NAME = "tramore-code-club-python"
GITHUB_USERNAME = "GITHUB_USERNAME_PLACEHOLDER"
REPO_URL = f"https://{GITHUB_USERNAME}:GITHUB_TOKEN_PLACEHOLDER@github.com/{GITHUB_USERNAME}/{REPO_NAME}.git"
WORK_DIR = os.path.expanduser("~/Desktop/TramoreCodeClub")
BACKUP_DIR = os.path.expanduser("~/Desktop/TramoreCodeClubBackup")
LOG_DIR = os.path.expanduser("~/Desktop/TramoreCodeClub")
MAIN_BRANCH = "main"
STUDENT_BRANCH_PREFIX = "student/"
STUDENTS_SUBDIR = "students"
DEFAULT_GIT_NAME = "Tramore Code Club"
DEFAULT_GIT_EMAIL = "tramore.code.club@example.com"
EXCLUDE_DIRS = ['.git']

# Make sure directories exist
os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Setup logging
def setup_logging():
    """Configure logging with both file and console handlers."""
    log_file = os.path.join(LOG_DIR, "tramore_code_club.log")

    # Create logger
    logger = logging.getLogger("TramoreCodeClub")
    logger.setLevel(logging.DEBUG)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # File handler - detailed logging
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler - only errors and warnings
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

logger = setup_logging()

def clear_screen():
    """Clear the terminal screen."""
    os.system('clear')
    logger.debug("Screen cleared")

def run_command(command: str, working_dir: Optional[str] = None) -> Tuple[bool, str]:
    """Run a shell command and return the output.

    Args:
        command: Shell command to execute
        working_dir: Directory to run command in (optional)

    Returns:
        Tuple of (success: bool, output: str)
    """
    logger.debug(f"Running command: {command} in {working_dir or 'current directory'}")
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
        logger.debug(f"Command succeeded with output: {result.stdout[:100]}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {command}")
        logger.error(f"Error output: {e.stderr}")
        return False, e.stderr
    except Exception as e:
        logger.exception(f"Unexpected error running command: {command}")
        return False, str(e)

def configure_git_identity(repo_path: str) -> bool:
    """Configure Git identity if not already set.

    Args:
        repo_path: Path to the git repository

    Returns:
        True if configuration was successful or already set
    """
    logger.debug(f"Configuring Git identity for {repo_path}")
    try:
        _, has_name = run_command("git config --get user.name", working_dir=repo_path)
        _, has_email = run_command("git config --get user.email", working_dir=repo_path)

        # If not set, use defaults
        if not has_name.strip():
            logger.info(f"Setting default Git name: {DEFAULT_GIT_NAME}")
            run_command(f"git config --global user.name \"{DEFAULT_GIT_NAME}\"", working_dir=repo_path)
        if not has_email.strip():
            logger.info(f"Setting default Git email: {DEFAULT_GIT_EMAIL}")
            run_command(f"git config --global user.email \"{DEFAULT_GIT_EMAIL}\"", working_dir=repo_path)

        return True
    except Exception as e:
        logger.exception("Failed to configure Git identity")
        return False

def clone_repository(target_dir: str) -> bool:
    """Clone the repository to the target directory.

    Args:
        target_dir: Directory where repository should be cloned

    Returns:
        True if clone was successful
    """
    logger.info(f"Cloning repository to {target_dir}")
    print("Setting up code storage... please wait...")
    success, output = run_command(f"git clone {REPO_URL}", working_dir=target_dir)
    if not success:
        logger.error(f"Failed to clone repository: {output}")
        print("Could not connect to code storage.")
        return False
    logger.info("Repository cloned successfully")
    return True

def setup_repository() -> bool:
    """Setup or update the repository.

    This function handles both initial clone and updates of existing repository.

    Returns:
        True if repository is ready to use
    """
    repo_path = os.path.join(WORK_DIR, REPO_NAME)
    logger.debug(f"Setting up repository at {repo_path}")

    # Check if repo directory exists
    if os.path.exists(repo_path):
        logger.debug("Repository exists, attempting to update")
        # Try to pull main branch
        success, output = run_command(f"git checkout {MAIN_BRANCH} && git pull", working_dir=repo_path)
        if not success:
            logger.warning(f"Pull failed, re-cloning repository. Error: {output}")
            print("Updating code storage... please wait...")
            # If pull fails, delete and re-clone
            try:
                shutil.rmtree(repo_path, ignore_errors=True)
                logger.info("Removed old repository directory")
            except Exception as e:
                logger.exception(f"Failed to remove old repository: {e}")

            if not clone_repository(WORK_DIR):
                return False
    else:
        logger.debug("Repository doesn't exist, cloning")
        if not clone_repository(WORK_DIR):
            return False

    # Configure Git identity
    if not configure_git_identity(repo_path):
        logger.warning("Git identity configuration failed, but continuing")

    logger.info("Repository setup completed successfully")
    return True

def branch_exists_remote(branch_name: str, repo_path: str) -> bool:
    """Check if a branch exists on the remote repository.

    Args:
        branch_name: Name of the branch to check
        repo_path: Path to the local repository

    Returns:
        True if branch exists on remote
    """
    logger.debug(f"Checking if branch {branch_name} exists on remote")
    success, output = run_command(f"git ls-remote --heads origin {branch_name}", working_dir=repo_path)
    exists = success and bool(output.strip())
    logger.debug(f"Branch {branch_name} {'exists' if exists else 'does not exist'} on remote")
    return exists

def branch_exists_local(branch_name: str, repo_path: str) -> bool:
    """Check if a branch exists locally.

    Args:
        branch_name: Name of the branch to check
        repo_path: Path to the local repository

    Returns:
        True if branch exists locally
    """
    logger.debug(f"Checking if branch {branch_name} exists locally")
    success, output = run_command(f"git branch --list {branch_name}", working_dir=repo_path)
    exists = success and bool(output.strip())
    logger.debug(f"Branch {branch_name} {'exists' if exists else 'does not exist'} locally")
    return exists

def get_safe_name(student_name: str) -> str:
    """Get a safe folder/branch name from a student name.

    Args:
        student_name: The student's name

    Returns:
        Sanitized name safe for filesystem and git
    """
    if not student_name or not student_name.strip():
        logger.warning("Empty student name provided")
        return "unknown"

    safe = student_name.lower().replace(' ', '-')
    logger.debug(f"Converted '{student_name}' to safe name '{safe}'")
    return safe

def check_student_exists(student_name: str) -> bool:
    """Check if a student already exists by checking both folder and branch.

    Args:
        student_name: The student's name

    Returns:
        True if student exists (has folder or branch)
    """
    logger.info(f"Checking if student '{student_name}' exists")
    # Check locally first - does the folder exist?
    safe_name = get_safe_name(student_name)
    student_folder = os.path.join(WORK_DIR, safe_name)

    if os.path.exists(student_folder):
        logger.info(f"Student folder exists at {student_folder}")
        return True

    # Setup repo if needed to check branches
    if not setup_repository():
        logger.error("Failed to setup repository for student check")
        return False

    # Check if the branch exists remotely
    branch_name = f"{STUDENT_BRANCH_PREFIX}{safe_name}"
    repo_path = os.path.join(WORK_DIR, REPO_NAME)

    # Update remote info first
    run_command("git fetch", working_dir=repo_path)

    # Check remote branches
    if branch_exists_remote(branch_name, repo_path):
        logger.info(f"Student branch {branch_name} exists on remote")
        return True

    # Check local branches too
    if branch_exists_local(branch_name, repo_path):
        logger.info(f"Student branch {branch_name} exists locally")
        return True

    logger.info(f"Student '{student_name}' does not exist")
    return False

def copy_all_files(src_dir: str, dest_dir: str, exclude_dirs: Optional[list] = None) -> int:
    """Copy all files recursively from src to dest directory, excluding certain directories.

    Args:
        src_dir: Source directory
        dest_dir: Destination directory
        exclude_dirs: List of directory names to exclude (default: ['.git'])

    Returns:
        Number of files copied
    """
    if exclude_dirs is None:
        exclude_dirs = EXCLUDE_DIRS

    logger.debug(f"Copying files from {src_dir} to {dest_dir}, excluding {exclude_dirs}")

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
        logger.debug(f"Created destination directory {dest_dir}")

    file_count = 0
    # Copy all files, preserving directory structure
    try:
        for item in os.listdir(src_dir):
            src_item = os.path.join(src_dir, item)
            dest_item = os.path.join(dest_dir, item)

            if os.path.isdir(src_item):
                if item not in exclude_dirs:
                    file_count += copy_all_files(src_item, dest_item, exclude_dirs)
            else:
                shutil.copy2(src_item, dest_item)
                file_count += 1

        logger.debug(f"Copied {file_count} files from {src_dir} to {dest_dir}")
        return file_count
    except Exception as e:
        logger.exception(f"Error copying files from {src_dir} to {dest_dir}: {e}")
        return file_count

def pull_student_files(student_name: str, branch_name: str):
    """Pull the latest files for a student and sync them to their folder.

    Args:
        student_name: The student's name
        branch_name: The git branch name for this student
    """
    logger.info(f"Pulling files for student '{student_name}' from branch '{branch_name}'")
    print(f"Getting your latest saved files... please wait...")

    repo_path = os.path.join(WORK_DIR, REPO_NAME)
    safe_name = get_safe_name(student_name)
    student_folder = os.path.join(WORK_DIR, safe_name)
    repo_student_folder = os.path.join(repo_path, STUDENTS_SUBDIR, safe_name)

    # Ensure repository exists
    if not os.path.exists(repo_path):
        logger.warning("Repository doesn't exist, setting up")
        print("Setting up code storage... please wait...")
        if not setup_repository():
            logger.error("Failed to setup repository")
            return

    # Checkout and pull the student branch
    run_command(f"git checkout {MAIN_BRANCH}", working_dir=repo_path)  # Start from main
    run_command("git fetch origin", working_dir=repo_path)  # Get latest branches

    # Check if branch exists remotely
    if branch_exists_remote(branch_name, repo_path):
        # Checkout the branch, creating it if needed
        success, output = run_command(
            f"git checkout {branch_name} 2>/dev/null || git checkout -b {branch_name} origin/{branch_name}",
            working_dir=repo_path
        )
        if success:
            run_command(f"git pull origin {branch_name}", working_dir=repo_path)
            logger.info(f"Checked out and pulled branch {branch_name}")
        else:
            logger.error(f"Failed to checkout branch {branch_name}: {output}")

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
                logger.info(f"Copied {file_count} files to {student_folder}")

    # If there are no files yet, create default ones
    all_files = []
    for root, _, files in os.walk(student_folder):
        all_files.extend([os.path.join(root, f) for f in files])

    if not all_files:
        logger.info("No files found, creating default student folder")
        create_student_folder(student_name)

def show_welcome_screen() -> Tuple[str, str]:
    """Show the welcome screen and get student name.

    Returns:
        Tuple of (student_name, branch_name)
    """
    logger.info("Showing welcome screen")
    clear_screen()
    print("="*50)
    print("     WELCOME TO TRAMORE CODE CLUB!     ")
    print("="*50)

    while True:
        print("\nWhat is your name?")
        student_name = input("> ").strip()

        if not student_name:
            print("Please enter your name.")
            logger.warning("Empty name entered")
            continue

        # Create a safe branch name from student name
        safe_name = get_safe_name(student_name)
        branch_name = f"{STUDENT_BRANCH_PREFIX}{safe_name}"

        # Check if this is a new student - ensure repository is setup first
        if not setup_repository():
            logger.error("Failed to setup repository during welcome")
            print("\nCould not set up code storage. Please ask your mentor for help.")
            continue

        is_existing_student = check_student_exists(student_name)

        if not is_existing_student:
            print("\nThis name doesn't have any saved work yet.")
            print("Is this your first time here? (y/n)")
            first_time = input("> ").strip().lower()

            if first_time == "y":
                logger.info(f"New student: {student_name}")
                # Create student folder automatically for new students
                create_student_folder(student_name)
                break
            else:
                print("\nLet's try again. Please enter your name exactly as before.")
                logger.info(f"Student name not found, asking to retry: {student_name}")
                continue
        else:
            print(f"\nWelcome back, {student_name}!")
            logger.info(f"Returning student: {student_name}")
            # Pull latest code for returning students
            pull_student_files(student_name, branch_name)
            break

    return student_name, branch_name

def setup_student_branch(branch_name: str) -> bool:
    """Setup the student's branch.

    Args:
        branch_name: The git branch name to setup

    Returns:
        True if branch setup was successful
    """
    logger.info(f"Setting up student branch: {branch_name}")
    repo_path = os.path.join(WORK_DIR, REPO_NAME)

    # First checkout main branch and update
    success, output = run_command(f"git checkout {MAIN_BRANCH} && git pull", working_dir=repo_path)
    if not success:
        logger.error(f"Failed to checkout/pull main branch: {output}")

    # Check if the branch exists locally
    if branch_exists_local(branch_name, repo_path):
        logger.debug(f"Branch {branch_name} exists locally")
        # Just checkout the local branch
        run_command(f"git checkout {branch_name}", working_dir=repo_path)
    # Check if the branch exists on remote
    elif branch_exists_remote(branch_name, repo_path):
        logger.debug(f"Branch {branch_name} exists on remote")
        # Checkout the existing branch
        run_command(f"git checkout {branch_name}", working_dir=repo_path)
        run_command(f"git pull origin {branch_name}", working_dir=repo_path)
    else:
        logger.debug(f"Branch {branch_name} doesn't exist, creating new")
        # Create a new branch from main
        run_command(f"git checkout -b {branch_name}", working_dir=repo_path)

    logger.info(f"Branch {branch_name} is ready")
    return True

def create_student_folder(student_name: str) -> str:
    """Create a student folder directly under the work directory.

    Args:
        student_name: The student's name

    Returns:
        Path to the created student folder
    """
    logger.info(f"Creating folder for student: {student_name}")
    safe_name = get_safe_name(student_name)
    student_folder = os.path.join(WORK_DIR, safe_name)

    # Create student folder if it doesn't exist
    try:
        os.makedirs(student_folder, exist_ok=True)
        logger.debug(f"Created directory: {student_folder}")
    except Exception as e:
        logger.exception(f"Failed to create student folder: {e}")
        raise

    # Create a README file for the student
    readme_path = os.path.join(student_folder, "README.md")
    if not os.path.exists(readme_path):
        try:
            with open(readme_path, "w") as f:
                f.write(f"# {student_name}'s Python Projects\n\n")
                f.write("This folder contains Python projects for Tramore Code Club.\n")
            logger.debug(f"Created README at {readme_path}")
        except IOError as e:
            logger.exception(f"Failed to create README: {e}")

    # Create a default Python file if none exists
    python_files = list(Path(student_folder).glob("*.py"))
    if not python_files:
        default_file = os.path.join(student_folder, "program.py")
        try:
            with open(default_file, "w", encoding="utf-8") as f:
                f.write(f"""# {student_name}'s Python Program
# Created: {datetime.datetime.now().strftime("%Y-%m-%d")}

# Write your code below this line:
print("Hello, World! My name is {student_name}!")
""")
            logger.debug(f"Created default Python file at {default_file}")
        except IOError as e:
            logger.exception(f"Failed to create default Python file: {e}")

    logger.info(f"Student folder created successfully at {student_folder}")
    return student_folder

def get_student_folder(student_name: str) -> str:
    """Get path to student folder.

    Args:
        student_name: The student's name

    Returns:
        Path to the student's folder
    """
    safe_name = get_safe_name(student_name)
    return os.path.join(WORK_DIR, safe_name)

def count_files_by_type(folder: str) -> Dict[str, int]:
    """Count files by type in a folder and its subdirectories.

    Args:
        folder: Path to the folder to analyze

    Returns:
        Dictionary with counts for different file types
    """
    logger.debug(f"Counting files in {folder}")
    file_counts = {
        "python": 0,
        "text": 0,
        "other": 0,
        "total": 0,
        "dirs": 0
    }

    try:
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

        logger.debug(f"File counts: {file_counts}")
    except Exception as e:
        logger.exception(f"Error counting files in {folder}: {e}")

    return file_counts

def load_student_code(student_name: str) -> bool:
    """Load the student's code (just print the path without opening editor).

    Args:
        student_name: The student's name

    Returns:
        True if successful
    """
    logger.info(f"Loading code for student: {student_name}")
    student_folder = get_student_folder(student_name)

    # Ensure the folder exists
    if not os.path.exists(student_folder):
        logger.info(f"Student folder doesn't exist, creating: {student_folder}")
        create_student_folder(student_name)

    # Count files by type
    file_counts = count_files_by_type(student_folder)

    if file_counts["total"] > 0:
        print("\nYour folder contains:")
        print(f"- {file_counts['python']} Python file(s)")
        print(f"- {file_counts['text']} Text file(s)")
        print(f"- {file_counts['other']} Other file(s)")

        if file_counts["dirs"] > 0:
            print(f"- {file_counts['dirs']} folder(s)")

        # Show path to student folder
        print(f"\nYour working folder is: {student_folder}")
        print("Open this folder to see all your files.")
        logger.info(f"Loaded {file_counts['total']} files for {student_name}")
    else:
        # Create a new file
        file_path = os.path.join(student_folder, "program.py")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(f"""# Python Program
# Created: {datetime.datetime.now().strftime("%Y-%m-%d")}

print("Hello from Tramore Code Club!")
""")
            print(f"\nCreated new file: {file_path}")
            logger.info(f"Created new file for {student_name}: {file_path}")
        except IOError as e:
            logger.exception(f"Failed to create new file: {e}")
            return False

    print(f"\nYou can find your files in: {student_folder}")
    print("Open these files with your favorite editor to start coding.")

    return True

def create_backup(student_folder: str, safe_name: str) -> Optional[str]:
    """Create a backup of student files.

    Args:
        student_folder: Path to student's folder
        safe_name: Safe name for the student

    Returns:
        Path to backup folder if successful, None otherwise
    """
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = os.path.join(BACKUP_DIR, safe_name, timestamp)
        os.makedirs(backup_folder, exist_ok=True)

        # Copy entire directory structure to backup
        file_count = copy_all_files(student_folder, backup_folder)
        logger.info(f"Created backup at {backup_folder} with {file_count} files")
        return backup_folder
    except Exception as e:
        logger.exception(f"Failed to create backup: {e}")
        return None

def save_work(student_name: str, branch_name: str) -> bool:
    """Save the student's work to GitHub.

    Args:
        student_name: The student's name
        branch_name: The git branch name for this student

    Returns:
        True if save was successful
    """
    logger.info(f"Saving work for student '{student_name}' to branch '{branch_name}'")
    repo_path = os.path.join(WORK_DIR, REPO_NAME)
    safe_name = get_safe_name(student_name)
    student_folder = get_student_folder(student_name)

    # Check if there are any files
    all_files = []
    for root, _, files in os.walk(student_folder):
        all_files.extend([os.path.join(root, f) for f in files])

    if not all_files:
        print("\nNo files found to save.")
        logger.warning(f"No files to save for {student_name}")
        return False

    # Create a backup first
    backup_path = create_backup(student_folder, safe_name)
    if backup_path:
        logger.info(f"Backup created at {backup_path}")
    else:
        logger.warning("Backup creation failed, but continuing with save")

    # Copy files to the repository structure
    repo_student_folder = os.path.join(repo_path, STUDENTS_SUBDIR, safe_name)

    # Ensure repository structure exists
    try:
        os.makedirs(repo_student_folder, exist_ok=True)
        logger.debug(f"Ensured repo student folder exists: {repo_student_folder}")
    except Exception as e:
        logger.exception(f"Failed to create repo student folder: {e}")
        return False

    # Copy all files from student folder to repo (recursive)
    file_count = copy_all_files(student_folder, repo_student_folder)
    logger.info(f"Copied {file_count} files to repository")

    # Add all changes
    print("\nSaving your code...")

    # Make sure we're on the right branch
    success, output = run_command(
        f"git checkout {branch_name} 2>/dev/null || git checkout -b {branch_name}",
        working_dir=repo_path
    )
    if not success:
        logger.error(f"Failed to checkout branch: {output}")

    # Stage changes in the student's folder
    success, output = run_command(f"git add {STUDENTS_SUBDIR}/{safe_name}", working_dir=repo_path)
    if not success:
        print("Could not prepare your code for saving.")
        logger.error(f"Failed to stage changes: {output}")
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
            logger.info("No changes to commit")
            return True
        else:
            print(f"Could not save your code. Error: {output}")
            logger.error(f"Commit failed: {output}")
            return False

    # Push changes to GitHub on student's branch
    print("Uploading your code to safe storage...")
    success, output = run_command(f"git push -u origin {branch_name}", working_dir=repo_path)
    if not success:
        print("Could not upload your code.")
        print("Don't worry! Your code is saved on this computer.")
        print(f"Error: {output}")
        logger.error(f"Push failed: {output}")
        return False

    print("\nYour code has been saved successfully!")
    file_counts = count_files_by_type(student_folder)
    print(f"Saved {file_counts['total']} file(s) in total.")
    logger.info(f"Successfully saved {file_counts['total']} files for {student_name}")
    return True

def show_main_menu(student_name: str) -> str:
    """Show the main menu and get student choice.

    Args:
        student_name: The student's name

    Returns:
        The user's menu choice
    """
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
    logger.debug(f"User selected menu option: {choice}")
    return choice

def main():
    """Main entry point for the application."""
    logger.info("=" * 50)
    logger.info("Starting Tramore Code Club application")
    logger.info("=" * 50)

    try:
        # Get student name and branch name
        student_name, branch_name = show_welcome_screen()
        logger.info(f"Student logged in: {student_name}, branch: {branch_name}")

        # Setup repository quietly
        if not setup_repository():
            print("\nCould not set up code storage. Please ask your mentor for help.")
            logger.error("Failed to setup repository in main")
            input("\nPress Enter to exit...")
            return

        # Setup student's branch
        if not setup_student_branch(branch_name):
            logger.error(f"Failed to setup branch {branch_name}")

        while True:
            choice = show_main_menu(student_name)

            if choice == "1":
                # Load code - load files and show information
                logger.info("User selected: Load My Code")
                if load_student_code(student_name):
                    print("\nYour code has been loaded!")
                    print("\nYou can now edit your files in your preferred editor.")
                else:
                    logger.error("Failed to load student code")

            elif choice == "2":
                # Save code
                logger.info("User selected: Save My Code")
                save_work(student_name, branch_name)

            elif choice == "3":
                # Exit
                logger.info("User selected: Exit")
                print("\nThank you for coding today!")
                print("See you next time at Tramore Code Club!")
                time.sleep(1)
                logger.info("Application exiting normally")
                sys.exit(0)

            else:
                print("\nPlease type 1, 2, or 3 and press Enter.")
                logger.warning(f"Invalid menu choice: {choice}")

            input("\nPress Enter to continue...")

    except KeyboardInterrupt:
        print("\nGoodbye!")
        logger.info("Application interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\nSomething went wrong: {str(e)}")
        print("Please ask your mentor for help.")
        logger.exception(f"Unhandled exception in main: {e}")

    input("\nPress Enter to exit...")
    logger.info("Application terminated")

if __name__ == "__main__":
    main()