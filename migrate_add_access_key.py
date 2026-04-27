"""
migrate_add_access_key.py
─────────────────────────
Adiciona a coluna access_key na tabela companies sem perder dados.
Rode UMA VEZ antes de subir o servidor.
"""

import sqlite3
import random
import string
import os

DB_PATH = "transport_test.db"

if not os.path.exists(DB_PATH):
    print(f"❌ Banco '{DB_PATH}' não encontrado. Rode uvicorn primeiro para criar o banco.")
    exit(1)

def generate_key(plan_type: str) -> str:
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    prefix = "DEMO" if plan_type == "demo" else "FULL"
    return f"{prefix}-{suffix}"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1. Verificar se coluna já existe
cur.execute("PRAGMA table_info(companies)")
cols = [row[1] for row in cur.fetchall()]

if "access_key" not in cols:
    print("➕ Adicionando coluna access_key...")
    cur.execute("ALTER TABLE companies ADD COLUMN access_key TEXT")
    conn.commit()
    print("✅ Coluna adicionada.")
else:
    print("✅ Coluna access_key já existe.")

# 2. Gerar chaves para empresas que não têm
cur.execute("SELECT id, plan_type, access_key FROM companies")
companies = cur.fetchall()

used_keys = set()
updated = 0

for company_id, plan_type, existing_key in companies:
    if existing_key and existing_key.strip():
        used_keys.add(existing_key)
        continue

    # Gerar chave única
    for _ in range(20):
        key = generate_key(plan_type or "demo")
        if key not in used_keys:
            used_keys.add(key)
            break

    cur.execute(
        "UPDATE companies SET access_key = ? WHERE id = ?",
        (key, company_id)
    )
    print(f"   Empresa ID {company_id} → {key}")
    updated += 1

conn.commit()
conn.close()

print(f"\n✅ Migração concluída! {updated} empresa(s) atualizada(s).")
print("Agora pode subir o servidor: uvicorn main:app --reload --host 0.0.0.0 --port 8000")