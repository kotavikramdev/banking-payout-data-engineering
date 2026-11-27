import random
from datetime import date, datetime, time, timedelta, timezone

import pandas as pd

try:
    from .config import (
        GENERATED_DATA_DIR,
        RANDOM_SEED,
        TRANSACTION_START_DATE,
        TRANSACTION_END_DATE,
        DEFAULT_CURRENCY,
        RECORD_COUNTS,
        ensure_output_directories,
    )
except ImportError:
    from config import (
        GENERATED_DATA_DIR,
        RANDOM_SEED,
        TRANSACTION_START_DATE,
        TRANSACTION_END_DATE,
        DEFAULT_CURRENCY,
        RECORD_COUNTS,
        ensure_output_directories,
    )


# --------------------------------------------------
# GENERATION SETTINGS
# --------------------------------------------------

IST = timezone(timedelta(hours=5, minutes=30))

STATUS_VALUES = [
    "SUCCESSFUL",
    "FAILED",
    "CANCELLED",
]

STATUS_WEIGHTS = [90, 5, 5]

SOURCE_SYSTEMS = [
    "LOS",
    "CORE_BANKING",
    "LOAN_ORIGINATION",
    "DIGITAL_LENDING",
]

# Synthetic design: 1,500 loans and 2,000 events.
TOTAL_LOANS = 1500
LOANS_WITH_TWO_EVENTS = 500


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def random_date(rng, start_date, end_date):
    """Return a random date within the inclusive range."""

    total_days = (end_date - start_date).days

    return start_date + timedelta(
        days=rng.randint(0, total_days)
    )


def random_timestamp(rng, event_date):
    """Create a timestamp on the supplied date in IST."""

    event_time = time(
        hour=rng.randint(8, 19),
        minute=rng.randint(0, 59),
        second=rng.randint(0, 59),
    )

    return datetime.combine(
        event_date,
        event_time,
        tzinfo=IST,
    )


# --------------------------------------------------
# GENERATE DISBURSEMENTS
# --------------------------------------------------

def generate_disbursements(partner_df, product_df):

    rng = random.Random(RANDOM_SEED)

    partner_ids = (
        partner_df["partner_id"]
        .dropna()
        .astype(str)
        .tolist()
    )

    loan_products = (
        product_df.loc[
            product_df["product_category"] == "LOAN",
            "product_id",
        ]
        .dropna()
        .astype(str)
        .tolist()
    )

    if not partner_ids:
        raise ValueError("No valid partner IDs found.")

    if len(loan_products) != 5:
        raise ValueError(
            f"Expected 5 LOAN products, found {len(loan_products)}."
        )

    if TOTAL_LOANS > RECORD_COUNTS["src_disbursements"]:
        raise ValueError(
            "Total loan count cannot exceed event record count."
        )

    if not (
        0 <= LOANS_WITH_TWO_EVENTS <= TOTAL_LOANS
    ):
        raise ValueError("Invalid two-event loan count.")

    # Select loans that will have two partial disbursement events.
    two_event_loan_numbers = set(
        rng.sample(
            range(1, TOTAL_LOANS + 1),
            LOANS_WITH_TWO_EVENTS,
        )
    )

    records = []
    event_counter = 1

    for loan_number in range(1, TOTAL_LOANS + 1):

        loan_id = f"LOAN{loan_number:06d}"
        customer_ref = f"CUST{loan_number:06d}"

        # Keep the same partner and product for all events
        # belonging to the same loan.
        partner_id = rng.choice(partner_ids)
        product_id = rng.choice(loan_products)

        event_count = (
            2
            if loan_number in two_event_loan_numbers
            else 1
        )

        # Reserve enough date range for the second event.
        if event_count == 2:
            first_event_date = random_date(
                rng,
                TRANSACTION_START_DATE,
                TRANSACTION_END_DATE - timedelta(days=1),
            )

            remaining_days = (
                TRANSACTION_END_DATE - first_event_date
            ).days

            second_event_date = (
                first_event_date
                + timedelta(
                    days=rng.randint(1, remaining_days)
                )
            )

            event_dates = [
                first_event_date,
                second_event_date,
            ]

        else:
            event_dates = [
                random_date(
                    rng,
                    TRANSACTION_START_DATE,
                    TRANSACTION_END_DATE,
                )
            ]

        for sequence_number, disbursement_date in enumerate(
            event_dates,
            start=1,
        ):

            source_event_timestamp = random_timestamp(
                rng,
                disbursement_date,
            )

            created_at = (
                source_event_timestamp
                + timedelta(minutes=rng.randint(1, 180))
            )

            # Some source records receive a later update.
            updated_at = None

            if rng.random() < 0.20:
                updated_at = (
                    created_at
                    + timedelta(
                        hours=rng.randint(1, 72)
                    )
                )

            disbursement_status = rng.choices(
                STATUS_VALUES,
                weights=STATUS_WEIGHTS,
                k=1,
            )[0]

            # Positive amount for every event, as required
            # by the source data dictionary.
            disbursed_amount = round(
                rng.uniform(25000, 5000000),
                2,
            )

            records.append({
                "disbursement_event_id": (
                    f"DISB{event_counter:06d}"
                ),
                "loan_id": loan_id,
                "disbursement_sequence": sequence_number,
                "partner_id": partner_id,
                "product_id": product_id,
                "customer_ref": customer_ref,
                "disbursement_date": (
                    disbursement_date.isoformat()
                ),
                "disbursed_amount": disbursed_amount,
                "currency_code": DEFAULT_CURRENCY,
                "disbursement_status": disbursement_status,
                "source_system": rng.choice(SOURCE_SYSTEMS),
                "source_event_timestamp": (
                    source_event_timestamp.isoformat()
                ),
                "created_at": created_at.isoformat(),
                "updated_at": (
                    updated_at.isoformat()
                    if updated_at
                    else None
                ),
            })

            event_counter += 1

    return pd.DataFrame(records)


# --------------------------------------------------
# VALIDATE DISBURSEMENTS
# --------------------------------------------------

def validate_disbursements(
    disbursement_df,
    partner_df,
    product_df,
):

    expected_count = RECORD_COUNTS["src_disbursements"]

    expected_columns = [
        "disbursement_event_id",
        "loan_id",
        "disbursement_sequence",
        "partner_id",
        "product_id",
        "customer_ref",
        "disbursement_date",
        "disbursed_amount",
        "currency_code",
        "disbursement_status",
        "source_system",
        "source_event_timestamp",
        "created_at",
        "updated_at",
    ]

    if list(disbursement_df.columns) != expected_columns:
        raise ValueError("Column names or column order mismatch.")

    if len(disbursement_df) != expected_count:
        raise ValueError(
            f"Expected {expected_count} records, "
            f"found {len(disbursement_df)}."
        )

    # Mandatory fields.
    mandatory_columns = [
        column
        for column in expected_columns
        if column != "updated_at"
    ]

    if disbursement_df[mandatory_columns].isnull().any().any():
        raise ValueError("Null values found in mandatory columns.")

    # Primary key.
    if disbursement_df["disbursement_event_id"].duplicated().any():
        raise ValueError("Duplicate disbursement event IDs found.")

    # Foreign keys.
    valid_partner_ids = set(
        partner_df["partner_id"].dropna().astype(str)
    )

    valid_loan_products = set(
        product_df.loc[
            product_df["product_category"] == "LOAN",
            "product_id",
        ].dropna().astype(str)
    )

    if not set(disbursement_df["partner_id"]).issubset(
        valid_partner_ids
    ):
        raise ValueError("Invalid partner references found.")

    if not set(disbursement_df["product_id"]).issubset(
        valid_loan_products
    ):
        raise ValueError("Invalid or non-LOAN product references found.")

    # Loan and sequence uniqueness.
    if (disbursement_df["loan_id"].str.strip() == "").any():
        raise ValueError("Blank loan IDs found.")

    if (disbursement_df["customer_ref"].str.strip() == "").any():
        raise ValueError("Blank customer references found.")

    if (
        disbursement_df["disbursement_sequence"] <= 0
    ).any():
        raise ValueError("Non-positive sequence numbers found.")

    if (
        disbursement_df.duplicated(
            subset=["loan_id", "disbursement_sequence"]
        ).any()
    ):
        raise ValueError(
            "Duplicate loan_id + disbursement_sequence combinations."
        )

    # Positive monetary amounts.
    if (disbursement_df["disbursed_amount"] <= 0).any():
        raise ValueError("Non-positive disbursement amounts found.")

    # Currency and status.
    if not disbursement_df["currency_code"].eq(
        DEFAULT_CURRENCY
    ).all():
        raise ValueError("Unexpected currency code found.")

    if not disbursement_df["disbursement_status"].isin(
        STATUS_VALUES
    ).all():
        raise ValueError("Invalid disbursement status found.")

    # Transaction date range.
    disbursement_dates = pd.to_datetime(
        disbursement_df["disbursement_date"],
        errors="raise",
    ).dt.date

    if not disbursement_dates.between(
        TRANSACTION_START_DATE,
        TRANSACTION_END_DATE,
    ).all():
        raise ValueError("Disbursement date outside configured range.")

    # Timestamp validation.
    timestamp_columns = [
        "source_event_timestamp",
        "created_at",
    ]

    for column in timestamp_columns:
        if not disbursement_df[column].str.endswith(
            "+05:30"
        ).all():
            raise ValueError(
                f"{column} must contain the +05:30 timezone."
            )

    source_timestamps = pd.to_datetime(
        disbursement_df["source_event_timestamp"],
        utc=True,
        errors="raise",
    )

    created_timestamps = pd.to_datetime(
        disbursement_df["created_at"],
        utc=True,
        errors="raise",
    )

    if (created_timestamps < source_timestamps).any():
        raise ValueError(
            "Created timestamp precedes source event timestamp."
        )

    if not disbursement_df["updated_at"].dropna().str.endswith(
        "+05:30"
    ).all():
        raise ValueError(
            "Updated timestamps must contain the +05:30 timezone."
        )

    updated_timestamps = pd.to_datetime(
        disbursement_df["updated_at"],
        utc=True,
        errors="raise",
    )

    updated_mask = disbursement_df["updated_at"].notna()

    if (
        updated_timestamps[updated_mask]
        < created_timestamps[updated_mask]
    ).any():
        raise ValueError(
            "Updated timestamp precedes created timestamp."
        )

    # Source event timestamp must fall on the disbursement date.
    source_event_dates = (
        source_timestamps
        .dt.tz_convert("Asia/Kolkata")
        .dt.date
    )

    if not source_event_dates.equals(disbursement_dates):
        raise ValueError(
            "Source event timestamp date does not match disbursement date."
        )

    # Each loan must have one consistent partner, product and customer.
    consistency_columns = [
        "partner_id",
        "product_id",
        "customer_ref",
    ]

    for column in consistency_columns:
        if (
            disbursement_df.groupby("loan_id")[column]
            .nunique()
            .gt(1)
            .any()
        ):
            raise ValueError(
                f"Inconsistent {column} values within a loan."
            )

    # Validate sequence continuity and chronological ordering.
    for loan_id, loan_group in disbursement_df.groupby("loan_id"):

        loan_group = loan_group.sort_values(
            "disbursement_sequence"
        )

        expected_sequences = list(
            range(1, len(loan_group) + 1)
        )

        actual_sequences = (
            loan_group["disbursement_sequence"].tolist()
        )

        if actual_sequences != expected_sequences:
            raise ValueError(
                f"Invalid sequence progression for {loan_id}."
            )

        if len(loan_group) > 1:
            dates = pd.to_datetime(
                loan_group["disbursement_date"]
            ).tolist()

            if dates != sorted(dates) or len(set(dates)) != len(dates):
                raise ValueError(
                    f"Disbursement dates are not sequential for {loan_id}."
                )

    # Confirm the intended one-event / two-event loan distribution.
    loan_event_counts = (
        disbursement_df.groupby("loan_id").size()
    )

    if len(loan_event_counts) != TOTAL_LOANS:
        raise ValueError("Unexpected number of unique loans.")

    if (
        loan_event_counts.eq(1).sum()
        != TOTAL_LOANS - LOANS_WITH_TWO_EVENTS
    ):
        raise ValueError("Unexpected single-event loan count.")

    if (
        loan_event_counts.eq(2).sum()
        != LOANS_WITH_TWO_EVENTS
    ):
        raise ValueError("Unexpected two-event loan count.")

    if not loan_event_counts.isin([1, 2]).all():
        raise ValueError("Unexpected event count for a loan.")

    # Display validation summary.
    print("Disbursement validation passed.")
    print(f"Total records: {len(disbursement_df)}")
    print(f"Unique loans: {len(loan_event_counts)}")
    print(
        "Loans with one event:",
        int(loan_event_counts.eq(1).sum()),
    )
    print(
        "Loans with two events:",
        int(loan_event_counts.eq(2).sum()),
    )
    print(
        "Successful events:",
        int(disbursement_df["disbursement_status"].eq("SUCCESSFUL").sum()),
    )
    print(
        "Failed events:",
        int(disbursement_df["disbursement_status"].eq("FAILED").sum()),
    )
    print(
        "Cancelled events:",
        int(disbursement_df["disbursement_status"].eq("CANCELLED").sum()),
    )
    print(
        "Loan products:",
        sorted(disbursement_df["product_id"].unique().tolist()),
    )
    print(
        "Source systems:",
        sorted(disbursement_df["source_system"].unique().tolist()),
    )


# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------

def main():

    ensure_output_directories()

    partner_path = (
        GENERATED_DATA_DIR / "src_partner_master.csv"
    )

    product_path = (
        GENERATED_DATA_DIR / "src_product_master.csv"
    )

    if not partner_path.exists():
        raise FileNotFoundError(
            "Partner master CSV not found. "
            "Generate src_partner_master first."
        )

    if not product_path.exists():
        raise FileNotFoundError(
            "Product master CSV not found. "
            "Generate src_product_master first."
        )

    partner_df = pd.read_csv(partner_path)
    product_df = pd.read_csv(product_path)

    disbursement_df = generate_disbursements(
        partner_df,
        product_df,
    )

    validate_disbursements(
        disbursement_df,
        partner_df,
        product_df,
    )

    output_path = (
        GENERATED_DATA_DIR / "src_disbursements.csv"
    )

    disbursement_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    print(
        f"\nsrc_disbursements: "
        f"{len(disbursement_df)} records exported"
    )

    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()