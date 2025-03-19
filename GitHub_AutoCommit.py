import os
from GitHub_PushToken import Token
import tkinter as tk
from tkinter import simpledialog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class GitAutoCommit(FileSystemEventHandler):
    def __init__(self):
        self.modifications = {}
        self.owner = "KrisshDiwedy38"
        self.repo = "GitHub-AutoPush"
        self.branch = "main"
        self.token = Token
        self.header = {
            'Authorization': f'Bearer {self.token}',
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        self.path = os.getcwd()
        # Initialize git repo if not already done
        self._ensure_git_repo()
        
    def _ensure_git_repo(self):
        """Ensure we're in a git repository, with remote set up correctly"""
        if not os.path.exists(os.path.join(self.path, '.git')):
            subprocess.run(['git', 'init'], cwd=self.path)
            remote_url = f"https://{self.token}@github.com/{self.owner}/{self.repo}.git"
            subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=self.path)
            # Pull from remote if it exists
            subprocess.run(['git', 'pull', 'origin', self.branch], cwd=self.path)

    # Checks to see if files were modified
    def on_modified(self, event):
        if not event.is_directory:
            self.modifications[self._get_relative_path(event.src_path)] = "Modified"
   
    # Checks to see if new file/dir was created
    def on_created(self, event):
        self.modifications[self._get_relative_path(event.src_path)] = "Created"

    # Checks to see if file/dir is deleted
    def on_deleted(self, event):
        self.modifications[self._get_relative_path(event.src_path)] = "Deleted"
    
    def _get_relative_path(self, abs_path):
        """Convert absolute path to repository-relative path"""
        return os.path.relpath(abs_path, self.path)

    def get_commit_msg(self):
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        commit_msg = simpledialog.askstring("GitHub Commit", "Enter commit message:")
        root.destroy()
        return commit_msg if commit_msg else "Auto commit"

    def commit_and_push(self):
        if not self.modifications:
            print("No changes detected")
            return
            
        print(f"Changes detected: {self.modifications}")
        
        # First pull to get any remote changes
        try:
            subprocess.run(['git', 'pull', 'origin', self.branch], cwd=self.path, check=True)
        except subprocess.CalledProcessError:
            print("Pull failed, there might be conflicts to resolve")
            return
            
        # Stage modified/created files
        for file_path, change_type in self.modifications.items():
            if change_type in ["Created", "Modified"]:
                subprocess.run(['git', 'add', file_path], cwd=self.path)
            elif change_type == "Deleted":
                subprocess.run(['git', 'rm', file_path], cwd=self.path)
                
        # Commit changes
        commit_message = self.get_commit_msg()
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=self.path)
        
        # Push to remote
        try:
            subprocess.run(['git', 'push', 'origin', self.branch], cwd=self.path, check=True)
            print("Changes successfully committed and pushed")
        except subprocess.CalledProcessError:
            print("Push failed, run 'git pull' and resolve any conflicts")
            
        # Clear modifications after commit attempt
        self.modifications.clear()


def main(): 
   # Setting up an observer
   observer = Observer()
   eventHandler = GitAutoCommit()
   
   # Watch current directory
   dir_to_watch = "."
   
   observer.schedule(eventHandler, dir_to_watch, recursive=True)

   observer.start()

   try:
      # Keep running script until intrupted by "Ctrl + C"
      while True:
         pass
   except KeyboardInterrupt:
      eventHandler.commit_and_push()
      observer.stop()

   # Shuts down observer
   observer.join()

if __name__ == "__main__":
   main()