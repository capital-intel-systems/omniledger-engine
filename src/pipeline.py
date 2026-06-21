import os
import sys

from src.core.ingestion import OmniLedgerIngestionAdapter
from src.core.normalization import OmniLedgerCurrencyNormalizer

def run_ingestion_pipeline():
    # File locations resolved relative to execution root
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
            
            # Print exact conversion tracking metrics for all non-USD assets
            if normalized_state.original_currency != "USD":
                print(f"   Normalized {normalized_state.transaction_id}: {normalized_state.original_amount} {normalized_state.original_currency} -> {normalized_state.normalized_amount_base} USD (Rate: {normalized_state.spot_conversion_rate})")
        except Exception as e:
            with open(error_log, mode='a', encoding='utf-8') as err_file:
                err_file.write(f"[NORMALIZATION EXCEPTION] Tx: {tx.transaction_id} | Details: {e}\n")

    print(f"-------------------------------------------------------------------------")
    print(f"📊 Normalization Engine Summary:")
    print(f"      - Processed Ledger Count: {len(normalized_ledger_records)} Valid Baseline States Mapped.")
    print(f"      - Aggregate Vault Liquidity: ${total_normalized_capital_usd:,.2f} True USD Net State.")

    if os.path.exists(error_log):
        print(f"\n⚠️ Isolated Pipeline Deviations Trapped:")
        with open(error_log, 'r') as log:
            for line in log:
                if "[NORMALIZATION" in line:
                    print(f"  {line.strip()}")

if __name__ == "__main__":
    run_ingestion_pipeline()
