import sqlite3
import os
from src.core.models import NormalizedLedgerState

class OmniLedgerDatabaseManager:
    def __init__(self, db_path: str = "omniledger.db"):
        self.db_path = db_path
        self._initialize_relational_schema()

    def _get_connection(self) -> sqlite3.Connection:
        """Establishes an authoritative connection tracking pointer with foreign keys enforced."""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _initialize_relational_schema(self):
        """Creates the authoritative transaction table and database indexes natively."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS normalized_ledger (
            transaction_id TEXT PRIMARY KEY,
            account_source TEXT NOT NULL,
            original_amount REAL NOT NULL,
            original_currency TEXT NOT NULL,
            normalized_amount_base REAL NOT NULL,
            base_currency_ticker TEXT NOT NULL,
            spot_conversion_rate REAL NOT NULL,
            audit_status TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            processed_at TEXT NOT NULL
        );
        """
        create_index_source = "CREATE INDEX IF NOT EXISTS idx_ledger_source ON normalized_ledger(account_source);"
        create_index_risk = "CREATE INDEX IF NOT EXISTS idx_ledger_risk ON normalized_ledger(risk_level);"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            cursor.execute(create_index_source)
            cursor.execute(create_index_risk)
            conn.commit()

    def write_normalized_records(self, records: list[NormalizedLedgerState]) -> int:
        """Executes an idempotent batch upsert block protecting the ledger from duplication."""
        upsert_query = """
        INSERT INTO normalized_ledger (
            transaction_id, account_source, original_amount, original_currency,
            normalized_amount_base, base_currency_ticker, spot_conversion_rate,
            audit_status, risk_level, processed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(transaction_id) DO UPDATE SET
            audit_status = excluded.audit_status,
            risk_level = excluded.risk_level,
            processed_at = excluded.processed_at;
        """
        
        inserted_rows = 0
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for rec in records:
                cursor.execute(upsert_query, (
                    rec.transaction_id,
                    rec.account_source,
                    rec.original_amount,
                    rec.original_currency,
                    rec.normalized_amount_base,
                    rec.base_currency_ticker,
                    rec.spot_conversion_rate,
                    rec.audit_status,
                    rec.risk_level,
                    rec.processed_at.isoformat()
                ))
                inserted_rows += 1
            conn.commit()
        return inserted_rows
