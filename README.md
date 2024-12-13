# CopyPasteDeleteRenameGUI
Copy, Paste, Delete or Rename to multiple folders from one folder
# CPDRv1

## Overview

**CPDRv1** is an application designed to monitor a specified source directory for file changes, including creation, deletion, and renaming. It automatically replicates these changes across multiple target directories. This tool is ideal for maintaining synchronized copies of files across different locations.

---

## Features

- **Real-time Monitoring**: Continuously watches a source directory for any file changes.
- **File Replication**: Copies new files and applies deletions or renames to all specified target directories.
- **Graphical User Interface (GUI)**: Provides an easy-to-use interface for selecting directories and viewing logs.
- **Safe Shutdown**: Allows users to stop monitoring safely with a button click.

---

## Installation

The application is available as an executable file located in the `dist` folder. You can run it directly without needing any additional software installations.

---

## Usage

### 1. Launch the Application
Run the executable from the `dist` folder to open the GUI.

### 2. Select Directories
- Use the **"Browse"** button to select a source directory.
- Select up to five target directories where file changes will be replicated.

### 3. Start Monitoring
Click **"Start Monitoring"** to begin watching for file changes. The application will log activities in real-time within the GUI.

### 4. Stop Monitoring
Click **"Stop Monitoring"** to safely stop the observer and close the application.

---

## Additional Notes

- Ensure that all specified directories exist and have appropriate read/write permissions.
- The GUI auto-scrolls logs to keep you updated with the latest actions performed by the application.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

