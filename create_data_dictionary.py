# ============================================================
# create_data_dictionary.py
# Generates the Excel data dictionary for business users.
# Run once to produce Docs/data_dictionary.xlsx
# ============================================================

import pandas as pd
import os

os.makedirs("Docs", exist_ok=True)

# ── Define all columns in the output report ──────────────────
output_report = [
    {
        "Column Name":       "referral_details_id",
        "Data Type":         "INTEGER",
        "Description":       "A unique number identifying this log entry.",
        "Example Value":     "101",
        "Can Be Empty?":     "No",
        "Notes":             "Comes from the referral log system. 0 means no log entry exists."
    },
    {
        "Column Name":       "referral_id",
        "Data Type":         "STRING",
        "Description":       "A unique code identifying each referral.",
        "Example Value":     "9331c8f144dad5a3b8e4a10467b4343a",
        "Can Be Empty?":     "No",
        "Notes":             "Each referral has one unique ID."
    },
    {
        "Column Name":       "referral_source",
        "Data Type":         "STRING",
        "Description":       "How the new member was referred to the platform.",
        "Example Value":     "User Sign Up",
        "Can Be Empty?":     "No",
        "Notes":             "One of: User Sign Up, Draft Transaction, Lead."
    },
    {
        "Column Name":       "referral_source_category",
        "Data Type":         "STRING",
        "Description":       "A simplified label for the referral channel. Useful for marketing reporting.",
        "Example Value":     "Online",
        "Can Be Empty?":     "No",
        "Notes":             "User Sign Up = Online. Draft Transaction = Offline. Lead = category from lead record."
    },
    {
        "Column Name":       "referral_at",
        "Data Type":         "DATETIME",
        "Description":       "The date and time the referral was created, in the referrer's local timezone.",
        "Example Value":     "2024-05-01 12:17:31",
        "Can Be Empty?":     "Yes",
        "Notes":             "Empty when referral has no referrer (Draft Transaction source)."
    },
    {
        "Column Name":       "referrer_id",
        "Data Type":         "STRING",
        "Description":       "The unique ID of the existing member who made the referral.",
        "Example Value":     "2c71c5d66c7e12a0b3c200ba6ed3b78e",
        "Can Be Empty?":     "Yes",
        "Notes":             "Empty for Draft Transaction referrals which have no referrer."
    },
    {
        "Column Name":       "referrer_name",
        "Data Type":         "STRING",
        "Description":       "Full name of the member who made the referral.",
        "Example Value":     "John Doe",
        "Can Be Empty?":     "Yes",
        "Notes":             "Empty when no referrer is linked to the referral."
    },
    {
        "Column Name":       "referrer_phone_number",
        "Data Type":         "STRING",
        "Description":       "Phone number of the member who made the referral.",
        "Example Value":     "08xx-xxxx-xxxx",
        "Can Be Empty?":     "Yes",
        "Notes":             "Empty when no referrer is linked."
    },
    {
        "Column Name":       "referrer_homeclub",
        "Data Type":         "STRING",
        "Description":       "The home gym location of the referring member.",
        "Example Value":     "BENHIL",
        "Can Be Empty?":     "Yes",
        "Notes":             "Club name casing is preserved exactly as stored."
    },
    {
        "Column Name":       "referee_id",
        "Data Type":         "STRING",
        "Description":       "The ID of the new member being referred. Only populated for Lead source referrals.",
        "Example Value":     "f1327c9d6d4efee6ad69e7e467b605b9",
        "Can Be Empty?":     "Yes",
        "Notes":             "Only present when referral_source is Lead."
    },
    {
        "Column Name":       "referee_name",
        "Data Type":         "STRING",
        "Description":       "Full name of the new member who was referred.",
        "Example Value":     "Jane Doe",
        "Can Be Empty?":     "Yes",
        "Notes":             "Empty for 3 referrals where name was not recorded."
    },
    {
        "Column Name":       "referee_phone",
        "Data Type":         "STRING",
        "Description":       "Phone number of the new member who was referred.",
        "Example Value":     "08xx-xxxx-xxxx",
        "Can Be Empty?":     "No",
        "Notes":             "Always recorded at time of referral."
    },
    {
        "Column Name":       "referral_status",
        "Data Type":         "STRING",
        "Description":       "The current outcome of the referral.",
        "Example Value":     "Berhasil",
        "Can Be Empty?":     "No",
        "Notes":             "Berhasil = Successful. Menunggu = Pending. Tidak Berhasil = Failed."
    },
    {
        "Column Name":       "num_reward_days",
        "Data Type":         "INTEGER",
        "Description":       "The number of free membership days rewarded to the referrer for a successful referral.",
        "Example Value":     "10",
        "Can Be Empty?":     "No",
        "Notes":             "0 means no reward was assigned. Possible values: 0, 10, 15, 20."
    },
    {
        "Column Name":       "transaction_id",
        "Data Type":         "STRING",
        "Description":       "The unique ID of the transaction linked to this referral.",
        "Example Value":     "bc3a22d1b0c651d0c807a9bdaed08e8d",
        "Can Be Empty?":     "Yes",
        "Notes":             "Empty when no transaction was made for this referral."
    },
    {
        "Column Name":       "transaction_status",
        "Data Type":         "STRING",
        "Description":       "The payment status of the linked transaction.",
        "Example Value":     "Paid",
        "Can Be Empty?":     "Yes",
        "Notes":             "Empty when no transaction exists. Must be PAID for a valid referral reward."
    },
    {
        "Column Name":       "transaction_at",
        "Data Type":         "DATETIME",
        "Description":       "When the transaction took place, in the transaction location's local timezone.",
        "Example Value":     "2024-05-02 11:49:01",
        "Can Be Empty?":     "Yes",
        "Notes":             "Must be after referral_at for a valid referral."
    },
    {
        "Column Name":       "transaction_location",
        "Data Type":         "STRING",
        "Description":       "The gym or club where the transaction occurred.",
        "Example Value":     "GREENVILLE",
        "Can Be Empty?":     "Yes",
        "Notes":             "Club name casing is preserved exactly as stored."
    },
    {
        "Column Name":       "transaction_type",
        "Data Type":         "STRING",
        "Description":       "The type of membership purchased in the transaction.",
        "Example Value":     "New",
        "Can Be Empty?":     "Yes",
        "Notes":             "Must be NEW for a reward-eligible referral. REJOIN is not eligible."
    },
    {
        "Column Name":       "updated_at",
        "Data Type":         "DATETIME",
        "Description":       "The last time this referral record was updated, in local timezone.",
        "Example Value":     "2024-05-01 12:17:31",
        "Can Be Empty?":     "Yes",
        "Notes":             "Empty when referral has no referrer timezone available."
    },
    {
        "Column Name":       "reward_granted_at",
        "Data Type":         "DATETIME",
        "Description":       "When the reward was actually given to the referee.",
        "Example Value":     "2024-06-30 14:00:00",
        "Can Be Empty?":     "Yes",
        "Notes":             "Empty when no reward log entry exists for this referral."
    },
    {
        "Column Name":       "is_business_logic_valid",
        "Data Type":         "BOOLEAN",
        "Description":       "The fraud detection flag. TRUE means the referral passes all business rules and the reward is legitimate. FALSE means at least one rule was broken and this referral needs review.",
        "Example Value":     "TRUE",
        "Can Be Empty?":     "No",
        "Notes":             (
            "FALSE is triggered when: "
            "reward given without successful status; "
            "reward given without a transaction; "
            "paid transaction exists but no reward assigned; "
            "successful referral with no reward; "
            "transaction happened before the referral."
        )
    },
]

# ── Write to Excel ────────────────────────────────────────────
output_path = "Docs/data_dictionary.xlsx"

with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
    df = pd.DataFrame(output_report)
    df.to_excel(writer, sheet_name="Output Report", index=False)

    # auto-size columns
    worksheet = writer.sheets["Output Report"]
    for col in worksheet.columns:
        max_len = max(len(str(cell.value)) if cell.value else 0 for cell in col)
        worksheet.column_dimensions[col[0].column_letter].width = min(max_len + 4, 60)

print(f"Data dictionary saved → {output_path}")