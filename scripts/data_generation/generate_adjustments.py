import random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

import pandas as pd

try:
    from .config import (
        GENERATED_DATA_DIR,
        RANDOM_SEED,
        TRANSACTION_END_DATE,
        RECORD_COUNTS,
        DEFAULT_CURRENCY,
        MONEY_DECIMAL_PLACES,
        ensure_output_directories,
    )
except ImportError:
    from config import (
        GENERATED_DATA_DIR,
        RANDOM_SEED,
        TRANSACTION_END_DATE,
        RECORD_COUNTS,
        DEFAULT_CURRENCY,
        MONEY_DECIMAL_PLACES,
        ensure_output_directories,
    )


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

random.seed(RANDOM_SEED)

RECORD_COUNT = RECORD_COUNTS["src_adjustments"]
TIMEZONE = "Asia/Kolkata"

ADJUSTMENT_TYPES = [
    "CLAWBACK",
    "CANCELLATION_REVERSAL",
    "FORECLOSURE_REVERSAL",
    "MANUAL_ADJUSTMENT",
]

APPROVAL_STATUSES = [
    "APPROVED",
    "PENDING",
    "REJECTED",
]

SOURCE_SYSTEMS = [
    "LOAN_SERVICING",
    "CORE_BANKING",
    "PARTNER_COMMISSION_SYSTEM",
    "FINANCE_OPERATIONS",
]

APPROVERS = [
    "PORTFOLIO_APPROVER_01",
    "PORTFOLIO_APPROVER_02",
    "FINANCE_APPROVER_01",
    "FINANCE_APPROVER_02",
]

COLUMNS = [
    "adjustment_id",
    "original_source_event_type",
    "original_source_event_id",
    "partner_id",
    "product_id",
    "adjustment_type",
    "adjustment_amount",
    "adjustment_direction",
    "adjustment_reason",
    "adjustment_date",
    "effective_date",
    "approval_status",
    "approved_by",
    "source_system",
    "source_event_timestamp",
    "created_at",
    "updated_at",
]


# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

def random_timestamp(event_date, hour=None):
    """Generate an IST-aware timestamp on the supplied date."""

    if hour is None:
        hour = random.randint(9, 18)

    return (
        pd.Timestamp(event_date)
        .tz_localize(TIMEZONE)
        + pd.Timedelta(
            hours=hour,
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )
    )


def random_amount(minimum, maximum):
    """Generate a positive two-decimal adjustment amount."""

    amount = Decimal(
        str(round(random.uniform(minimum, maximum), 2))
    )

    return amount.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )


def load_source_data():
    """Load all source datasets required for adjustment references."""

    partner_df = pd.read_csv(
        GENERATED_DATA_DIR / "src_partner_master.csv"
    )

    product_df = pd.read_csv(
        GENERATED_DATA_DIR / "src_product_master.csv"
    )

    disbursement_df = pd.read_csv(
        GENERATED_DATA_DIR / "src_disbursements.csv"
    )

    casa_df = pd.read_csv(
        GENERATED_DATA_DIR / "src_casa_acquisitions.csv"
    )

    return (
        partner_df,
        product_df,
        disbursement_df,
        casa_df,
    )


# --------------------------------------------------
# 3. BUILD ADJUSTMENT REFERENCE EVENTS
# --------------------------------------------------

def build_reference_events(disbursement_df, casa_df):

    # Only successful disbursements are selected because
    # adjustments relate to previously calculated commissions.
    successful_disbursements = disbursement_df[
        disbursement_df["disbursement_status"] == "SUCCESSFUL"
    ].copy()

    # Only eligible CASA measurements are selected.
    eligible_casa = casa_df[
        casa_df["eligibility_status"] == "ELIGIBLE"
    ].copy()

    if len(successful_disbursements) < 120:
        raise ValueError(
            "Insufficient successful disbursement events."
        )

    if len(eligible_casa) < 30:
        raise ValueError(
            "Insufficient eligible CASA acquisition events."
        )

    loan_events = successful_disbursements.sample(
        n=120,
        random_state=RANDOM_SEED,
    )

    casa_events = eligible_casa.sample(
        n=30,
        random_state=RANDOM_SEED,
    )

    references = []

    for _, row in loan_events.iterrows():

        references.append({
            "original_source_event_type": "DISBURSEMENT",
            "original_source_event_id": row[
                "disbursement_event_id"
            ],
            "partner_id": row["partner_id"],
            "product_id": row["product_id"],
            "source_event_date": pd.to_datetime(
                row["disbursement_date"]
            ).date(),
        })

    for _, row in casa_events.iterrows():

        references.append({
            "original_source_event_type": "CASA_ACQUISITION",
            "original_source_event_id": row[
                "acquisition_event_id"
            ],
            "partner_id": row["partner_id"],
            "product_id": row["product_id"],
            "source_event_date": pd.to_datetime(
                row["source_event_timestamp"]
            ).date(),
        })

    random.shuffle(references)

    return references


# --------------------------------------------------
# 4. ADJUSTMENT TYPE AND DIRECTION ASSIGNMENT
# --------------------------------------------------

def build_adjustment_types():

    # 120 disbursement adjustments:
    # 35 clawbacks, 35 cancellation reversals,
    # 35 foreclosure reversals and 15 manual adjustments.
    loan_types = (
        ["CLAWBACK"] * 35
        + ["CANCELLATION_REVERSAL"] * 35
        + ["FORECLOSURE_REVERSAL"] * 35
        + ["MANUAL_ADJUSTMENT"] * 15
    )

    # 30 CASA adjustments:
    # 10 clawbacks and 20 manual adjustments.
    casa_types = (
        ["CLAWBACK"] * 10
        + ["MANUAL_ADJUSTMENT"] * 20
    )

    random.shuffle(loan_types)
    random.shuffle(casa_types)

    return loan_types, casa_types


def determine_direction(adjustment_type):

    if adjustment_type in [
        "CLAWBACK",
        "CANCELLATION_REVERSAL",
        "FORECLOSURE_REVERSAL",
    ]:
        return "DEBIT"

    return random.choice(["DEBIT", "CREDIT"])


def determine_reason(adjustment_type):

    reasons = {
        "CLAWBACK": [
            "Partial commission recovery",
            "Contractual commission clawback",
            "Recovery of previously paid commission",
            "Adjustment following source event review",
        ],
        "CANCELLATION_REVERSAL": [
            "Loan cancellation reversal",
            "Commission reversal following loan cancellation",
            "Cancellation-related payout correction",
        ],
        "FORECLOSURE_REVERSAL": [
            "Early loan foreclosure",
            "Foreclosure-related commission recovery",
            "Commission reversal following early closure",
        ],
        "MANUAL_ADJUSTMENT": [
            "Approved commission correction",
            "Manual payout reconciliation",
            "Correction of previously processed amount",
            "Finance-approved payout adjustment",
        ],
    }

    return random.choice(reasons[adjustment_type])


# --------------------------------------------------
# 5. GENERATE ADJUSTMENTS
# --------------------------------------------------

def generate_adjustments(references):

    records = []

    loan_types, casa_types = build_adjustment_types()

    approval_statuses = (
        ["APPROVED"] * 90
        + ["PENDING"] * 35
        + ["REJECTED"] * 25
    )

    random.shuffle(approval_statuses)

    loan_counter = 0
    casa_counter = 0

    for index, reference in enumerate(references, start=1):

        event_type = reference["original_source_event_type"]

        if event_type == "DISBURSEMENT":
            adjustment_type = loan_types[loan_counter]
            loan_counter += 1

            minimum_amount = 100.00
            maximum_amount = 50000.00

        else:
            adjustment_type = casa_types[casa_counter]
            casa_counter += 1

            minimum_amount = 100.00
            maximum_amount = 10000.00

        adjustment_direction = determine_direction(
            adjustment_type
        )

        approval_status = approval_statuses[index - 1]

        approved_by = (
            random.choice(APPROVERS)
            if approval_status == "APPROVED"
            else None
        )

        source_event_date = reference["source_event_date"]

        maximum_delay = (
            TRANSACTION_END_DATE - source_event_date
        ).days

        if maximum_delay < 0:
            raise ValueError(
                "Source event date exceeds transaction end date."
            )

        adjustment_date = (
            source_event_date
            + timedelta(
                days=random.randint(0, maximum_delay)
            )
        )

        remaining_days = (
            TRANSACTION_END_DATE - adjustment_date
        ).days

        effective_date = (
            adjustment_date
            + timedelta(
                days=random.randint(
                    0,
                    min(14, remaining_days),
                )
            )
        )

        source_event_timestamp = random_timestamp(
            adjustment_date
        )

        created_at = (
            source_event_timestamp
            + pd.Timedelta(minutes=random.randint(1, 30))
        )

        updated_at = (
            created_at
            + pd.Timedelta(hours=random.randint(1, 3))
        )

        source_system = (
            "LOAN_SERVICING"
            if event_type == "DISBURSEMENT"
            else "CORE_BANKING"
        )

        records.append({
            "adjustment_id": f"ADJ{index:04d}",
            "original_source_event_type": event_type,
            "original_source_event_id": (
                reference["original_source_event_id"]
            ),
            "partner_id": reference["partner_id"],
            "product_id": reference["product_id"],
            "adjustment_type": adjustment_type,
            "adjustment_amount": random_amount(
                minimum_amount,
                maximum_amount,
            ),
            "adjustment_direction": adjustment_direction,
            "adjustment_reason": determine_reason(
                adjustment_type
            ),
            "adjustment_date": adjustment_date.isoformat(),
            "effective_date": effective_date.isoformat(),
            "approval_status": approval_status,
            "approved_by": approved_by,
            "source_system": source_system,
            "source_event_timestamp": (
                source_event_timestamp.isoformat()
            ),
            "created_at": created_at.isoformat(),
            "updated_at": updated_at.isoformat(),
        })

    return pd.DataFrame(records, columns=COLUMNS)


# --------------------------------------------------
# 6. VALIDATE ADJUSTMENTS
# --------------------------------------------------

def validate_adjustments(
    adjustment_df,
    partner_df,
    product_df,
    disbursement_df,
    casa_df,
):

    assert len(adjustment_df) == RECORD_COUNT
    assert list(adjustment_df.columns) == COLUMNS

    # Primary key validation.
    assert adjustment_df["adjustment_id"].notna().all()
    assert adjustment_df["adjustment_id"].is_unique

    # Required field validation.
    required_columns = [
        column
        for column in COLUMNS
        if column != "approved_by"
    ]

    assert adjustment_df[required_columns].notna().all().all()

    # Partner and product foreign keys.
    valid_partner_ids = set(partner_df["partner_id"])
    valid_product_ids = set(product_df["product_id"])

    assert set(adjustment_df["partner_id"]).issubset(
        valid_partner_ids
    )

    assert set(adjustment_df["product_id"]).issubset(
        valid_product_ids
    )

    # Source event reference validation.
    valid_disbursement_ids = set(
        disbursement_df["disbursement_event_id"]
    )

    valid_casa_ids = set(
        casa_df["acquisition_event_id"]
    )

    loan_adjustments = adjustment_df[
        adjustment_df["original_source_event_type"]
        == "DISBURSEMENT"
    ]

    casa_adjustments = adjustment_df[
        adjustment_df["original_source_event_type"]
        == "CASA_ACQUISITION"
    ]

    assert set(
        loan_adjustments["original_source_event_id"]
    ).issubset(valid_disbursement_ids)

    assert set(
        casa_adjustments["original_source_event_id"]
    ).issubset(valid_casa_ids)

    # Verify that source references belong to the same partner
    # and product as the adjustment.
    disbursement_lookup = disbursement_df.set_index(
        "disbursement_event_id"
    )

    casa_lookup = casa_df.set_index("acquisition_event_id")

    for _, row in adjustment_df.iterrows():

        if row["original_source_event_type"] == "DISBURSEMENT":
            source = disbursement_lookup.loc[
                row["original_source_event_id"]
            ]
        else:
            source = casa_lookup.loc[
                row["original_source_event_id"]
            ]

        assert row["partner_id"] == source["partner_id"]
        assert row["product_id"] == source["product_id"]

    # Allowed values.
    assert set(
        adjustment_df["original_source_event_type"]
    ).issubset({
        "DISBURSEMENT",
        "CASA_ACQUISITION",
    })

    assert set(adjustment_df["adjustment_type"]).issubset(
        ADJUSTMENT_TYPES
    )

    assert set(
        adjustment_df["adjustment_direction"]
    ).issubset({"DEBIT", "CREDIT"})

    assert set(
        adjustment_df["approval_status"]
    ).issubset(APPROVAL_STATUSES)

    # Positive adjustment amount.
    assert (
        pd.to_numeric(adjustment_df["adjustment_amount"]) > 0
    ).all()

    # Reversal and clawback types must be DEBIT.
    debit_only_types = [
        "CLAWBACK",
        "CANCELLATION_REVERSAL",
        "FORECLOSURE_REVERSAL",
    ]

    debit_only_records = adjustment_df[
        adjustment_df["adjustment_type"].isin(debit_only_types)
    ]

    assert (
        debit_only_records["adjustment_direction"] == "DEBIT"
    ).all()

    # Manual adjustments may be DEBIT or CREDIT.
    manual_records = adjustment_df[
        adjustment_df["adjustment_type"] == "MANUAL_ADJUSTMENT"
    ]

    assert set(
        manual_records["adjustment_direction"]
    ).issubset({"DEBIT", "CREDIT"})

    # Approval reference validation.
    approved_records = adjustment_df[
        adjustment_df["approval_status"] == "APPROVED"
    ]

    non_approved_records = adjustment_df[
        adjustment_df["approval_status"] != "APPROVED"
    ]

    assert approved_records["approved_by"].notna().all()
    assert non_approved_records["approved_by"].isna().all()

    # Date validation.
    adjustment_dates = pd.to_datetime(
        adjustment_df["adjustment_date"]
    ).dt.date

    effective_dates = pd.to_datetime(
        adjustment_df["effective_date"]
    ).dt.date

    assert (adjustment_dates <= effective_dates).all()
    assert (effective_dates <= TRANSACTION_END_DATE).all()

    # Timestamp validation.
    for column in [
        "source_event_timestamp",
        "created_at",
        "updated_at",
    ]:
        timestamps = pd.to_datetime(
            adjustment_df[column],
            utc=True,
        )

        assert timestamps.notna().all()

    created_timestamps = pd.to_datetime(
        adjustment_df["created_at"],
        utc=True,
    )

    updated_timestamps = pd.to_datetime(
        adjustment_df["updated_at"],
        utc=True,
    )

    assert (updated_timestamps >= created_timestamps).all()

    # Distribution validation.
    assert len(loan_adjustments) == 120
    assert len(casa_adjustments) == 30

    assert adjustment_df["adjustment_type"].value_counts().to_dict() == {
        "CLAWBACK": 45,
        "CANCELLATION_REVERSAL": 35,
        "FORECLOSURE_REVERSAL": 35,
        "MANUAL_ADJUSTMENT": 35,
    }

    assert adjustment_df["approval_status"].value_counts().to_dict() == {
        "APPROVED": 90,
        "PENDING": 35,
        "REJECTED": 25,
    }

    print("Adjustment validation passed.")
    print(f"Total records: {len(adjustment_df)}")
    print(f"Disbursement references: {len(loan_adjustments)}")
    print(f"CASA references: {len(casa_adjustments)}")

    print("\nAdjustment types:")
    print(adjustment_df["adjustment_type"].value_counts().sort_index())

    print("\nAdjustment directions:")
    print(adjustment_df["adjustment_direction"].value_counts().sort_index())

    print("\nApproval statuses:")
    print(adjustment_df["approval_status"].value_counts().sort_index())


# --------------------------------------------------
# 7. MAIN EXECUTION
# --------------------------------------------------

def main():

    ensure_output_directories()

    (
        partner_df,
        product_df,
        disbursement_df,
        casa_df,
    ) = load_source_data()

    references = build_reference_events(
        disbursement_df,
        casa_df,
    )

    adjustment_df = generate_adjustments(references)

    validate_adjustments(
        adjustment_df,
        partner_df,
        product_df,
        disbursement_df,
        casa_df,
    )

    output_path = (
        GENERATED_DATA_DIR / "src_adjustments.csv"
    )

    adjustment_df.to_csv(
        output_path,
        index=False,
    )

    print(
        f"\nsrc_adjustments: {len(adjustment_df)} records exported"
    )
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()