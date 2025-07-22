#!/usr/bin/env python3
"""
Simple script to list all project files for manual download
"""
import os

def list_project_files(root_dir='.'):
    """List all important project files"""
    important_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # Skip hidden directories and files
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        files = [f for f in files if not f.startswith('.')]
        
        for file in files:
            if file.endswith(('.py', '.md', '.txt', '.json', '.toml', '.lock')):
                full_path = os.path.join(root, file)
                important_files.append(full_path)
    
    print("=== PROJECT FILES TO DOWNLOAD ===")
    for file_path in sorted(important_files):
        print(f"📁 {file_path}")
    
    print("\n=== MANUAL GITHUB UPDATE STEPS ===")
    print("1. Go to: https://github.com/heynoxcodes/discord-shop-bot")
    print("2. Click 'Add file' -> 'Upload files'")
    print("3. Download each file listed above from Replit")
    print("4. Upload all files to GitHub")
    print("5. Commit with message: 'Fixed threading issues and added products'")

if __name__ == "__main__":
    list_project_files()