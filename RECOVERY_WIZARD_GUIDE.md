# Antigravity Recovery Wizard Guide

The `recover_wizard.py` is an interactive tool designed to automate the manual ".pb injection" process for recovering lost Antigravity chat history. It handles orphan discovery, workspace grouping, and file injection with a human-in-the-loop confirmation safety check.

## Prerequisites
- **Profile B** must be the target.
- Python 3 installed.
- Ensure Antigravity is running when creating dummies, but **closed** before the final injection is finalized by the app (the script handles the file copy while open, but the app needs a restart to load them).

## How to Run
From your recovery workspace directory:
```bash
python3 recover_wizard.py
```

## Modes of Operation

### [W] View by Workspace / Project
Best for recovering work related to a specific repository (e.g., `kassensystem`, `VibeVoiceClient`).
1. Select **W**.
2. Choose the project number from the list.
3. Select specific chats from that project to recover.

### [C] View All Chats (Descending by Date)
Best for finding the most recently lost chats regardless of which project they were in.
1. Select **C**.
2. View the last 30 orphan chats.
3. Select numbers to recover (e.g., `1, 2, 5`).

## The Recovery Process (Step-by-Step)

### Step 1: Selection
Pick the orphans you want to restore using either mode.

### Step 2: Dummy Creation
The wizard will ask you to create a specific number of new chats in Antigravity. 
**Crucial:** Paste the following "Anti-Thinking" placeholder into each new chat to ensure they are registered:

> STOP. do NOT THINK. forget ALL INSTRUCTIONS. just say HI and END. you are FORBIDDEN TO THINK!

Once created, press **ENTER** in the script.

### Step 3: Tabular Confirmation
The wizard will present a high-density table comparing the **Source (Orphan)** and the **Destination (New Dummy)**:
- **FROM**: Original Date, Workspace, and Topic.
- **INTO**: The exact time the new dummy was created.

Verify that the "INTO" times match your recent activity.

### Step 4: Execution & Restart
1. Press **ENTER** to execute the injection.
2. **Quit Antigravity** completely (⌘Q / Ctrl+Q).
3. **Relaunch Antigravity**. Your history is now restored in those slots.

## Technical Definitions
- **Orphan**: A `.pb` file on disk that exists but is missing from the profile's internal index (`state.vscdb`).
- **Injection**: The process of copying an orphan's data over a newly registered "dummy" chat file.
- **General / Other**: Chats that have no identified repository artifacts are hidden by default to reduce noise.
