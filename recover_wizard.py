import os
import sqlite3
import base64
import re
import shutil
from datetime import datetime

# Paths
CONV_DIR = os.path.expanduser("~/.gemini/antigravity/conversations")
BRAIN_DIR = os.path.expanduser("~/.gemini/antigravity/brain")
DB_PATH = os.path.expanduser("~/.config/Antigravity-B/User/globalStorage/state.vscdb")

def get_indexed_uuids():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM ItemTable WHERE key = 'antigravityUnifiedStateSync.trajectorySummaries'")
        row = cursor.fetchone()
        if not row: return set()
        data = base64.b64decode(row[0]).decode('latin-1')
        return set(re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', data))
    except: return set()

def get_chat_metadata(uuid):
    metadata = {"topic": "Unknown", "workspace": "General / Other", "time": 0}
    path = os.path.join(CONV_DIR, f"{uuid}.pb")
    if os.path.exists(path):
        metadata["time"] = os.path.getmtime(path)
    
    brain_path = os.path.join(BRAIN_DIR, uuid)
    if os.path.exists(brain_path):
        for root, dirs, files in os.walk(brain_path):
            for bf in files:
                bfile_path = os.path.join(root, bf)
                try:
                    with open(bfile_path, 'r', errors='ignore') as f:
                        content = f.read()
                        if "/repos_private/" in content:
                            # Cleaner regex: match until next slash, space, or quote
                            match = re.search(r'/repos_private/([a-zA-Z0-9\-_]+)', content)
                            if match: metadata["workspace"] = match.group(1)
                        if bf == "task.md":
                            line = content.split('\n')[0].strip()
                            metadata["topic"] = line.replace('# ', '').replace('- [x] ', '').replace('- [ ] ', '')
                except: pass
    return metadata

def wizard():
    indexed = get_indexed_uuids()
    files = [f for f in os.listdir(CONV_DIR) if f.endswith('.pb')]
    
    # Discover and Group Orphans
    all_orphans = []
    projects = {}
    for f in files:
        uuid = f.replace('.pb', '')
        if uuid not in indexed:
            meta = get_chat_metadata(uuid)
            ws = meta["workspace"]
            if ws != "General / Other":
                all_orphans.append({'uuid': uuid, 'time': meta['time'], 'topic': meta['topic'], 'ws': meta['workspace']})
                if ws not in projects: projects[ws] = []
                projects[ws].append(all_orphans[-1])
    
    if not all_orphans:
        print("No orphans found!")
        return

    while True:
        print("\n--- Antigravity Recovery Wizard ---")
        print("[W] View by Workspace / Project")
        print("[C] View All Chats (Descending by Date)")
        print("[Q] Quit")
        
        mode = input("\nSelect Mode: ").upper()
        
        if mode == 'Q': break
        
        if mode == 'C':
            # Global Chat View
            sorted_orphans = sorted(all_orphans, key=lambda x: x['time'], reverse=True)
            print(f"\n{'#':<3} | {'Date':<16} | {'Workspace':<20} | {'Goal / Topic':<40}")
            print("-" * 85)
            for i, o in enumerate(sorted_orphans[:30]): # Show top 30
                dt = datetime.fromtimestamp(o['time']).strftime('%Y-%m-%d %H:%M')
                print(f"{i+1:<3} | {dt:<16} | {o['ws'][:18]:<20} | {o['topic'][:40]:<40}")
            
            selection = input("\nSelect orphans to recover (e.g. 1,2,5) or 'b' for back: ")
            if selection.lower() == 'b': continue
            indices = [int(i.strip()) - 1 for i in selection.split(',') if i.strip().isdigit()]
            targets = [sorted_orphans[i] for i in indices if 0 <= i < len(sorted_orphans)]
            if targets: handle_recovery(targets)

        if mode == 'W':
            # Workspace View
            print(f"\n{'#':<3} | {'Workspace / Project':<30} | {'Orphans':<8}")
            print("-" * 45)
            ws_list = sorted(projects.keys())
            for i, ws in enumerate(ws_list):
                print(f"{i+1:<3} | {ws:<30} | {len(projects[ws]):<8}")
            
            ws_sel = input("\nSelect Project Number or 'b' for back: ")
            if ws_sel.lower() == 'b': continue
            if not ws_sel.isdigit() or int(ws_sel) > len(ws_list): continue
            
            selected_ws = ws_list[int(ws_sel)-1]
            orphans = sorted(projects[selected_ws], key=lambda x: x['time'], reverse=True)

            print(f"\n--- Orphans in {selected_ws} ---")
            print(f"{'#':<3} | {'Date':<16} | {'Goal / Topic':<60}")
            print("-" * 85)
            for i, o in enumerate(orphans):
                dt = datetime.fromtimestamp(o['time']).strftime('%Y-%m-%d %H:%M')
                print(f"{i+1:<3} | {dt:<16} | {o['topic']:<60}")
            
            selection = input("\nSelect orphans to recover (e.g. 1,2,5) or 'b' for back: ")
            if selection.lower() == 'b': continue
            indices = [int(i.strip()) - 1 for i in selection.split(',') if i.strip().isdigit()]
            targets = [orphans[i] for i in indices if 0 <= i < len(orphans)]
            if targets: handle_recovery(targets)

def handle_recovery(targets):
    # 4. Dummy Creation
    print(f"\n[STEP 1] Create {len(targets)} NEW chats in Profile B.")
    print("\nPaste this EXACTLY into each new chat:\n")
    print("--------------------------------------------------")
    print("Do not look at the workspace, I forbid it. The only thing you should do is briefly say hi. Hi mate!")
    print("--------------------------------------------------\n")
    
    input(f"Press ENTER once all {len(targets)} are created...")
    
    # 5. Discover Dummies
    now = datetime.now().timestamp()
    dummies = []
    for f in [f for f in os.listdir(CONV_DIR) if f.endswith('.pb')]:
        mtime = os.path.getmtime(os.path.join(CONV_DIR, f))
        if now - mtime < 180: # Increased to 3 minutes for safety
            dummies.append({'uuid': f.replace('.pb', ''), 'time': mtime})
    
    dummies.sort(key=lambda x: x['time'], reverse=True)
    if len(dummies) < len(targets):
        print(f"\nError: Found only {len(dummies)} new chats. (Needed {len(targets)})")
        return

    # 6. Detailed Confirmation
    print("\n[STEP 2] CONFIRM RESTORATION:")
    print(f"{' ':4} | {'Date':<16} | {'Workspace':<20} | {'Goal / Topic':<40}")
    print("-" * 85)
    mapping = []
    for i in range(len(targets)):
        mapping.append((targets[i]['uuid'], dummies[i]['uuid']))
        
        # Get dummy metadata for confirmation
        dummy_meta = get_chat_metadata(dummies[i]['uuid'])
        orphan_dt = datetime.fromtimestamp(targets[i]['time']).strftime('%Y-%m-%d %H:%M')
        dummy_dt = datetime.fromtimestamp(dummies[i]['time']).strftime('%Y-%m-%d %H:%M')
        
        print(f"FROM | {orphan_dt:<16} | {targets[i]['ws'][:18]:<20} | {targets[i]['topic'][:40]:<40}")
        print(f"INTO | {dummy_dt:<16} | {dummy_meta['workspace'][:18]:<20} | {dummy_meta['topic'][:40]:<40}")
        print("-" * 85)
    
    confirm = input("\nPress ENTER to execute restoration or 'q' to abort: ")
    if confirm.lower() == 'q':
        print("Aborted.")
        return

    # 7. Injection
    print("\n[STEP 3] Injecting...")
    for i in range(len(targets)):
        shutil.copy2(os.path.join(CONV_DIR, f"{targets[i]['uuid']}.pb"), 
                     os.path.join(CONV_DIR, f"{dummies[i]['uuid']}.pb"))
        print(f"DONE: {targets[i]['topic'][:30]}...")

    print("\nAll tasks finished!")
    input("\nPress ENTER to close Antigravity (soft shutdown)...")
    
    import subprocess
    try:
        # Send SIGTERM to all processes named 'antigravity'
        subprocess.run(["pkill", "-15", "antigravity"], check=False)
        print("Shutdown signal sent.")
    except Exception as e:
        print(f"Could not send shutdown signal: {e}")

if __name__ == "__main__":
    try:
        wizard()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
