"""Database Seeding Script for Aditya University Curriculum."""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.database.seed import seed_database

if __name__ == "__main__":
    print("[*] Starting Aditya University database seeding...")
    seed_database()
    print("[+] Seeding completed successfully.")
