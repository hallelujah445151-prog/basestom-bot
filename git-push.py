import subprocess
import os
import sys

os.chdir('basestom')

print('[INFO] Running git commands...')

try:
    # Stage the file
    result = subprocess.run(['git', 'add', 'src/services/reminder_service.py'], 
                         capture_output=True, text=True, encoding='utf-8')
    print(result.stdout)
    if result.returncode != 0:
        print(f'[ERROR] Git add failed: {result.stderr}')
        sys.exit(1)
    
    # Commit
    result = subprocess.run(['git', 'commit', '-m', 'Fix reminder - send 1 day before deadline'],
                         capture_output=True, text=True, encoding='utf-8')
    print(result.stdout)
    if result.returncode != 0:
        print(f'[ERROR] Git commit failed: {result.stderr}')
        sys.exit(1)
    
    # Push
    result = subprocess.run(['git', 'push'],
                         capture_output=True, text=True, encoding='utf-8', timeout=60)
    print(result.stdout)
    if result.returncode != 0:
        print(f'[ERROR] Git push failed: {result.stderr}')
        sys.exit(1)
    
    print('[SUCCESS] All git commands completed successfully!')
    
except subprocess.TimeoutExpired:
    print('[ERROR] Git push timeout after 60 seconds')
    sys.exit(1)
except Exception as e:
    print(f'[ERROR] Unexpected error: {e}')
    sys.exit(1)
