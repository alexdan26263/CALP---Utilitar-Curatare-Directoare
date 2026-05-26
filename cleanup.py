#!/usr/bin/env python3
import argparse
import subprocess
import sys
import time

def fetch_files(directory, older_than_days, recursive):
    cmd = ["find", directory]

    if not recursive:
        cmd.extend(["-maxdepth", "1"])

    cmd.extend(["-type", "f", "-exec", "stat", "-c", "%n|%s|%Y", "{}", "+"])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0 and not result.stdout:
            print(f"Eroare sau permisiuni refuzate: {result.stderr}", file=sys.stderr)
            return []

        files = []
        current_time = time.time()

        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            
            parts = line.rsplit('|', 2)
            if len(parts) == 3:
                path, size_str, mtime_str = parts
                size = int(size_str)
                mtime = int(mtime_str)
                
                age_days = (current_time - mtime) / 86400

                if older_than_days is not None and age_days < older_than_days:
                    continue

                files.append({
                    'path': path,
                    'size': size,
                    'age_days': age_days
                })
        return files
    except FileNotFoundError:
        print("Eroare: Comenzile Linux 'find' sau 'stat' lipsesc.", file=sys.stderr)
        sys.exit(1)

def format_size(size_bytes):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0

def obtine_dimensiune(fisier):
    return fisier['size']

def obtine_varsta(fisier):
    return fisier['age_days']

def main():
    parser = argparse.ArgumentParser(description="Cleanup Tool")
    parser.add_argument("-d", "--dir", default=".", help="Director tinta (default: curent)")
    parser.add_argument("-s", "--sort", choices=["size", "age"], default="size", help="Criteriul de sortare")
    parser.add_argument("-r", "--reverse", action="store_true", help="Inverseaza ordinea sortarii")
    parser.add_argument("--older-than", type=int, help="Filtreaza fisierele mai vechi de x zile")
    parser.add_argument("--delete", action="store_true", help="Sterge deefinitiv fisierele gasite")
    parser.add_argument("--dry-run", action="store_true", help="Arata ce fisiere s-ar sterge fara a efectua stergerea")
    
    parser.add_argument("--recursive", action="store_true", help="Cauta inclusiv in toate subddirectoarele")

    args = parser.parse_args()

    mod_cautare = "RECURSIV" if args.recursive else "NON-RECURSIV"
    print(f"Analizam directorul: {args.dir} | Mod: {mod_cautare}")

    files = fetch_files(args.dir, args.older_than, args.recursive)

    if not files:
        print("Nu s-au gasit fisiere care sa corespunda criteriilor")
        return

    if args.sort == "size":
        files.sort(key=obtine_dimensiune, reverse=not args.reverse)
    else:
        files.sort(key=obtine_varsta, reverse=not args.reverse)

    print(f"\nS-au gasit {len(files)} fisiere:\n")
    print(f"{'Dimensiune':<12} | {'Varsta (zile)':<13} | {'Fisier'}")
    print("-" * 70)

    for f in files:
        size_fmt = format_size(f['size'])
        print(f"{size_fmt:<12} | {f['age_days']:<13.1f} | {f['path']}")
    print("-" * 70)

    if args.delete or args.dry_run:
        print("\nStergere...")
        for f in files:
            if args.dry_run:
                print(f"[DRY-RUN] S-ar fi sters: {f['path']}")
            else:
                try:
                    subprocess.run(["rm", "-f", f['path']], check=True)
                    print(f"[STERS] {f['path']}")
                except subprocess.CalledProcessError:
                    print(f"[EROARE] Nu s-a putut sterge: {f['path']}")
    else:
        print("\nRuleaza cu --dry-run pentru a simula stergerea sau --delete pentru a executa.")

if __name__ == "__main__":
    main()