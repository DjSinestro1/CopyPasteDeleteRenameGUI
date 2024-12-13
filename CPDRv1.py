import os
import shutil
import time
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Attempt to import psutil, install if not found
try:
    import psutil
except ImportError:
    print("psutil not found. Attempting to install...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'psutil'])
    import psutil

class FileCopyHandler(FileSystemEventHandler):
    def __init__(self, source_dir, destination_dirs, wait_time=5, max_retries=3, log_widget=None):
        self.source_dir = source_dir
        self.destination_dirs = [d for d in destination_dirs if d.strip()]  # Filter empty paths
        self.wait_time = wait_time
        self.max_retries = max_retries
        self.log_widget = log_widget

    def log(self, message):
        """Log a message to the GUI log widget."""
        if self.log_widget:
            self.log_widget.insert(tk.END, message + '\n')
            self.log_widget.yview(tk.END)  # Auto-scroll to the end

    def is_file_locked(self, filepath):
        """Check if file is in use by another process"""
        try:
            os.rename(filepath, filepath)
            return False
        except (OSError, PermissionError):
            return True

    def wait_for_file_ready(self, filepath):
        """Wait for file to be fully available"""
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.wait_time)
                initial_size = os.path.getsize(filepath)
                time.sleep(1)
                final_size = os.path.getsize(filepath)
                if initial_size == final_size and not self.is_file_locked(filepath):
                    return True
            except Exception as e:
                self.log(f"File check attempt {attempt + 1} failed: {e}")
        return False

    def on_created(self, event):
        if not event.is_directory:
            source_path = event.src_path
            if not self.wait_for_file_ready(source_path):
                self.log(f"File {source_path} not ready after multiple attempts")
                return

            relative_path = os.path.relpath(source_path, self.source_dir)
            for dest_dir in self.destination_dirs:
                try:
                    full_dest_path = os.path.join(dest_dir, relative_path)
                    os.makedirs(os.path.dirname(full_dest_path), exist_ok=True)
                    shutil.copy2(source_path, full_dest_path)
                    self.log(f"Successfully copied {relative_path} to {full_dest_path}")
                except Exception as e:
                    self.log(f"Error copying {relative_path} to {dest_dir}: {e}")

    def on_deleted(self, event):
        if not event.is_directory:
            source_path = event.src_path
            relative_path = os.path.relpath(source_path, self.source_dir)
            for dest_dir in self.destination_dirs:
                try:
                    full_dest_path = os.path.join(dest_dir, relative_path)
                    if os.path.exists(full_dest_path):
                        os.remove(full_dest_path)
                        self.log(f"Deleted {relative_path} from {dest_dir}")
                except Exception as e:
                    self.log(f"Error deleting {relative_path} from {dest_dir}: {e}")

    def on_moved(self, event):
        if not event.is_directory:
            src_relative_path = os.path.relpath(event.src_path, self.source_dir)
            dest_relative_path = os.path.relpath(event.dest_path, self.source_dir)
            for dest_dir in self.destination_dirs:
                try:
                    src_full_dest_path = os.path.join(dest_dir, src_relative_path)
                    dest_full_dest_path = os.path.join(dest_dir, dest_relative_path)

                    if os.path.exists(src_full_dest_path):
                        os.makedirs(os.path.dirname(dest_full_dest_path), exist_ok=True)
                        os.rename(src_full_dest_path, dest_full_dest_path)
                        self.log(f"Renamed {src_relative_path} to {dest_relative_path} in {dest_dir}")
                except Exception as e:
                    self.log(f"Error renaming {src_relative_path} to {dest_relative_path} in {dest_dir}: {e}")

def browse_directory(entry_widget):
    directory = filedialog.askdirectory()
    if directory:
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, directory)

def start_monitoring():
    global observer  # Declare observer as global so it can be accessed in stop_monitoring
    source_directory = entry_source_directory.get()
    destination_directories = [
        dir_path for dir_path in [
            entry_target_directory_1.get(),
            entry_target_directory_2.get(),
            entry_target_directory_3.get(),
            entry_target_directory_4.get(),
            entry_target_directory_5.get()
        ] if dir_path.strip()  # Only include non-empty directory paths
    ]

    if not os.path.isdir(source_directory):
        messagebox.showerror("Error", "Please select a valid source directory.")
        return

    if not destination_directories:
        messagebox.showerror("Error", "Please select at least one target directory.")
        return

    for target_directory in destination_directories:
        if not os.path.isdir(target_directory):
            messagebox.showerror("Error", f"Please select a valid target directory: {target_directory}.")
            return

    # Create the event handler with custom wait times and logging capability
    event_handler = FileCopyHandler(
        source_dir=source_directory,
        destination_dirs=destination_directories,
        wait_time=5,
        max_retries=3,
        log_widget=text_log  # Pass the text widget for logging
    )

    observer = Observer()
    observer.schedule(event_handler, source_directory, recursive=True)
    observer.start()

    text_log.insert(tk.END, f"Monitoring {source_directory} for new files...\n")
    text_log.insert(tk.END, f"Active target directories: {len(destination_directories)}\n")
    for dir in destination_directories:
        text_log.insert(tk.END, f"- {dir}\n")

def stop_monitoring():
    global observer  # Access the global observer variable
    observer.stop()
    observer.join()
    root.quit()  # Close the application safely

# Create the main window
root = tk.Tk()
root.title("File Monitor and Copier")

# Source Directory selection
frame_source = tk.Frame(root)
frame_source.pack(padx=10, pady=5)

label_source_directory = tk.Label(frame_source, text="Select Source Directory:")
label_source_directory.grid(row=0, column=0, padx=5, pady=5)

entry_source_directory = tk.Entry(frame_source, width=50)
entry_source_directory.grid(row=0,column=1,padx=5,pady=5)

button_browse_source=tk.Button(frame_source,text="Browse",command=lambda: browse_directory(entry_source_directory))
button_browse_source.grid(row=0,column=2,padx=5,pady=5)

# Target Directory 1-5 selections
for i in range(1, 6):
    frame_target=tk.Frame(root)
    frame_target.pack(padx=(10),pady=(5))

    label_target_directory=tk.Label(frame_target,text=f"Select Target Directory {i}:")
    label_target_directory.grid(row=(0),column=(0),padx=(5),pady=(5))

    entry_target=tk.Entry(frame_target,width=(50))
    entry_target.grid(row=(0),column=(1),padx=(5),pady=(5))

    globals()[f'entry_target_directory_{i}']=entry_target

    button_browse_target=tk.Button(frame_target,text="Browse",command=lambda e=entry_target: browse_directory(e))
    button_browse_target.grid(row=(0),column=(2),padx=(5),pady=(5))

# Start monitoring button
button_start=tk.Button(root,text="Start Monitoring",command=start_monitoring)
button_start.pack(pady=(10))

# Stop monitoring button (to safely close the program)
button_stop=tk.Button(root,text="Stop Monitoring",command=stop_monitoring)
button_stop.pack(pady=(10))

# Log display area using ScrolledText widget for better user experience with logs.
text_log=scrolledtext.ScrolledText(root,width=(80),height=(20))
text_log.pack(padx=(10),pady=(10))

root.mainloop()
