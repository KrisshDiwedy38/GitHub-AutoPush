import os 
import sys
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import simpledialog, messagebox
from GitHub_PushToken import PushingToken


class GitAutoCommit(FileSystemEventHandler):
   def __init__(self):
      self.modifications = {}

   def on_modified(self, event):
      if not event.is_directory:
         self.modifications[event.src_path] = "Modified"

   def on_created(self, event):
      self.modifications[event.src_path] = "Created"

   def on_deleted(self, event):
      self.modifications[event.src_path] = "Deleted"

   def print(self):
      print (self.modifications)

   # def get_commit_msg(self):
   #    root = Tk()
   #    commit_msg = simpledialog.askstring("GitHub Commit", 
   #                                           f"Enter commit message:")
      
   #    return commit_msg

def main(): 
   observer = Observer()
   eventHandler = GitAutoCommit()
   
   dir_to_watch = "."
   
   observer.schedule(eventHandler, dir_to_watch, recursive=True)

   observer.start()

   try:
      while True:
         pass
   except KeyboardInterrupt:
      eventHandler.print()
      observer.stop()

   observer.join()

if __name__ == "__main__":
   main()