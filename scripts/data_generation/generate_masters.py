import random
from datetime import timedelta

import pandas as pd

from config import (
    GENERATED_DATA_DIR,
    RANDOM_SEED,
    RECORD_COUNTS,
    TRANSACTION_START_DATE,
    TRANSACTION_END_DATE,
    ensure_output_directories,
)

# --------------------------------------------------
# 1. INITIALIZE RANDOM GENERATOR
# --------------------------------------------------

random.seed(RANDOM_SEED)

# --------------------------------------------------
# 2. PARTNER MASTER REFERENCE DATA
# --------------------------------------------------

PARTNER_TYPES = [
    "DSA",
    "AUTO_DEALER",
    "TRACTOR_DEALER",
    "CONNECTOR",
]

PARTNER_STATUSES = [
    "ACTIVE",
    "INACTIVE",
    "SUSPENDED",
]

PARTNER_STATUS_WEIGHTS = [0.75, 0.15, 0.10]

CITY_STATE_MAPPING = {
    "Hyderabad": "Telangana",
    "Bengaluru": "Karnataka",
    "Chennai": "Tamil Nadu",
    "Mumbai": "Maharashtra",
    "Pune": "Maharashtra",
    "Delhi": "Delhi",
    "Jaipur": "Rajasthan",
    "Ahmedabad": "Gujarat",
    "Kochi": "Kerala",
    "Lucknow": "Uttar Pradesh",
}

PARTNER_NAMES = [
    "Apex Financial Services",
    "Prime Auto Associates",
    "Metro Business Solutions",
    "Sunrise Finance Network",
    "Global Partner Services",
    "Reliable Credit Associates",
    "Smart Finance Solutions",
    "Unity Business Network",
    "Vision Financial Partners",
    "Trust Auto Services",
]

# --------------------------------------------------
# 3. HELPER FUNCTION: GENERATE RANDOM DATE
# --------------------------------------------------

def random_date(start_date, end_date):
    """Generate a random date within the supplied range."""

    total_days = (end_date - start_date).days

    return start_date + timedelta(
        days=random.randint(0, total_days)
    )


# --------------------------------------------------
# 4. GENERATE PARTNER MASTER
# --------------------------------------------------

def generate_partner_master():

    records = []

    total_partners = RECORD_COUNTS["src_partner_master"]

    for i in range(1, total_partners + 1):

        partner_id = f"PARTNER{i:03d}"

        partner_name = (
            f"{random.choice(PARTNER_NAMES)} {i:03d}"
        )

        city = random.choice(list(CITY_STATE_MAPPING.keys()))
        state = CITY_STATE_MAPPING[city]

        partner_type = random.choice(PARTNER_TYPES)

        partner_status = random.choices(
            PARTNER_STATUSES,
            weights=PARTNER_STATUS_WEIGHTS,
            k=1,
        )[0]

        onboarding_date = random_date(
            TRANSACTION_START_DATE,
            TRANSACTION_END_DATE,
        )

        created_at = pd.Timestamp(onboarding_date) + pd.Timedelta(
            hours=random.randint(9, 18),
            minutes=random.randint(0, 59),
        )

        updated_at = created_at + pd.Timedelta(
            days=random.randint(0, 60)
        )

        records.append({
            "partner_id": partner_id,
            "partner_name": partner_name,
            "partner_type": partner_type,
            "city": city,
            "state": state,
            "onboarding_date": onboarding_date.isoformat(),
            "partner_status": partner_status,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
        })

    return pd.DataFrame(records)


# --------------------------------------------------
# 5. GENERATE PRODUCT MASTER
# --------------------------------------------------

def generate_product_master():

    records = [
        {
            "product_id": "PROD001",
            "product_name": "New Car Loan",
            "product_category": "LOAN",
            "commission_basis": "DISBURSED_AMOUNT",
            "product_status": "ACTIVE",
        },
        {
            "product_id": "PROD002",
            "product_name": "Used Car Loan",
            "product_category": "LOAN",
            "commission_basis": "DISBURSED_AMOUNT",
            "product_status": "ACTIVE",
        },
        {
            "product_id": "PROD003",
            "product_name": "Tractor Loan",
            "product_category": "LOAN",
            "commission_basis": "DISBURSED_AMOUNT",
            "product_status": "ACTIVE",
        },
        {
            "product_id": "PROD004",
            "product_name": "Personal Loan",
            "product_category": "LOAN",
            "commission_basis": "DISBURSED_AMOUNT",
            "product_status": "ACTIVE",
        },
        {
            "product_id": "PROD005",
            "product_name": "Small Business Banking",
            "product_category": "LOAN",
            "commission_basis": "DISBURSED_AMOUNT",
            "product_status": "ACTIVE",
        },
        {
            "product_id": "PROD006",
            "product_name": "CASA",
            "product_category": "CASA",
            "commission_basis": "CASA_AMB",
            "product_status": "ACTIVE",
        },
    ]

    return pd.DataFrame(records)


# --------------------------------------------------
# 6. EXPORT DATASETS TO CSV
# --------------------------------------------------

def export_dataset(dataframe, dataset_name):

    output_path = GENERATED_DATA_DIR / f"{dataset_name}.csv"

    dataframe.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    print(
        f"{dataset_name}: {len(dataframe)} records exported"
    )


# --------------------------------------------------
# 7. MAIN EXECUTION
# --------------------------------------------------

def main():

    ensure_output_directories()

    partner_df = generate_partner_master()
    product_df = generate_product_master()

    export_dataset(partner_df, "src_partner_master")
    export_dataset(product_df, "src_product_master")

    print("\nMaster data generation completed.")


if __name__ == "__main__":
    main()