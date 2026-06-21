import sqlite3

class OmniLedgerQueryEngine:
    def __init__(self, db_path: str = "omniledger.db"):
        self.db_path = db_path

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def extract_currency_exposure(self) -> list[dict]:
        """Calculates consolidated asset exposure concentration metrics grouped by original currency."""
        query = """
        SELECT original_currency, COUNT(*), SUM(original_amount), SUM(normalized_amount_base)
        FROM normalized_ledger
        GROUP BY original_currency
        ORDER BY SUM(normalized_amount_base) DESC;
        """
        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                results.append({
                    "currency": row[0],
                    "count": row[1],
                    "total_original": row[2],
                    "total_normalized_usd": row[3]
                })
        return results

    def extract_risk_profile(self) -> list[dict]:
        """Stratifies systemic operational risk exposures committed across historical ledgers."""
        query = """
        SELECT risk_level, COUNT(*), SUM(normalized_amount_base)
        FROM normalized_ledger
        GROUP BY risk_level
        ORDER BY SUM(normalized_amount_base) DESC;
        """
        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                results.append({
                    "risk_level": row[0],
                    "count": row[1],
                    "total_normalized_usd": row[2]
                })
        return results

    def extract_system_dependency_risk(self) -> list[dict]:
        """Answser: Which source tracking system presents the largest asset capital footprint?"""
        query = """
        SELECT account_source, COUNT(*), SUM(normalized_amount_base), AVG(normalized_amount_base)
        FROM normalized_ledger
        GROUP BY account_source
        ORDER BY SUM(normalized_amount_base) DESC;
        """
        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                results.append({
                    "source": row[0],
                    "count": row[1],
                    "total_usd": row[2],
                    "avg_usd": row[3]
                })
        return results

    def extract_critical_threshold_violations(self, limit: float = 1000.0) -> list[dict]:
        """Answer: Which active accounts or records currently exceed risk safety bounds?"""
        query = """
        SELECT transaction_id, account_source, normalized_amount_base, risk_level
        FROM normalized_ledger
        WHERE normalized_amount_base >= ? AND risk_level IN ('MEDIUM', 'HIGH')
        ORDER BY normalized_amount_base DESC;
        """
        results = []
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (limit,))
            for row in cursor.fetchall():
                results.append({
                    "tx_id": row[0],
                    "source": row[1],
                    "amount_usd": row[2],
                    "risk": row[3]
                })
        return results
