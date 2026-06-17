# ============================================================
# Springer Capital — Data Profiling Script
# Profiles all 7 source tables and saves results to CSV.
# For each column: null count, distinct count, min, max value.
# ============================================================

import pandas as pd
import os

DATA_DIR   = "Data"
OUTPUT_DIR = "Output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Load all 7 tables ─────────────────────────────────────────
tables = {
    "lead_log":               pd.read_csv(f"{DATA_DIR}/lead_log.csv"),
    "paid_transactions":      pd.read_csv(f"{DATA_DIR}/paid_transactions.csv"),
    "referral_rewards":       pd.read_csv(f"{DATA_DIR}/referral_rewards.csv"),
    "user_logs":              pd.read_csv(f"{DATA_DIR}/user_logs.csv"),
    "user_referral_logs":     pd.read_csv(f"{DATA_DIR}/user_referral_logs.csv"),
    "user_referral_statuses": pd.read_csv(f"{DATA_DIR}/user_referral_statuses.csv"),
    "user_referrals":         pd.read_csv(f"{DATA_DIR}/user_referrals.csv"),
}

# ── Profile every column in every table ───────────────────────
profile_rows = []

for table_name, df in tables.items():
    for col in df.columns:
        series = df[col]
        profile_rows.append({
            "table_name":     table_name,
            "column_name":    col,
            "data_type":      str(series.dtype),
            "row_count":      len(series),
            "null_count":     int(series.isna().sum()),
            "null_pct":       round(series.isna().mean() * 100, 2),
            "distinct_count": int(series.nunique(dropna=False)),
            "min_value":      str(series.dropna().min()) if not series.dropna().empty else "N/A",
            "max_value":      str(series.dropna().max()) if not series.dropna().empty else "N/A",
        })

# ── Save and print results ────────────────────────────────────
profiling_report = pd.DataFrame(profile_rows)
profiling_report.to_csv(f"{OUTPUT_DIR}/profiling_report.csv", index=False)

print(f"Profiling complete — {len(profiling_report)} columns profiled across {len(tables)} tables")
print(profiling_report.to_string())