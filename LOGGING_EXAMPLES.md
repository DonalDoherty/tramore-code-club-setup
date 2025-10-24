# Logging Output Examples

This document shows examples of what the log files will look like with the new logging system.

## Log File Location

Logs are saved to: `~/Desktop/TramoreCodeClub/tramore_code_club.log`

## Example Log Output

### Successful Session

```
2025-10-24 18:41:24 - TramoreCodeClub - INFO - ==================================================
2025-10-24 18:41:24 - TramoreCodeClub - INFO - Starting Tramore Code Club application
2025-10-24 18:41:24 - TramoreCodeClub - INFO - ==================================================
2025-10-24 18:41:25 - TramoreCodeClub - DEBUG - Screen cleared
2025-10-24 18:41:25 - TramoreCodeClub - INFO - Showing welcome screen
2025-10-24 18:41:30 - TramoreCodeClub - DEBUG - Converted 'John Doe' to safe name 'john-doe'
2025-10-24 18:41:30 - TramoreCodeClub - INFO - Checking if student 'John Doe' exists
2025-10-24 18:41:30 - TramoreCodeClub - DEBUG - Setting up repository at /home/user/Desktop/TramoreCodeClub/tramore-code-club-python
2025-10-24 18:41:30 - TramoreCodeClub - DEBUG - Repository exists, attempting to update
2025-10-24 18:41:31 - TramoreCodeClub - DEBUG - Running command: git checkout main && git pull in /home/user/Desktop/TramoreCodeClub/tramore-code-club-python
2025-10-24 18:41:32 - TramoreCodeClub - DEBUG - Command succeeded with output: Already up to date.
2025-10-24 18:41:32 - TramoreCodeClub - DEBUG - Configuring Git identity for /home/user/Desktop/TramoreCodeClub/tramore-code-club-python
2025-10-24 18:41:32 - TramoreCodeClub - INFO - Repository setup completed successfully
2025-10-24 18:41:32 - TramoreCodeClub - DEBUG - Running command: git fetch in /home/user/Desktop/TramoreCodeClub/tramore-code-club-python
2025-10-24 18:41:33 - TramoreCodeClub - DEBUG - Checking if branch student/john-doe exists on remote
2025-10-24 18:41:33 - TramoreCodeClub - DEBUG - Running command: git ls-remote --heads origin student/john-doe
2025-10-24 18:41:34 - TramoreCodeClub - DEBUG - Branch student/john-doe exists on remote
2025-10-24 18:41:34 - TramoreCodeClub - INFO - Student branch student/john-doe exists on remote
2025-10-24 18:41:34 - TramoreCodeClub - INFO - Returning student: John Doe
2025-10-24 18:41:34 - TramoreCodeClub - INFO - Pulling files for student 'John Doe' from branch 'student/john-doe'
2025-10-24 18:41:35 - TramoreCodeClub - DEBUG - Copied 5 files to /home/user/Desktop/TramoreCodeClub/john-doe
2025-10-24 18:41:35 - TramoreCodeClub - INFO - Copied 5 files to /home/user/Desktop/TramoreCodeClub/john-doe
2025-10-24 18:41:35 - TramoreCodeClub - INFO - Student logged in: John Doe, branch: student/john-doe
2025-10-24 18:41:35 - TramoreCodeClub - INFO - Setting up student branch: student/john-doe
2025-10-24 18:41:36 - TramoreCodeClub - INFO - Branch student/john-doe is ready
2025-10-24 18:41:37 - TramoreCodeClub - DEBUG - User selected menu option: 1
2025-10-24 18:41:37 - TramoreCodeClub - INFO - User selected: Load My Code
2025-10-24 18:41:37 - TramoreCodeClub - INFO - Loading code for student: John Doe
2025-10-24 18:41:37 - TramoreCodeClub - DEBUG - Counting files in /home/user/Desktop/TramoreCodeClub/john-doe
2025-10-24 18:41:37 - TramoreCodeClub - DEBUG - File counts: {'python': 3, 'text': 1, 'other': 1, 'total': 5, 'dirs': 0}
2025-10-24 18:41:37 - TramoreCodeClub - INFO - Loaded 5 files for John Doe
2025-10-24 18:42:15 - TramoreCodeClub - DEBUG - User selected menu option: 2
2025-10-24 18:42:15 - TramoreCodeClub - INFO - User selected: Save My Code
2025-10-24 18:42:15 - TramoreCodeClub - INFO - Saving work for student 'John Doe' to branch 'student/john-doe'
2025-10-24 18:42:15 - TramoreCodeClub - DEBUG - Copying files from /home/user/Desktop/TramoreCodeClub/john-doe to /home/user/Desktop/TramoreCodeClubBackup/john-doe/20251024_184215
2025-10-24 18:42:15 - TramoreCodeClub - DEBUG - Copied 5 files from /home/user/Desktop/TramoreCodeClub/john-doe to /home/user/Desktop/TramoreCodeClubBackup/john-doe/20251024_184215
2025-10-24 18:42:15 - TramoreCodeClub - INFO - Created backup at /home/user/Desktop/TramoreCodeClubBackup/john-doe/20251024_184215 with 5 files
2025-10-24 18:42:15 - TramoreCodeClub - INFO - Copied 5 files to repository
2025-10-24 18:42:16 - TramoreCodeClub - DEBUG - Running command: git commit -m "Update from John Doe on 2025-10-24 18:42"
2025-10-24 18:42:17 - TramoreCodeClub - DEBUG - Running command: git push -u origin student/john-doe
2025-10-24 18:42:18 - TramoreCodeClub - INFO - Successfully saved 5 files for John Doe
2025-10-24 18:42:30 - TramoreCodeClub - DEBUG - User selected menu option: 3
2025-10-24 18:42:30 - TramoreCodeClub - INFO - User selected: Exit
2025-10-24 18:42:31 - TramoreCodeClub - INFO - Application exiting normally
2025-10-24 18:42:31 - TramoreCodeClub - INFO - Application terminated
```

### Session with Error

```
2025-10-24 18:45:12 - TramoreCodeClub - INFO - Starting Tramore Code Club application
2025-10-24 18:45:12 - TramoreCodeClub - INFO - Showing welcome screen
2025-10-24 18:45:18 - TramoreCodeClub - WARNING - Empty student name provided
2025-10-24 18:45:23 - TramoreCodeClub - INFO - Checking if student 'Jane Smith' exists
2025-10-24 18:45:23 - TramoreCodeClub - DEBUG - Setting up repository at /home/user/Desktop/TramoreCodeClub/tramore-code-club-python
2025-10-24 18:45:23 - TramoreCodeClub - DEBUG - Running command: git checkout main && git pull
2025-10-24 18:45:24 - TramoreCodeClub - ERROR - Command failed: git checkout main && git pull
2025-10-24 18:45:24 - TramoreCodeClub - ERROR - Error output: fatal: unable to access 'https://...': Could not resolve host: github.com
2025-10-24 18:45:24 - TramoreCodeClub - WARNING - Pull failed, re-cloning repository. Error: fatal: unable to access...
2025-10-24 18:45:24 - TramoreCodeClub - INFO - Cloning repository to /home/user/Desktop/TramoreCodeClub
2025-10-24 18:45:25 - TramoreCodeClub - ERROR - Failed to clone repository: fatal: unable to access...
2025-10-24 18:45:25 - TramoreCodeClub - ERROR - Failed to setup repository in main
```

### First-Time Student

```
2025-10-24 18:50:00 - TramoreCodeClub - INFO - Starting Tramore Code Club application
2025-10-24 18:50:00 - TramoreCodeClub - INFO - Showing welcome screen
2025-10-24 18:50:10 - TramoreCodeClub - DEBUG - Converted 'Alice Brown' to safe name 'alice-brown'
2025-10-24 18:50:10 - TramoreCodeClub - INFO - Checking if student 'Alice Brown' exists
2025-10-24 18:50:11 - TramoreCodeClub - INFO - Student 'Alice Brown' does not exist
2025-10-24 18:50:15 - TramoreCodeClub - INFO - New student: Alice Brown
2025-10-24 18:50:15 - TramoreCodeClub - INFO - Creating folder for student: Alice Brown
2025-10-24 18:50:15 - TramoreCodeClub - DEBUG - Created directory: /home/user/Desktop/TramoreCodeClub/alice-brown
2025-10-24 18:50:15 - TramoreCodeClub - DEBUG - Created README at /home/user/Desktop/TramoreCodeClub/alice-brown/README.md
2025-10-24 18:50:15 - TramoreCodeClub - DEBUG - Created default Python file at /home/user/Desktop/TramoreCodeClub/alice-brown/program.py
2025-10-24 18:50:15 - TramoreCodeClub - INFO - Student folder created successfully at /home/user/Desktop/TramoreCodeClub/alice-brown
2025-10-24 18:50:15 - TramoreCodeClub - INFO - Student logged in: Alice Brown, branch: student/alice-brown
```

## Log Levels

The logging system uses these levels:

- **DEBUG**: Detailed information for debugging (git commands, file operations, etc.)
- **INFO**: General information about program flow (user actions, successful operations)
- **WARNING**: Something unexpected happened but the program continues (empty input, non-critical errors)
- **ERROR**: A serious problem that prevented an operation from completing
- **EXCEPTION**: An error with full stack trace

## Console vs File Logging

- **Console**: Only shows WARNING and ERROR messages to avoid cluttering the terminal
- **Log File**: Shows all levels (DEBUG and above) for comprehensive debugging

## Benefits of Logging

1. **Debugging**: See exactly what happened when something goes wrong
2. **User Support**: Students can share logs with mentors for troubleshooting
3. **Audit Trail**: Track all operations and changes over time
4. **Performance**: Identify slow operations by reviewing timestamps
5. **Security**: Log suspicious activities or unauthorized access attempts

## Accessing Logs

### On Linux/Ubuntu:
```bash
# View the log file
cat ~/Desktop/TramoreCodeClub/tramore_code_club.log

# View last 50 lines
tail -n 50 ~/Desktop/TramoreCodeClub/tramore_code_club.log

# Follow log in real-time
tail -f ~/Desktop/TramoreCodeClub/tramore_code_club.log

# Search for errors
grep ERROR ~/Desktop/TramoreCodeClub/tramore_code_club.log
```

### Size Management

The log file grows over time. To manage size:
- The file is plain text and compresses well
- Can be manually deleted when it gets too large
- Consider implementing log rotation in future versions
