#!/usr/bin/env bash
set -euo pipefail

if [ -z "${SUPABASE_DB_URL:-}" ]; then
  echo "ERRO: SUPABASE_DB_URL não definida"
  exit 1
fi

python - <<'PY'
import os
from sqlalchemy import create_engine, text

db_url = os.environ["SUPABASE_DB_URL"]
engine = create_engine(db_url, pool_pre_ping=True)

with engine.connect() as conn:
    total = conn.execute(text("SELECT COUNT(*) FROM noticias")).scalar()
    ultima = conn.execute(text("SELECT MAX(data_coleta) FROM noticias")).scalar()

print(f"OK | noticias={total} | ultima_coleta={ultima}")
PY
