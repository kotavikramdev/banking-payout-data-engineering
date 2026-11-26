import random
from datetime import timedelta

import pandas as pd

from config import (
    GENERATED_DATA_DIR,
    RANDOM_SEED,
    RECORD_COUNTS,
    TRANSACTION_START_DATE,
    TRANSACTION_END_DATE,
    AS_OF_DATE,
    ensure_output_directories,
)


# --------------------------------------------------
# 1. INITIALIZE RANDOM GENERATOR
# --------------------------------------------------

random.seed(RANDOM_SEED)


# --------------------------------------------------
# 2. AGREEMENT REFERENCE DATA
# --------------------------------------------------

AGREEMENT_STATUSES = [
    "ACTIVE",
    "EXPIRED",
    "TERMINATED",
    "SUSPENDED",
]

AGREEMENT_STATUS_WEIGHTS = [0.65, 0.15, 0.10, 0.10]


# --------------------------------------------------
# 3. HELPER FUNCTION
# --------------------------------------------------

def random_date(start_date, end_date):
    """Generate a random date within a range."""

    total_days = (end_date - start_date).days

    return start_date + timedelta(
        days=random.randint(0, total_days)
    )


# --------------------------------------------------
# 4. GENERATE PARTNER AGREEMENTS
# --------------------------------------------------

def generate_partner_agreements(partner_df):

    records = []

    total_agreements = RECORD_COUNTS[
        "src_partner_agreements"
    ]

    partner_ids = partner_df["partner_id"].tolist()

    # Build a lookup of each partner's onboarding date.
    onboarding_dates = dict(
        zip(
            partner_df["partner_id"],
            pd.to_datetime(partner_df["onboarding_date"]).dt.date
        )
    )

    # Every partner receives at least one agreement.
    agreements_per_partner = {
        partner_id: 1 for partner_id in partner_ids
    }

    # Select partners with enough time for two sequential agreements.
    eligible_partners = [
        partner_id
        for partner_id in partner_ids
        if onboarding_dates[partner_id]
        <= TRANSACTION_END_DATE - timedelta(days=90)
    ]

    additional_count = total_agreements - len(partner_ids)

    additional_partners = random.sample(
        eligible_partners,
        additional_count
    )

    for partner_id in additional_partners:
        agreements_per_partner[partner_id] += 1

    agreement_counter = 1

    for partner_id, agreement_count in agreements_per_partner.items():

        onboarding_date = onboarding_dates[partner_id]

        # Select an initial start date after onboarding.
        if agreement_count == 2:
            latest_start_date = (
                TRANSACTION_END_DATE - timedelta(days=90)
            )
        else:
            latest_start_date = TRANSACTION_END_DATE

        agreement_start = random_date(
            onboarding_date,
            latest_start_date
        )

        for version in range(agreement_count):

            effective_from = agreement_start

            # Generate the first agreement's end date
            # so the second agreement can begin afterward.
            if version < agreement_count - 1:

                remaining_days = (
                    TRANSACTION_END_DATE - effective_from
                ).days

                period_days = random.randint(
                    15,
                    min(90, remaining_days)
                )

                effective_to = (
                    effective_from + timedelta(days=period_days)
                )

            else:
                effective_to = None

            # Determine whether the agreement is valid on the as-of date.
            is_currently_valid = (
                effective_from <= AS_OF_DATE
                and (
                    effective_to is None
                    or effective_to > AS_OF_DATE
                )
            )

            if is_currently_valid:

                agreement_status = random.choices(
                    ["ACTIVE", "SUSPENDED"],
                    weights=[85, 15],
                    k=1,
                )[0]

            else:

                agreement_status = random.choices(
                    ["EXPIRED", "TERMINATED"],
                    weights=[80, 20],
                    k=1,
                )[0]

            # Commission eligibility is a separate business attribute.
            if agreement_status == "ACTIVE":
                commission_eligible = random.choice([True, False])

            else:
                commission_eligible = False

            created_at = pd.Timestamp(effective_from) + pd.Timedelta(
                hours=10
            )

            if effective_to is not None:
                updated_at = pd.Timestamp(effective_to)
            else:
                updated_at = created_at + pd.Timedelta(days=30)

            records.append({
                "agreement_id": f"AGR{agreement_counter:04d}",
                "partner_id": partner_id,
                "agreement_status": agreement_status,
                "effective_from": effective_from.isoformat(),
                "effective_to": (
                    effective_to.isoformat()
                    if effective_to else None
                ),
                "commission_eligible": commission_eligible,
                "agreement_document_ref": (
                    f"DOC_{agreement_counter:04d}"
                ),
                "created_at": created_at.isoformat(),
                "updated_at": updated_at.isoformat(),
            })

            agreement_counter += 1

            if effective_to is not None:
                agreement_start = effective_to

    return pd.DataFrame(records)


# --------------------------------------------------
# 5. EXPORT DATASET
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
# 6. MAIN EXECUTION
# --------------------------------------------------

def main():

    ensure_output_directories()

    partner_path = (
        GENERATED_DATA_DIR / "src_partner_master.csv"
    )

    if not partner_path.exists():
        raise FileNotFoundError(
            "Partner master CSV not found. "
            "Generate partner master data first."
        )

    partner_df = pd.read_csv(partner_path)

    # Generate agreements.
    agreement_df = generate_partner_agreements(
        partner_df
    )

    export_dataset(
        agreement_df,
        "src_partner_agreements",
    )

    # Generate KYC history.
    kyc_df = generate_partner_kyc(
        partner_df
    )

    export_dataset(
        kyc_df,
        "src_partner_kyc",
    )

    print("\nBusiness rule data generation completed.")


# --------------------------------------------------
# 7. KYC REFERENCE DATA
# --------------------------------------------------

KYC_STATUSES = [
    "PENDING",
    "VERIFIED",
    "REJECTED",
    "EXPIRED",
]


# --------------------------------------------------
# 8. GENERATE PARTNER KYC HISTORY
# --------------------------------------------------

def generate_partner_kyc(partner_df):

    records = []

    total_kyc_records = RECORD_COUNTS["src_partner_kyc"]

    partner_ids = partner_df["partner_id"].tolist()

    # Every partner receives at least one KYC record.
    kyc_per_partner = {
        partner_id: 1 for partner_id in partner_ids
    }

    onboarding_dates = dict(
        zip(
            partner_df["partner_id"],
            pd.to_datetime(partner_df["onboarding_date"]).dt.date
        )
    )

    # Distribute remaining 30 records.
    eligible_partners = [
        partner_id
        for partner_id, onboarding_date in onboarding_dates.items()
        if onboarding_date <= TRANSACTION_END_DATE - timedelta(days=15)
    ]

    partners_with_multiple_records = set(
        random.sample(eligible_partners, 30)
    )

    for partner_id in partners_with_multiple_records:
        kyc_per_partner[partner_id] += 1

    kyc_counter = 1

    for partner_id, record_count in kyc_per_partner.items():
        
        onboarding_date = onboarding_dates[partner_id]

        if record_count == 2:
            latest_start_date = TRANSACTION_END_DATE - timedelta(days=15)
        else:
            latest_start_date = TRANSACTION_END_DATE

        effective_from = random_date(
            onboarding_date,
            latest_start_date
        )

        previous_status = None

        for version in range(record_count):

            # Assign historical status transitions.
            if version == 0:
                kyc_status = random.choice(
                    ["PENDING", "VERIFIED", "REJECTED"]
                )

            else:
                previous_status = kyc_status

                if previous_status == "PENDING":
                    kyc_status = random.choice(
                        ["VERIFIED", "REJECTED"]
                    )

                elif previous_status == "REJECTED":
                    kyc_status = random.choice(
                        ["PENDING", "VERIFIED"]
                    )

                else:
                    kyc_status = random.choice(
                        ["VERIFIED", "EXPIRED"]
                    )

            # Create sequential validity periods.
            if version == record_count - 1:
                effective_to = None
            else:
                remaining_days = (TRANSACTION_END_DATE - effective_from).days

                period_days = min(
                    random.randint(15, 120),
                    remaining_days
                )

                effective_to = effective_from + timedelta(days=period_days)

            verification_date = None
            rejection_reason = None

            if kyc_status == "VERIFIED":
                verification_date = effective_from.isoformat()

            elif kyc_status == "REJECTED":
                rejection_reason = random.choice([
                    "DOCUMENT_MISMATCH",
                    "INVALID_DOCUMENT",
                    "INCOMPLETE_DOCUMENTATION",
                    "IDENTITY_VERIFICATION_FAILED",
                ])

            created_at = (
                pd.Timestamp(effective_from)
                + pd.Timedelta(hours=11)
            )

            updated_at = (
                pd.Timestamp(effective_to)
                if effective_to is not None
                else created_at + pd.Timedelta(days=5)
            )

            records.append({
                "kyc_record_id": f"KYC{kyc_counter:04d}",
                "partner_id": partner_id,
                "kyc_status": kyc_status,
                "effective_from": effective_from.isoformat(),
                "effective_to": (
                    effective_to.isoformat()
                    if effective_to else None
                ),
                "verification_date": verification_date,
                "rejection_reason": rejection_reason,
                "created_at": created_at.isoformat(),
                "updated_at": updated_at.isoformat(),
            })

            kyc_counter += 1

            if effective_to is not None:
                effective_from = effective_to

    return pd.DataFrame(records)


if __name__ == "__main__":
    main()