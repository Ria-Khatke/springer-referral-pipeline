
import pandas as pd
import os
import pytz

DATA_DIR   = "Data"
OUTPUT_DIR = "Output"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Read all 7 source CSV files into DataFrames


lead_log               = pd.read_csv(f"{DATA_DIR}/lead_log.csv")
paid_transactions      = pd.read_csv(f"{DATA_DIR}/paid_transactions.csv")
referral_rewards       = pd.read_csv(f"{DATA_DIR}/referral_rewards.csv")
user_logs              = pd.read_csv(f"{DATA_DIR}/user_logs.csv")
user_referral_logs     = pd.read_csv(f"{DATA_DIR}/user_referral_logs.csv")
user_referral_statuses = pd.read_csv(f"{DATA_DIR}/user_referral_statuses.csv")
user_referrals         = pd.read_csv(f"{DATA_DIR}/user_referrals.csv")

print("LOAD COMPLETE")
print(f"  user_referrals:         {len(user_referrals)} rows")
print(f"  user_referral_logs:     {len(user_referral_logs)} rows")
print(f"  user_logs:              {len(user_logs)} rows")
print(f"  paid_transactions:      {len(paid_transactions)} rows")
print(f"  referral_rewards:       {len(referral_rewards)} rows")
print(f"  user_referral_statuses: {len(user_referral_statuses)} rows")
print(f"  lead_log:               {len(lead_log)} rows")

# Cleaning data 


user_referrals["referral_at"]  = pd.to_datetime(user_referrals["referral_at"],  utc=True)
user_referrals["updated_at"]   = pd.to_datetime(user_referrals["updated_at"],   utc=True)

user_referral_logs["created_at"] = pd.to_datetime(user_referral_logs["created_at"], utc=True)

paid_transactions["transaction_at"] = pd.to_datetime(paid_transactions["transaction_at"], utc=True)

lead_log["created_at"] = pd.to_datetime(lead_log["created_at"], utc=True)

# membership_expired_date is a date only (no time), different format
user_logs["membership_expired_date"] = pd.to_datetime(user_logs["membership_expired_date"], utc=False)

# Extract just the number from the string
referral_rewards["reward_value"] = (
    referral_rewards["reward_value"]
    .str.extract(r"(\d+)")   # pull out the digits
    .astype(int)
)


# Club name columns to leave as-is
CLUB_COLS = {
    "homeclub", "transaction_location", "preferred_location", "referrer_homeclub",
    "referral_id", "referrer_id", "referee_id", "user_referral_id",
    "transaction_id", "source_transaction_id", "lead_id", "user_id",
    "id", "phone_number", "referee_phone", "name", "referee_name",
    "referrer_name", "referrer_phone_number"
}

def apply_titlecase(df):
    for col in df.select_dtypes(include="object").columns:
        if col not in CLUB_COLS:
            df[col] = df[col].str.strip().str.title()
    return df

def apply_titlecase(df):
    for col in df.select_dtypes(include="object").columns:
        if col not in CLUB_COLS:
            df[col] = df[col].str.strip().str.title()
    return df

user_referrals  = apply_titlecase(user_referrals)
user_logs       = apply_titlecase(user_logs)
paid_transactions = apply_titlecase(paid_transactions)
lead_log        = apply_titlecase(lead_log)

# Deduplicate before joining 
user_logs = (user_logs
             .sort_values("id", ascending=False)
             .drop_duplicates(subset="user_id")
             .reset_index(drop=True))

lead_log = (lead_log
            .sort_values("id", ascending=False)
            .drop_duplicates(subset="lead_id")
            .reset_index(drop=True))

user_referral_logs = (user_referral_logs
                      .sort_values("created_at", ascending=False)
                      .drop_duplicates(subset="user_referral_id")
                      .reset_index(drop=True))

print(" CLEAN COMPLETE")
print(f"  user_logs after dedup:          {len(user_logs)} rows")
print(f"  lead_log after dedup:           {len(lead_log)} rows")
print(f"  user_referral_logs after dedup: {len(user_referral_logs)} rows")
print(f"  referral_rewards sample:")
print(f"  {referral_rewards[['id','reward_value']].to_string()}")
print("user_referrals referral_id sample:")
print(user_referrals["referral_id"].head(5).tolist())

#coverting timezonses

def convert_utc_to_local(ts, tz_str):
    """Convert a single UTC timestamp to local time using tz_str."""
    if pd.isna(ts) or pd.isna(tz_str):
        return pd.NaT
    try:
        local_tz = pytz.timezone(str(tz_str))
        return ts.astimezone(local_tz).replace(tzinfo=None)
    except Exception:
        return ts.replace(tzinfo=None)
paid_transactions["transaction_at"] = [
    convert_utc_to_local(ts, tz)
    for ts, tz in zip(
        paid_transactions["transaction_at"],
        paid_transactions["timezone_transaction"]
    )
]
lead_log["created_at"] = [
    convert_utc_to_local(ts, tz)
    for ts, tz in zip(
        lead_log["created_at"],
        lead_log["timezone_location"]
    )
]

referral_tz = user_referrals[["referral_id", "referrer_id"]].merge(
    user_logs[["user_id", "timezone_homeclub"]],
    left_on="referrer_id",
    right_on="user_id",
    how="left"
)[["referral_id", "timezone_homeclub"]]

user_referrals = user_referrals.merge(referral_tz, on="referral_id", how="left")

user_referrals["referral_at"] = [
    convert_utc_to_local(ts, tz)
    for ts, tz in zip(
        user_referrals["referral_at"],
        user_referrals["timezone_homeclub"]
    )
]

user_referrals["updated_at"] = [
    convert_utc_to_local(ts, tz)
    for ts, tz in zip(
        user_referrals["updated_at"],
        user_referrals["timezone_homeclub"]
    )
]

log_tz = user_referral_logs[["id", "user_referral_id"]].merge(
    user_referrals[["referral_id", "timezone_homeclub"]],
    left_on="user_referral_id",
    right_on="referral_id",
    how="left"
)[["id", "timezone_homeclub"]]

user_referral_logs = user_referral_logs.merge(log_tz, on="id", how="left")

user_referral_logs["created_at"] = [
    convert_utc_to_local(ts, tz)
    for ts, tz in zip(
        user_referral_logs["created_at"],
        user_referral_logs["timezone_homeclub"]
    )
]

print("TIMEZONE CONVERSION COMPLETE")
print(f"  Sample referral_at (local): {user_referrals['referral_at'].iloc[0]}")
print(f"  Sample transaction_at (local): {paid_transactions['transaction_at'].iloc[0]}")


# Joining all tables

master = user_referrals.merge(
    user_referral_statuses[["id", "description"]].rename(columns={
        "id":          "user_referral_status_id",
        "description": "referral_status"
    }),
    on="user_referral_status_id",
    how="left"
)
master = master.merge(
    referral_rewards[["id", "reward_value"]].rename(columns={
        "id": "referral_reward_id"
    }),
    on="referral_reward_id",
    how="left"
)

master["reward_value"] = master["reward_value"].fillna(0).astype(int)

master = master.merge(
    paid_transactions[[
        "transaction_id", "transaction_status",
        "transaction_at", "transaction_location", "transaction_type"
    ]],
    on="transaction_id",
    how="left"
)

master = master.merge(
    user_logs[[
        "user_id", "name", "phone_number",
        "homeclub", "membership_expired_date", "is_deleted"
    ]].rename(columns={
        "user_id":      "referrer_id",
        "name":         "referrer_name",
        "phone_number": "referrer_phone_number",
        "homeclub":     "referrer_homeclub",
    }),
    on="referrer_id",
    how="left"
)

master = master.merge(
    user_referral_logs[[
        "id", "user_referral_id", "created_at", "is_reward_granted"
    ]].rename(columns={
        "id":               "referral_details_id",
        "user_referral_id": "referral_id",
        "created_at":       "reward_granted_at"
    }),
    on="referral_id",
    how="left"
)
master = master.merge(
    lead_log[["lead_id", "source_category"]],
    left_on="referee_id",
    right_on="lead_id",
    how="left"
)

print("JOIN COMPLETE")
print(f"  Master rows: {len(master)}")
print(f"  Master cols: {len(master.columns)}")
print(f"  Columns: {list(master.columns)}")

#sourcing category

def get_source_category(row):
    src = row["referral_source"]
    if src == "User Sign Up":
        return "Online"
    elif src == "Draft Transaction":
        return "Offline"
    elif src == "Lead":
        return row["source_category"] if pd.notna(row["source_category"]) else "Unknown"
    return "Unknown"

master["referral_source_category"] = master.apply(get_source_category, axis=1)

print("SOURCE CATEGORY COMPLETE")
print(master[["referral_source", "referral_source_category"]].value_counts().to_string())

#FRAUD DETECTION
# Add is_business_logic_valid column (True/False)


def check_business_logic(row):

    # extract values we'll reuse
    reward        = row["reward_value"]
    status        = str(row["referral_status"]).strip() if pd.notna(row["referral_status"]) else ""
    tx_id         = row["transaction_id"]
    tx_status     = str(row["transaction_status"]).strip().upper() if pd.notna(row["transaction_status"]) else ""
    tx_type       = str(row["transaction_type"]).strip().upper() if pd.notna(row["transaction_type"]) else ""
    tx_at         = row["transaction_at"]
    ref_at        = row["referral_at"]
    mem_exp       = row["membership_expired_date"]
    is_deleted    = row["is_deleted"] if pd.notna(row["is_deleted"]) else False
    reward_granted = row["is_reward_granted"] if pd.notna(row["is_reward_granted"]) else False

    # helper flags
    has_reward   = reward > 0
    has_tx       = pd.notna(tx_id)
    tx_after_ref = pd.notna(tx_at) and pd.notna(ref_at) and tx_at > ref_at
    same_month   = (pd.notna(tx_at) and pd.notna(ref_at) and
                    tx_at.year == ref_at.year and tx_at.month == ref_at.month)
    mem_active   = pd.notna(mem_exp) and pd.Timestamp(mem_exp) > pd.Timestamp(ref_at)


    # Invalid 1: reward given but referral not successful
    if has_reward and status != "Berhasil":
        return False

    # Invalid 2: reward given but no transaction linked
    if has_reward and not has_tx:
        return False

    # Invalid 3: no reward but paid transaction exists after referral
    if not has_reward and has_tx and tx_status == "PAID" and tx_after_ref:
        return False

    # Invalid 4: status is Berhasil but no reward assigned
    if status == "Berhasil" and not has_reward:
        return False

    # Invalid 5: transaction happened before referral was created
    if has_tx and pd.notna(tx_at) and pd.notna(ref_at) and tx_at <= ref_at:
        return False

    # Valid 1: full successful referral
    if (has_reward
            and status == "Berhasil"
            and has_tx
            and tx_status == "PAID"
            and tx_type == "NEW"
            and tx_after_ref
            and same_month
            and mem_active
            and not is_deleted
            and reward_granted):
        return True

    # Valid 2: pending or failed with no reward (legitimate state)
    if status in ("Menunggu", "Tidak Berhasil") and not has_reward:
        return True
    return False

master["is_business_logic_valid"] = master.apply(check_business_logic, axis=1)

print(" FRAUD DETECTION COMPLETE")
print(f"  Valid   (True) : {master['is_business_logic_valid'].sum()}")
print(f"  Invalid (False): {(~master['is_business_logic_valid']).sum()}")
print(f"  Total          : {len(master)}")

#OUTPUT

def fmt_dt(val):
    if pd.isna(val):
        return ""
    return pd.Timestamp(val).strftime("%Y-%m-%d %H:%M:%S")

master["referral_at"]     = master["referral_at"].apply(fmt_dt)
master["transaction_at"]  = master["transaction_at"].apply(fmt_dt)
master["updated_at"]      = master["updated_at"].apply(fmt_dt)
master["reward_granted_at"] = master["reward_granted_at"].apply(fmt_dt)

# Spec says null values should not exist in the output
master["transaction_id"]       = master["transaction_id"].fillna("")
master["transaction_status"]   = master["transaction_status"].fillna("")
master["transaction_at"]       = master["transaction_at"].fillna("")
master["transaction_location"] = master["transaction_location"].fillna("")
master["transaction_type"]     = master["transaction_type"].fillna("")
master["referee_id"]           = master["referee_id"].fillna("")
master["referee_name"]         = master["referee_name"].fillna("")
master["referrer_name"]        = master["referrer_name"].fillna("")
master["referrer_phone_number"]= master["referrer_phone_number"].fillna("")
master["referrer_homeclub"]    = master["referrer_homeclub"].fillna("")
master["reward_granted_at"]    = master["reward_granted_at"].fillna("")
master["referral_details_id"]  = master["referral_details_id"].fillna(0).astype(int)
master["referrer_id"] = master["referrer_id"].fillna("")
report = master[[
    "referral_details_id",
    "referral_id",
    "referral_source",
    "referral_source_category",
    "referral_at",
    "referrer_id",
    "referrer_name",
    "referrer_phone_number",
    "referrer_homeclub",
    "referee_id",
    "referee_name",
    "referee_phone",
    "referral_status",
    "reward_value",
    "transaction_id",
    "transaction_status",
    "transaction_at",
    "transaction_location",
    "transaction_type",
    "updated_at",
    "reward_granted_at",
    "is_business_logic_valid",
]].rename(columns={
    "reward_value": "num_reward_days"
})

#  Save to CSV 
output_path = f"{OUTPUT_DIR}/referral_report.csv"
report.to_csv(output_path, index=False)

print("OUTPUT COMPLETE")
print(f"  Rows    : {len(report)}")
print(f"  Columns : {len(report.columns)}")
print(f"  Saved to: {output_path}")
print(f"\nSample (first 3 rows):")
print(report.head(3).to_string())