import os
import shutil

skills_root = r"D:\01_PROJECT_CODE\skills"
dev_organiza = os.path.join(skills_root, "organiza")
dev_checklist = os.path.join(skills_root, "checklist")

agent_organiza = r"D:\.agents\skills\organiza"
agent_checklist = r"C:\Users\darwi.PCDARWICH\.gemini\config\skills\checklist"

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
