import os
import sqlite3
import base64
import re
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
        
        # Decode base64 and find UUIDs
        data = base64.b64decode(row[0]).decode('latin-1')
        uuids = re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', data)
        return set(uuids)
    except Exception as e:
        print(f"Error reading DB: {e}")
        return set()

def discover_orphans(filter_term="kassensystem"):
    indexed = get_indexed_uuids()
    files = [f for f in os.listdir(CONV_DIR) if f.endswith('.pb')]
    
    orphans = []
    for f in files:
        uuid = f.replace('.pb', '')
        if uuid not in indexed:
            path = os.path.join(CONV_DIR, f)
            mtime = os.path.getmtime(path)
            
            topic = "No artifacts found"
            last_msg = "-"
            matches_filter = False
            
            brain_path = os.path.join(BRAIN_DIR, uuid)
            if os.path.exists(brain_path):
                # Search all artifacts for the project name
                for root, dirs, brain_files in os.walk(brain_path):
                    for bf in brain_files:
                        bfile_path = os.path.join(root, bf)
                        try:
                            with open(bfile_path, 'r', errors='ignore') as content_f:
                                content = content_f.read()
                                if filter_term.lower() in content.lower():
                                    matches_filter = True
                                if bf == "task.md":
                                    lines = [l.strip() for l in content.split('\n') if l.strip()]
                                    if lines:
                                        topic = lines[0].replace('# ', '').replace('- [x] ', '').replace('- [ ] ', '')
                                        # Try to find the last completed task
                                        completed = [l for l in lines if "[x]" in l]
                                        if completed:
                                            last_msg = completed[-1].replace('- [x] ', '')
                        except: pass
            
            if matches_filter:
                orphans.append((mtime, uuid, topic, last_msg))
            
    orphans.sort(reverse=True)
    
    print(f"| Date | Title / First Task | Last Completed Task | UUID (for mapping) |")
    print(f"| :--- | :--- | :--- | :--- |")
    for mtime, uuid, topic, last_msg in orphans:
        dt = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
        # Truncate long strings for the table
        title = (topic[:47] + '..') if len(topic) > 50 else topic
        last = (last_msg[:47] + '..') if len(last_msg) > 50 else last_msg
        print(f"| {dt} | {title} | {last} | {uuid} |")
    
    print(f"\nFound {len(orphans)} orphans for '{filter_term}'.")

if __name__ == "__main__":
    import sys
    term = sys.argv[1] if len(sys.argv) > 1 else "kassensystem"
    discover_orphans(term)
