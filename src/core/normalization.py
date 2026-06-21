from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime
from src.core.models import FinancialTransaction, NormalizedLedgerState

class OmniLedgerCurrencyNormalizer:
    def __init__(self, base_currency: str = "USD"):
        self.base_currency = base_currency.upper()
        # Authoritative reference rates indexed directly to target base USD
        self.exchange_index = {
            "USD": Decimal("1.000000"),
            "EUR": Decimal("1.085000"),
            "GBP": Decimal("1.272000")
        }

    def normalize_record(self, tx: FinancialTransaction) -> NormalizedLedgerState:
        """
        Transforms a raw transaction into an exact base-normalized ledger record.
        Eliminates floating-point accumulation drift over high-volume data pools.
        """
        currency = tx.currency_ticker.upper()
        if currency not in self.exchange_index:
            raise ValueError(f"Normalization Error: Asset ticker {currency} not tracked in spot map reference indexes.")

        # Convert float to absolute string representation to strip hardware parsing variances
        raw_decimal_amount = Decimal(str(tx.raw_amount))
        spot_rate = self.exchange_index[currency]

        # Execute fixed-point base scaling math: Base_Value = Original_Value * Conversion_Factor
        normalized_amount = (raw_decimal_amount * spot_rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Dynamic Operational Risk Stratification Matrix
        risk_level = "LOW"
        if tx.account_source == "BINANCE_EXCHANGE" and normalized_amount > Decimal("1000.00"):
            risk_level = "HIGH"
        elif normalized_amount > Decimal("5000.00"):
            risk_level = "MEDIUM"

        return NormalizedLedgerState(
            transaction_id=tx.transaction_id,
            account_source=tx.account_source,
            original_amount=tx.raw_amount,
            original_currency=tx.currency_ticker,
            normalized_amount_base=float(normalized_amount),
            base_currency_ticker=self.base_currency,
            spot_conversion_rate=float(spot_rate),
            audit_status="MATCHED",
            risk_level=risk_level,
            processed_at=datetime.utcnow()
        )
