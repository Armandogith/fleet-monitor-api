"""
migrate_plan_fields.py
──────────────────────
Adiciona as colunas  plan_type  e  plan_expires_at  na tabela companies
sem apagar dados existentes.

Execute UMA VEZ antes de subir a nova versão do sistema:

    python migrate_plan_fields.py
"""

import sqlite3
from datetime import date, timedelta

DB_PATH = "transport_test.db"   # ajuste se necessário

DEMO_EXPIRES_DAYS = 7           # demo expira em 7 dias a partir de hoje


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── 1. Verifica colunas já existentes ─────────────────────────────────────
    cur.execute("PRAGMA table_info(companies)")
    existing = {row[1] for row in cur.fetchall()}

    # ── 2. Adiciona plan_type se não existir ──────────────────────────────────
    if "plan_type" not in existing:
        cur.execute("ALTER TABLE companies ADD COLUMN plan_type TEXT NOT NULL DEFAULT 'demo'")
        print("✅ Coluna plan_type adicionada")
    else:
        print("⏭️  plan_type já existe — pulando")

    # ── 3. Adiciona plan_expires_at se não existir ────────────────────────────
    if "plan_expires_at" not in existing:
        cur.execute("ALTER TABLE companies ADD COLUMN plan_expires_at TEXT")   # ISO date string
        print("✅ Coluna plan_expires_at adicionada")
    else:
        print("⏭️  plan_expires_at já existe — pulando")

    # ── 4. Preenche empresas existentes sem data de expiração ─────────────────
    demo_exp = (date.today() + timedelta(days=DEMO_EXPIRES_DAYS)).isoformat()
    cur.execute(
        "UPDATE companies SET plan_expires_at = ? WHERE plan_expires_at IS NULL",
        (demo_exp,)
    )
    updated = cur.rowcount
    print(f"📅 {updated} empresa(s) receberam expiração demo = {demo_exp}")

    conn.commit()
    conn.close()
    print("\n🎉 Migração concluída! Pode subir o sistema.")


if __name__ == "__main__":
    migrate()