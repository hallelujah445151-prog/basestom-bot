import py_compile
import os
import sys

def check_file_syntax(file_path):
    """Check syntax of a single Python file"""
    try:
        py_compile.compile(file_path, doraise=True)
        return True, None
    except py_compile.PyCompileError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def main():
    """Check all Python files in basestom directory"""
    print("="*60)
    print("PYTHON SYNTAX CHECK - BASESTOM PROJECT")
    print("="*60)
    print()

    total_files = 0
    successful_files = 0
    failed_files = 0
    failed_files_list = []

    # Walk through all directories
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                total_files += 1

                # Skip __pycache__ directories
                if '__pycache__' in file_path:
                    continue

                print(f"Checking: {file_path}")

                success, error = check_file_syntax(file_path)

                if success:
                    successful_files += 1
                    print(f"  [OK] PASS")
                else:
                    failed_files += 1
                    failed_files_list.append((file_path, error))
                    print(f"  [FAIL] FAIL: {error}")

                print()

    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total files checked: {total_files}")
    print(f"Successful: {successful_files}")
    print(f"Failed: {failed_files}")
    print()

    if failed_files > 0:
        print("="*60)
        print("FAILED FILES")
        print("="*60)
        for file_path, error in failed_files_list:
            print(f"\n[X] {file_path}")
            print(f"   Error: {error}")
        print()
        print(f"Status: [ERROR] SYNTAX ERRORS FOUND")
        return 1
    else:
        print("="*60)
        print("[OK] ALL FILES PASSED SYNTAX CHECK")
        print("="*60)
        return 0

if __name__ == '__main__':
    sys.exit(main())
