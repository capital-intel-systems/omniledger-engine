from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any

@dataclass(frozen=True)
class FinancialTransaction:
    """Immutable data contract defining a single multi-source transaction entry."""
    transaction_id: str
    account_source: str       # e.g., 'CHASE_BANK', 'INVOICE_LEDGER', 'BINANCE_EXCHANGE'
    raw_amount: float
    currency_ticker: str     # e.g., 'USD', 'EUR', 'GBP'
    timestamp: datetime
    metadata_payload: Dict[str, Any] = field(default_factory=dict)

    def validate_integrity_bounds(self):
        if not self.transaction_id:
            raise ValueError("Transaction ID identifier cannot be empty.")
        if not self.account_source:
            raise ValueError("Account source system indicator cannot be empty.")
        if self.raw_amount <= 0.0:
            raise ValueError(f"Financial volume must be strictly positive: {self.raw_amount}")
        if len(self.currency_ticker) < 3:
            raise ValueError(f"Invalid standard asset currency ticker string: {self.currency_ticker}")

@dataclass(frozen=True)
class NormalizedLedgerState:
    """Baseline record representing an entry after parsing and multi-currency normalization."""
    transaction_id: str
    account_source: str
    original_amount: float
    original_currency: str
    normalized_amount_base: float
    base_currency_ticker: str
    spot_conversion_rate: float
    audit_status: str
    risk_level: str
    processed_at: datetime = field(default_factory=datetime.utcnow)
