#!/usr/bin/env bash
# BrandGuard AI â€” Backend Startup Script for Render
# 1. Runs DB migrations (creates all tables via SQLAlchemy)
# 2. Seeds demo workspace, users, and brand kit if first deploy
# 3. Starts Uvicorn web server

set -e

echo "ðŸ›¡ï¸  BrandGuard AI â€” Starting up..."
echo "ðŸ“¦  DATABASE_URL set: ${DATABASE_URL:0:30}..."

# Step 1: Create all DB tables (idempotent)
echo "ðŸ—„ï¸  Running database table initialization..."
python -c "
import sys, os
sys.path.insert(0, os.getcwd())
from app.core.database import Base, engine
from app.models import *  # Ensure all models are imported
Base.metadata.create_all(bind=engine)
print('  âœ“ All database tables created/verified')
"

# Step 2: Seed demo data (only if workspace does not yet exist)
echo "ðŸŒ±  Running demo seeder (skips if already seeded)..."
python -c "
import sys, os
sys.path.insert(0, os.getcwd())

from app.core.database import SessionLocal
from app.models.workspace import Workspace

db = SessionLocal()
existing = db.query(Workspace).filter(Workspace.name == 'Innovex Governance').first()
db.close()

if existing:
    print('  â­ï¸  Demo data already seeded â€” skipping.')
else:
    print('  ðŸŒ± Seeding demo workspace, users, and brand kit...')
    # Add parent dir of backend to path so seed_demo.py can import app
    seed_path = os.path.join(os.getcwd(), '..', 'sample-brand-kit', 'seed_demo.py')
    if os.path.exists(seed_path):
        exec(open(seed_path).read())
    else:
        print('  âš ï¸  Seed script not found â€” skipping. Please seed manually.')
"

# Step 3: Start Uvicorn
PORT=${PORT:-8000}
echo "ðŸš€  Starting Uvicorn on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
