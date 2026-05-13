import os, shutil, stat, sys

WHITE_LIST = ['python', 'pip', 'claude', 'cursor', 'microsoft', 'apple', 'nvidia', 'torch', 'opencv', 'google', 'anaconda']
BLACK_LIST = ['360', 'coolfile', 'viewer', 'helper', 'assistant', 'zhushou', '360Safe', '360sd']

def force_remove(path):
    def handle_error(func, path, exc_info):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    if os.path.exists(path):
        shutil.rmtree(path, onerror=handle_error)

def main():
    targets = [os.getenv('APPDATA'), os.getenv('LOCALAPPDATA')]
    to_delete = []
    for base in targets:
        if not base or not os.path.exists(base):
            continue
        for folder in os.listdir(base):
            full_path = os.path.join(base, folder)
            if not os.path.isdir(full_path):
                continue
            name = folder.lower()
            if any(safe in name for safe in WHITE_LIST):
                continue
            if any(key in name for key in BLACK_LIST):
                to_delete.append(full_path)

    if not to_delete:
        print("[OK] No matching junkware residues found.")
        return

    print("Found residues:")
    for p in to_delete:
        print(f"  {p}")

    # --force flag skips interactive prompt
    if '--force' in sys.argv:
        ok = True
    else:
        ok = input("\nDelete? (Y/N): ").lower() == 'y'

    if ok:
        for p in to_delete:
            force_remove(p)
            print(f"  Deleted: {p}")
        print("\nDone.")
    else:
        print("Skipped.")

if __name__ == '__main__':
    main()
