import os
import sys

# Self-Healing Path Anchor: Dynamically identifies the repo base folder
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.core.ingestion import OmniLedgerIngestionAdapter

def run_ingestion_pipeline():
    bank_csv = os.path.join("samples", "bank_chase_raw.csv")
    invoice_csv = os.path.join("samples", "invoices_raw.csv")
    binance_csv = os.path.join("samples", "binance_ledger_raw.csv")
    error_log = os.path.join("samples", "corrupt_records.log")

    if os.path.exists(error_log):
        os.remove(error_log)

    print("--- OMNILEDGER INTEGRATED INGESTION RUN ---")
    
    bank_txs = OmniLedgerIngestionAdapter.parse_bank_feed(bank_csv, error_log)
    invoice_txs = OmniLedgerIngestionAdapter.parse_invoice_feed(invoice_csv, error_log)
    binance_txs = OmniLedgerIngestionAdapter.parse_binance_feed(binance_csv, error_log)

    total_clean_records = len(bank_txs) + len(invoice_txs) + len(binance_txs)

    print(f" [PASS] Chase Ingestion:     {len(bank_txs)} Valid Transactions Extracted.")
    print(f" [PASS] Invoice Ingestion:   {len(invoice_txs)} Valid Transactions Extracted.")
    print(f" [PASS] Binance Ingestion:   {len(binance_txs)} Valid Transactions Extracted.")
    print(f"-------------------------------------------------------")
    print(f"📊 Pipeline Target Yield: {total_clean_records} Normalized Records Loaded.")

    if os.path.exists(error_log):
        print(f"\n⚠️ Defensive Exception Ledger Generated: {error_log}")
        print("Captured and isolated anomalous payloads:")
        with open(error_log, 'r') as log:
            for line in log:
                print(f"  {line.strip()}")

if __name__ == "__main__":
    run_ingestion_pipeline()
