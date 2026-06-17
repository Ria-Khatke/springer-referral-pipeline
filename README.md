# Springer Capital — Referral Data Pipeline

A data engineering pipeline that profiles, cleans, processes, and 
fraud-checks referral programme data. Outputs a 46-row validated 
referral report.

## Project Structure

## What the Pipeline Does

| Step | Description |
|------|-------------|
| Load | Reads all 7 CSV source files |
| Profile | Null counts, distinct counts, min/max per column |
| Clean | Parses timestamps, fixes data types, title-cases strings |
| Process | UTC to local timezone conversion, joins all 7 tables |
| Detect | Applies fraud detection rules → is_business_logic_valid |
| Output | Saves referral_report.csv (46 rows, 22 columns) |

## Requirements

- Docker Desktop installed and running
- The 7 source CSV files in the Data/ folder

## How to Run with Docker

### Step 1 — Build the image

```bash
docker build -t springer-pipeline .
```

### Step 2 — Run the container

**Mac / Linux:**
```bash
docker run --rm -v "$(pwd)/Output:/app/Output" springer-pipeline
```

**Windows PowerShell:**
```bash
docker run --rm -v "${PWD}/Output:/app/Output" springer-pipeline
```

### Step 3 — Get your output

After the container finishes, check the Output/ folder:
- `referral_report.csv`  — 46-row fraud detection report
- `profiling_report.csv` — data quality profile of all 7 tables

## How to Run Locally (without Docker)

### Step 1 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Run profiling

```bash
python profiling.py
```

### Step 3 — Run pipeline

```bash
python pipeline.py
```

## Output Report Columns

| Column | Type | Description |
|--------|------|-------------|
| referral_details_id | INTEGER | Unique log entry ID |
| referral_id | STRING | Unique referral identifier |
| referral_source | STRING | How the referral happened |
| referral_source_category | STRING | Online / Offline / lead category |
| referral_at | DATETIME | Referral creation time (local timezone) |
| referrer_id | STRING | ID of referring member |
| referrer_name | STRING | Name of referring member |
| referrer_phone_number | STRING | Referrer phone number |
| referrer_homeclub | STRING | Referrer home gym |
| referee_id | STRING | ID of referred person |
| referee_name | STRING | Name of new member |
| referee_phone | STRING | New member phone number |
| referral_status | STRING | Berhasil / Menunggu / Tidak Berhasil |
| num_reward_days | INTEGER | Reward days granted (0 = none) |
| transaction_id | STRING | Linked transaction ID |
| transaction_status | STRING | PAID / PENDING / FAILED |
| transaction_at | DATETIME | Transaction time (local timezone) |
| transaction_location | STRING | Gym where transaction occurred |
| transaction_type | STRING | NEW / REJOIN |
| updated_at | DATETIME | Last update to referral record |
| reward_granted_at | DATETIME | When reward was given |
| is_business_logic_valid | BOOLEAN | TRUE = valid, FALSE = potential fraud |

## Fraud Detection Rules

`is_business_logic_valid = FALSE` when any of these fire:

| # | Condition |
|---|-----------|
| 1 | Reward > 0 AND status is not Berhasil |
| 2 | Reward > 0 AND no transaction ID |
| 3 | No reward AND paid transaction exists after referral |
| 4 | Status is Berhasil AND reward is 0 or null |
| 5 | Transaction date is before referral date |

`is_business_logic_valid = TRUE` when:
- All 10 success criteria met (reward, status, PAID, NEW, timing, membership active, not deleted, reward granted)
- OR status is Pending/Failed with no reward assigned
