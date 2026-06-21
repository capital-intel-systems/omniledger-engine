import os
import sys

# Self-Healing Path Anchor context execution alignment
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.ingestion import OmniLedgerIngestionAdapter
from src.core.normalization import OmniLedgerCurrencyNormalizer
from src.database.manager import OmniLedgerDatabaseManager

def run_ingestion_pipeline():
    bank_csv = os.path.join(PROJECT_ROOT, "samples", "bank_chase_raw.csv")
    invoice_csv = os.path.join(PROJECT_ROOT, "samples", "invoices_raw.csv")
    binance_csv = os.path.join(PROJECT_ROOT, "samples", "binance_ledger_raw.csv")
    error_log = os.path.join(PROJECT_ROOT, "samples", "corrupt_records.log")

    if os.path.exists(error_log):
        os.remove(error_log)

    print("--- OMNILEDGER INTEGRATED INGESTION RUN ---")
    bank_txs = OmniLedgerIngestionAdapter.parse_bank_feed(bank_csv, error_log)
    invoice_txs = OmniLedgerIngestionAdapter.parse_invoice_feed(invoice_csv, error_log)
    binance_txs = OmniLedgerIngestionAdapter.parse_binance_feed(binance_csv, error_log)

    all_raw_transactions = bank_txs + invoice_txs + binance_txs
    print(f" [PASS] Ingestion Stream extracted {len(all_raw_transactions)} clean rows safely.")

    print("\n--- OMNILEDGER PRECISION NORMALIZATION MATCH RUN ---")
    normalizer = OmniLedgerCurrencyNormalizer(base_currency="USD")
    normalized_ledger_records = []
    total_normalized_capital_usd = 0.0

    for tx in all_raw_transactions:
        try:
            normalized_state = normalizer.normalize_record(tx)
            normalized_ledger_records.append(normalized_state)
            total_normalized_capital_usd += normalized_state.normalized_amount_base
        except Exception as e:
            with open(error_log, mode='a', encoding='utf-8') as err_file:
                err_file.write(f"[NORMALIZATION EXCEPTION] Tx: {tx.transaction_id} | Details: {e}\n")

    print(f" [PASS] Normalization Core mapped {len(normalized_ledger_records)} exact ledger models.")

    print("\n--- OMNILEDGER RELATIONAL PERSISTENCE LAYER WRITE ---")
    db_file = os.path.join(PROJECT_ROOT, "omniledger.db")
    db_manager = OmniLedgerDatabaseManager(db_path=db_file)
    
    # Write normalized balances straight to the local sqlite binary tracking ledger
    saved_count = db_manager.write_normalized_records(normalized_ledger_records)
    print(f" [PASS] SQLite Idempotent Batch commit: {saved_count} records saved securely.")

    print(f"-------------------------------------------------------------------------")
    print(f"📊 Relational System Summary:")
    print(f"      - Storage Ledger Path: {os.path.basename(db_file)}")
    print(f"      - Aggregate Vault Liquidity: ${total_normalized_capital_usd:,.2f} True USD Net State.")

if __name__ == "__main__":
    run_ingestion_pipeline()
