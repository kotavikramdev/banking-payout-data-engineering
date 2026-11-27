import random
from datetime import timedelta

import pandas as pd

try:
    from .config import (
        PROJECT_ROOT,
        GENERATED_DATA_DIR,
        RANDOM_SEED,
        TRANSACTION_START_DATE,
        TRANSACTION_END_DATE,
        RECORD_COUNTS,
        AS_OF_DATE,
        ensure_output_directories,
    )
except ImportError:
    from config import (
        PROJECT_ROOT,
        GENERATED_DATA_DIR,
        RANDOM_SEED,
        TRANSACTION_START_DATE,
        TRANSACTION_END_DATE,
        RECORD_COUNTS,
        AS_OF_DATE,
        ensure_output_directories,
    )


# Initialize Random Generator
random.seed(RANDOM_SEED)

# Agreement Reference Data
AGREEMENT_STATUSES = [
    "ACTIVE",
    "EXPIRED",
    "TERMINATED",
    "SUSPENDED",
]

AGREEMENT_STATUS_WEIGHTS = [0.65, 0.15, 0.10, 0.10]

# KYC Reference Data
KYC_STATUSES = [
    "PENDING",
    "VERIFIED",
    "REJECTED",
    "EXPIRED",
]

# Partner Types
PARTNER_TYPES = [
    "DSA",
    "AUTO_DEALER",
    "TRACTOR_DEALER",
    "CONNECTOR",
]

# Loan Products
LOAN_PRODUCT_IDS = [
    "PROD001",
    "PROD002",
    "PROD003",
    "PROD004",
    "PROD005",
]

# CASA Product
CASA_PRODUCT_ID = "PROD006"

# Supported Commission Modes
COMMISSION_MODES = [
    "LOAN_RATE",
    "AMB_RATE",
    "FIXED_PER_ACCOUNT",
    "AMB_TIERED",
]

# Synthetic As-Of Date
RATE_CARD_AS_OF_DATE = AS_OF_DATE


# --------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------

def random_date(start_date, end_date):
    """Generate a random date within a range."""

    total_days = (end_date - start_date).days

    return start_date + timedelta(
        days=random.randint(0, total_days)
    )


# --------------------------------------------------
# GENERATE PARTNER AGREEMENTS
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
# GENERATE PARTNER KYC HISTORY
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


# --------------------------------------------------
# GENERATE LOAN RATE CARDS
# --------------------------------------------------
def generate_loan_rate_cards(partner_df, start_counter=1):

    records = []

    partner_types = PARTNER_TYPES
    product_ids = LOAN_PRODUCT_IDS

    # Generate 20 partner-type rate cards:
    # 4 partner types x 5 loan products.
    for partner_type in partner_types:

        for product_id in product_ids:

            effective_from = random_date(
                TRANSACTION_START_DATE,
                TRANSACTION_END_DATE
            )

            effective_to = None

            # Some rules have historical end dates.
            if random.random() < 0.30:

                remaining_days = (
                    TRANSACTION_END_DATE - effective_from
                ).days

                if remaining_days >= 30:
                    period_days = random.randint(
                        30,
                        min(365, remaining_days)
                    )

                    effective_to = (
                        effective_from
                        + timedelta(days=period_days)
                    )

            rule_status = (
                "INACTIVE"
                if effective_to is not None
                else random.choice(["ACTIVE", "INACTIVE"])
            )

            created_at = (
                pd.Timestamp(effective_from)
                + pd.Timedelta(hours=10)
            )

            updated_at = (
                pd.Timestamp(effective_to)
                if effective_to is not None
                else created_at + pd.Timedelta(days=30)
            )

            records.append({
                "rate_card_id": f"RATE{start_counter:04d}",
                "partner_id": None,
                "partner_type": partner_type,
                "product_id": product_id,
                "commission_mode": "LOAN_RATE",
                "commission_rate": round(
                    random.uniform(0.005, 0.015), 6
                ),
                "fixed_amount": None,
                "effective_from": effective_from.isoformat(),
                "effective_to": (
                    effective_to.isoformat()
                    if effective_to else None
                ),
                "rule_status": rule_status,
                "rule_version": 1,
                "tier_group_id": None,
                "tier_lower_bound": None,
                "tier_upper_bound": None,
                "created_at": created_at.isoformat(),
                "updated_at": updated_at.isoformat(),
            })

            start_counter += 1

    # Generate partner-specific loan rate cards.
    # Each partner-product combination is unique.
    # The configured total includes 40 CASA rate cards.
    loan_partner_type_count = len(partner_types) * len(product_ids)
    casa_rate_card_count = 40

    partner_specific_count = (
        RECORD_COUNTS["src_rate_cards"]
        - loan_partner_type_count
        - casa_rate_card_count
    )

    partner_product_combinations = [
        (partner_id, product_id)
        for partner_id in partner_df["partner_id"].tolist()
        for product_id in product_ids
    ]

    selected_combinations = random.sample(
        partner_product_combinations,
        partner_specific_count
    )

    for partner_id, product_id in selected_combinations:

        effective_from = random_date(
            TRANSACTION_START_DATE,
            TRANSACTION_END_DATE
        )

        effective_to = None

        if random.random() < 0.30:

            remaining_days = (
                TRANSACTION_END_DATE - effective_from
            ).days

            if remaining_days >= 30:
                period_days = random.randint(
                    30,
                    min(365, remaining_days)
                )

                effective_to = (
                    effective_from
                    + timedelta(days=period_days)
                )

        rule_status = (
            "INACTIVE"
            if effective_to is not None
            else random.choice(["ACTIVE", "INACTIVE"])
        )

        created_at = (
            pd.Timestamp(effective_from)
            + pd.Timedelta(hours=10)
        )

        updated_at = (
            pd.Timestamp(effective_to)
            if effective_to is not None
            else created_at + pd.Timedelta(days=30)
        )

        records.append({
            "rate_card_id": f"RATE{start_counter:04d}",
            "partner_id": partner_id,
            "partner_type": None,
            "product_id": product_id,
            "commission_mode": "LOAN_RATE",
            "commission_rate": round(
                random.uniform(0.007, 0.018), 6
            ),
            "fixed_amount": None,
            "effective_from": effective_from.isoformat(),
            "effective_to": (
                effective_to.isoformat()
                if effective_to else None
            ),
            "rule_status": rule_status,
            "rule_version": 1,
            "tier_group_id": None,
            "tier_lower_bound": None,
            "tier_upper_bound": None,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
        })

        start_counter += 1

    return records


# --------------------------------------------------
# GENERATE CASA RATE CARDS
# --------------------------------------------------
def generate_casa_rate_cards(partner_df, start_counter=51):

    records = []
    tier_counter = 1

    # Synthetic AMB tiers: lower-inclusive, upper-exclusive.
    amb_tiers = [
        (0, 10000, 0.0005),
        (10000, 50000, 0.0010),
        (50000, None, 0.0015),
    ]

    # Select four distinct partners for partner-specific rules.
    selected_partners = random.sample(
        partner_df["partner_id"].tolist(),
        4
    )

    def generate_effective_dates():

        effective_from = random_date(
            TRANSACTION_START_DATE,
            TRANSACTION_END_DATE
        )

        effective_to = None

        if random.random() < 0.30:

            remaining_days = (
                TRANSACTION_END_DATE - effective_from
            ).days

            if remaining_days >= 30:
                period_days = random.randint(
                    30,
                    min(365, remaining_days)
                )

                effective_to = (
                    effective_from
                    + timedelta(days=period_days)
                )

        rule_status = (
            "INACTIVE"
            if effective_to is not None
            else random.choice(["ACTIVE", "INACTIVE"])
        )

        created_at = (
            pd.Timestamp(effective_from)
            + pd.Timedelta(hours=10)
        )

        updated_at = (
            pd.Timestamp(effective_to)
            if effective_to is not None
            else created_at + pd.Timedelta(days=30)
        )

        return (
            effective_from,
            effective_to,
            rule_status,
            created_at,
            updated_at,
        )

    def append_rate_card(
        partner_id,
        partner_type,
        commission_mode,
        commission_rate,
        fixed_amount,
        effective_from,
        effective_to,
        rule_status,
        created_at,
        updated_at,
        tier_group_id=None,
        tier_lower_bound=None,
        tier_upper_bound=None,
    ):

        nonlocal start_counter

        records.append({
            "rate_card_id": f"RATE{start_counter:04d}",
            "partner_id": partner_id,
            "partner_type": partner_type,
            "product_id": CASA_PRODUCT_ID,
            "commission_mode": commission_mode,
            "commission_rate": commission_rate,
            "fixed_amount": fixed_amount,
            "effective_from": effective_from.isoformat(),
            "effective_to": (
                effective_to.isoformat()
                if effective_to else None
            ),
            "rule_status": rule_status,
            "rule_version": 1,
            "tier_group_id": tier_group_id,
            "tier_lower_bound": tier_lower_bound,
            "tier_upper_bound": tier_upper_bound,
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
        })

        start_counter += 1

    def generate_rules(partner_id, partner_type):

        nonlocal tier_counter

        (
            effective_from,
            effective_to,
            rule_status,
            created_at,
            updated_at,
        ) = generate_effective_dates()

        # 1. AMB_RATE
        append_rate_card(
            partner_id=partner_id,
            partner_type=partner_type,
            commission_mode="AMB_RATE",
            commission_rate=round(
                random.uniform(0.0005, 0.0025), 6
            ),
            fixed_amount=None,
            effective_from=effective_from,
            effective_to=effective_to,
            rule_status=rule_status,
            created_at=created_at,
            updated_at=updated_at,
        )

        # 2. FIXED_PER_ACCOUNT
        append_rate_card(
            partner_id=partner_id,
            partner_type=partner_type,
            commission_mode="FIXED_PER_ACCOUNT",
            commission_rate=None,
            fixed_amount=random.choice([100, 200, 300, 400, 500]),
            effective_from=effective_from,
            effective_to=effective_to,
            rule_status=rule_status,
            created_at=created_at,
            updated_at=updated_at,
        )

        # 3. AMB_TIERED
        tier_group_id = f"CASA_TIER{tier_counter:04d}"
        tier_counter += 1

        for lower_bound, upper_bound, commission_rate in amb_tiers:

            append_rate_card(
                partner_id=partner_id,
                partner_type=partner_type,
                commission_mode="AMB_TIERED",
                commission_rate=commission_rate,
                fixed_amount=None,
                effective_from=effective_from,
                effective_to=effective_to,
                rule_status=rule_status,
                created_at=created_at,
                updated_at=updated_at,
                tier_group_id=tier_group_id,
                tier_lower_bound=lower_bound,
                tier_upper_bound=upper_bound,
            )

    # Generate partner-type CASA rules.
    for partner_type in PARTNER_TYPES:
        generate_rules(
            partner_id=None,
            partner_type=partner_type
        )

    # Generate partner-specific CASA rules.
    for partner_id in selected_partners:
        generate_rules(
            partner_id=partner_id,
            partner_type=None
        )

    return records


# --------------------------------------------------
# EXPORT DATASET
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
# MAIN EXECUTION
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

    # Generate loan rate cards.
    loan_rate_cards = generate_loan_rate_cards(
        partner_df
    )

    # Generate CASA rate cards.
    casa_rate_cards = generate_casa_rate_cards(
        partner_df,
        start_counter=61,
    )

    # Combine loan and CASA rate cards.
    rate_card_df = pd.DataFrame(
        loan_rate_cards + casa_rate_cards
    )

    # Validate configured record count.
    expected_count = RECORD_COUNTS["src_rate_cards"]

    if len(rate_card_df) != expected_count:
        raise ValueError(
            f"Expected {expected_count} rate cards, "
            f"but generated {len(rate_card_df)}."
        )

    if rate_card_df["rate_card_id"].nunique() != expected_count:
        raise ValueError(
            "Duplicate rate_card_id values found."
        )

    export_dataset(
        rate_card_df,
        "src_rate_cards",
    )

    print("\nBusiness rule data generation completed.")


if __name__ == "__main__":
    main()