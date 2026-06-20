import csv
import os
from datetime import datetime
from src.core.models import FinancialTransaction

class OmniLedgerIngestionAdapter:
    @staticmethod
    def _sanitize_headers(fieldnames: list) -> list:
        return [name.strip() for name in fieldnames] if fieldnames else []

    @staticmethod
    def parse_bank_feed(filepath: str, error_log: str) -> list:
        transactions = []
        if not os.path.exists(filepath):
            return transactions

        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            reader.fieldnames = OmniLedgerIngestionAdapter._sanitize_headers(reader.fieldnames)

            for row in reader:
                try:
                    tx_id = row.get('Transaction_ID', '').strip()
                    raw_amt = row.get('Clear_Amount', '').strip()
                    currency = row.get('Asset_Currency', '').strip().upper()
                    date_str = row.get('Posting_Date', '').strip()

                    amount = float(raw_amt)
                    timestamp = datetime.strptime(date_str, "%Y-%m-%d")

                    tx = FinancialTransaction(
                        transaction_id=tx_id,
                        account_source='CHASE_BANK',
                        raw_amount=amount,
                        currency_ticker=currency,
                        timestamp=timestamp,
                        metadata_payload={'account_no': row.get('Account_No', ''), 'desc': row.get('Description', '')}
                    )
                    tx.validate_integrity_bounds()
                    transactions.append(tx)

                except Exception as e:
                    with open(error_log, mode='a', encoding='utf-8') as err_file:
                        err_file.write(f"[INGESTION EXCEPTION] [CHASE_BANK] Row: {row} | Details: {e}\n")
        return transactions

    @staticmethod
    def parse_invoice_feed(filepath: str, error_log: str) -> list:
        transactions = []
        if not os.path.exists(filepath):
            return transactions

        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            reader.fieldnames = OmniLedgerIngestionAdapter._sanitize_headers(reader.fieldnames)

            for row in reader:
                try:
                    tx_id = row.get('inv_reference', '').strip()
                    raw_amt = row.get('bill_val', '').strip()
                    currency = row.get('currency_type', '').strip().upper()
                    date_str = row.get('date_issued', '').strip()

                    amount = float(raw_amt)
                    timestamp = datetime.strptime(date_str, "%Y-%m-%d")

                    tx = FinancialTransaction(
                        transaction_id=tx_id,
                        account_source='INVOICE_LEDGER',
                        raw_amount=amount,
                        currency_ticker=currency,
                        timestamp=timestamp,
                        metadata_payload={'counterparty': row.get('counterparty', '')}
                    )
                    tx.validate_integrity_bounds()
                    transactions.append(tx)

                except Exception as e:
                    with open(error_log, mode='a', encoding='utf-8') as err_file:
                        err_file.write(f"[INGESTION EXCEPTION] [INVOICE_LEDGER] Row: {row} | Details: {e}\n")
        return transactions

    @staticmethod
    def parse_binance_feed(filepath: str, error_log: str) -> list:
        transactions = []
        if not os.path.exists(filepath):
            return transactions

        with open(filepath, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            reader.fieldnames = OmniLedgerIngestionAdapter._sanitize_headers(reader.fieldnames)

            for row in reader:
                try:
                    tx_id = row.get('TxId', '').strip()
                    raw_amt = row.get('NetValue', '').strip()
                    currency = row.get('Asset', '').strip().upper()
                    date_str = row.get('EventTime', '').strip()

                    amount = float(raw_amt)
                    timestamp = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")

                    tx = FinancialTransaction(
                        transaction_id=tx_id,
                        account_source='BINANCE_EXCHANGE',
                        raw_amount=amount,
                        currency_ticker=currency,
                        timestamp=timestamp,
                        metadata_payload={'op_type': row.get('OpType', '')}
                    )
                    tx.validate_integrity_bounds()
                    transactions.append(tx)

                except Exception as e:
                    with open(error_log, mode='a', encoding='utf-8') as err_file:
                        err_file.write(f"[INGESTION EXCEPTION] [BINANCE_EXCHANGE] Row: {row} | Details: {e}\n")
        return transactions
