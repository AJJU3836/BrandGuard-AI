#!/usr/bin/env bash
# BrandGuard AI - Backend Startup Script for Render
set -e

echo "Starting BrandGuard AI backend..."

# Step 1: Create all DB tables via SQLAlchemy
echo "Initializing database tables..."
python -c "
import sys, os
sys.path.insert(0, os.getcwd())
import app.models
from app.core.database import Base, engine
Base.metadata.create_all(bind=engine)
print('Database tables created/verified OK')
"

# Step 2: Seed demo data if workspace does not yet exist
echo "Checking demo seed data..."
python -c "
import sys, os
sys.path.insert(0, os.getcwd())
from app.core.database import SessionLocal
from app.models.workspace import Workspace
db = SessionLocal()
existing = db.query(Workspace).filter(Workspace.name == 'Innovex Governance').first()
db.close()
if existing:
    print('Demo data already seeded - skipping.')
else:
    print('Seeding demo workspace...')
    seed_path = os.path.join(os.getcwd(), '..', 'sample-brand-kit', 'seed_demo.py')
    if os.path.exists(seed_path):
        exec(open(seed_path).read())
    else:
        print('Seed script not found - skipping. Seed manually if needed.')
"

# Step 3: Start Uvicorn server
PORT=${PORT:-8000}
echo "Starting Uvicorn on port $PORT"
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"