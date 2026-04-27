"""
migrate_fix.py
──────────────
Corrige o banco existente:
  - Adiciona plan_type e plan_expires_at se não existirem
  - Adiciona responsible_whatsapp se não existir
  - Atualiza empresas sem expiração para demo 7 dias

Rode UMA VEZ antes de subir o servidor:
  python migrate_fix.py
"""

import sqlite3
from datetime import date, timedelta

DB_PATH = "./transport_test.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Descobre colunas existentes
cur.execute("PRAGMA table_info(companies)")
cols = {row[1] for row in cur.fetchall()}

added = []

if "plan_type" not in cols:
    cur.execute("ALTER TABLE companies ADD COLUMN plan_type TEXT NOT NULL DEFAULT 'demo'")
    added.append("plan_type")

if "plan_expires_at" not in cols:
    cur.execute("ALTER TABLE companies ADD COLUMN plan_expires_at TEXT")
    added.append("plan_expires_at")

if "responsible_whatsapp" not in cols:
    cur.execute("ALTER TABLE companies ADD COLUMN responsible_whatsapp TEXT")
    added.append("responsible_whatsapp")

if added:
    print(f"✅ Colunas adicionadas: {', '.join(added)}")
else:
    print("ℹ️  Todas as colunas já existiam.")

# Atualiza empresas sem expiração → demo 7 dias
expires_demo = (date.today() + timedelta(days=7)).isoformat()
cur.execute(
    "UPDATE companies SET plan_expires_at = ? WHERE plan_expires_at IS NULL OR plan_expires_at = ''",
    (expires_demo,),
)
updated = cur.rowcount
if updated:
    print(f"📅 {updated} empresa(s) receberam expiração demo = {expires_demo}")

conn.commit()
conn.close()
print("🎉 Migração concluída! Agora suba o servidor.")