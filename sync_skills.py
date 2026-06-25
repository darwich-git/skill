import os
import shutil

# Get the repository root dynamically
skills_root = os.path.dirname(os.path.abspath(__file__))
dev_organiza = os.path.join(skills_root, "organiza")
dev_checklist = os.path.join(skills_root, "checklist")

user_home = os.path.expanduser("~")
agent_checklist = os.path.join(user_home, ".gemini", "config", "skills", "checklist")

# Use D:\.agents\skills\organiza if D:\ exists, otherwise fall back to global config folder
if os.path.exists("D:\\"):
    agent_organiza = os.path.join("D:\\", ".agents", "skills", "organiza")
else:
    agent_organiza = os.path.join(user_home, ".gemini", "config", "skills", "organiza")

def sync_folder(src, dest):
    if not os.path.exists(src):
        return
    
    # Clean destination if exists (rmtree handles read-only files if error callback is provided)
    if os.path.exists(dest):
        def on_error(func, path, exc_info):
            import stat
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(dest, onerror=on_error)
        
    shutil.copytree(src, dest)
    print(f"Synced: {os.path.basename(src)} -> {dest}")

if __name__ == "__main__":
    print("Executing automatic skill synchronization...")
    sync_folder(dev_organiza, agent_organiza)
    sync_folder(dev_checklist, agent_checklist)
    print("Sync complete!")
