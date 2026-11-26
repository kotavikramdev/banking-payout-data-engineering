from pathlib import Path
from datetime import date

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

# Locate the repository root from this file's location.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Output directories for synthetic source data.
GENERATED_DATA_DIR = PROJECT_ROOT / "data" / "generated"
QUALITY_SCENARIOS_DIR = PROJECT_ROOT / "data" / "quality_scenarios"


# --------------------------------------------------
# 2. DATA GENERATION SETTINGS
# --------------------------------------------------

# Fixed seed ensures reproducible random data.
RANDOM_SEED = 42


# --------------------------------------------------
# 3. BUSINESS DATE RANGE
# --------------------------------------------------

TRANSACTION_START_DATE = date(2025, 1, 1)
TRANSACTION_END_DATE = date(2026, 10, 31)
AS_OF_DATE = date(2026, 10, 31)


# --------------------------------------------------
# 4. RECORD VOLUMES
# --------------------------------------------------

RECORD_COUNTS = {
    "src_partner_master": 100,
    "src_product_master": 6,
    "src_partner_agreements": 120,
    "src_partner_kyc": 130,
    "src_disbursements": 2000,
    "src_casa_acquisitions": 1000,
    "src_rate_cards": 100,
    "src_incentive_slabs": 40,
    "src_tax_rules": 8,
    "src_adjustments": 150,
    "src_partner_invoices": 100,
}


# --------------------------------------------------
# 5. CURRENCY AND DATA STANDARDS
# --------------------------------------------------

DEFAULT_CURRENCY = "INR"

# Use these standards when generating and exporting data.
MONEY_DECIMAL_PLACES = 2
RATE_DECIMAL_PLACES = 6


# --------------------------------------------------
# 6. OUTPUT DIRECTORY SETUP
# --------------------------------------------------

def ensure_output_directories():
    """Create the required output directories if absent."""

    GENERATED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    QUALITY_SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 7. CONFIGURATION SUMMARY
# --------------------------------------------------

def display_configuration():
    """Display the active synthetic data generation settings."""

    print("Synthetic Data Generation Configuration")
    print("-" * 45)

    print(f"Project root       : {PROJECT_ROOT}")
    print(f"Random seed        : {RANDOM_SEED}")
    print(f"Transaction start  : {TRANSACTION_START_DATE}")
    print(f"Transaction end    : {TRANSACTION_END_DATE}")
    print(f"Generated data     : {GENERATED_DATA_DIR}")

    print("\nPlanned record counts:")

    for dataset, count in RECORD_COUNTS.items():
        print(f"{dataset:<30} {count:>6,}")

    print("-" * 45)


if __name__ == "__main__":
    ensure_output_directories()
    display_configuration()