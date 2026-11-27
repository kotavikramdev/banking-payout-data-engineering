import random
from calendar import monthrange
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

CASA_PRODUCT_ID = "PROD006"

ACCOUNT_TYPES = [
    "SAVINGS",
    "CURRENT",
]

ACCOUNT_STATUSES = [
    "ACTIVE",
    "CLOSED",
    "DORMANT",
]

ELIGIBILITY_STATUSES = [
    "ELIGIBLE",
    "INELIGIBLE",
    "PENDING",
]

SOURCE_SYSTEMS = [
    "CORE_BANKING",
    "CASA_ORIGINATION",
    "DIGITAL_BANKING",
    "BRANCH_BANKING",
]

# Synthetic design:
# 500 accounts x 2 monthly measurements = 1,000 records.
TOTAL_ACCOUNTS = 500
MEASUREMENTS_PER_ACCOUNT = 2


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def first_day_of_next_month(input_date):
    """Return the first day of the month after input_date."""

    if input_date.month == 12:
        return date(input_date.year + 1, 1, 1)

    return date(
        input_date.year,
        input_date.month + 1,
        1,
    )


def add_months(month_start, number_of_months):
    """Add calendar months to a first-of-month date."""

    month_index = (
        month_start.year * 12
        + month_start.month - 1
        + number_of_months
    )

    year = month_index // 12
    month = month_index % 12 + 1

    return date(year, month, 1)


def month_end(month_start):
    """Return the last day of the measurement month."""

    last_day = monthrange(
        month_start.year,
        month_start.month,
    )[1]

    return date(
        month_start.year,
        month_start.month,
        last_day,
    )


def random_date(rng, start_date, end_date):
    """Generate a date within an inclusive range."""

    total_days = (end_date - start_date).days

    return start_date + timedelta(
        days=rng.randint(0, total_days)
    )


def random_month_end_timestamp(rng, measurement_month):
    """Generate a source timestamp on the month's final day."""

    event_date = month_end(measurement_month)

    event_time = time(
        hour=rng.randint(20, 23),
        minute=rng.randint(0, 59),
        second=rng.randint(0, 59),
    )

    return datetime.combine(
        event_date,
        event_time,
        tzinfo=IST,
    )


# --------------------------------------------------
# GENERATE CASA ACQUISITIONS
# --------------------------------------------------

def generate_casa_acquisitions(partner_df, product_df):

    rng = random.Random(RANDOM_SEED)

    partner_ids = (
        partner_df["partner_id"]
        .dropna()
        .astype(str)
        .tolist()
    )

    casa_products = (
        product_df.loc[
            product_df["product_category"] == "CASA",
            "product_id",
        ]
        .dropna()
        .astype(str)
        .tolist()
    )

    if not partner_ids:
        raise ValueError("No valid partner IDs found.")

    if casa_products != [CASA_PRODUCT_ID]:
        raise ValueError(
            f"Expected CASA product {CASA_PRODUCT_ID}, "
            f"found {casa_products}."
        )

    expected_count = RECORD_COUNTS["src_casa_acquisitions"]

    if (
        TOTAL_ACCOUNTS * MEASUREMENTS_PER_ACCOUNT
        != expected_count
    ):
        raise ValueError(
            "Account and measurement design does not match "
            "the configured record count."
        )

    # Acquisition dates must leave room for two subsequent
    # monthly measurement cycles within the transaction range.
    latest_measurement_month = date(
        TRANSACTION_END_DATE.year,
        TRANSACTION_END_DATE.month,
        1,
    )

    latest_first_measurement = add_months(
        latest_measurement_month,
        -(MEASUREMENTS_PER_ACCOUNT - 1),
    )

    latest_acquisition_date = (
        latest_first_measurement - timedelta(days=1)
    )

    records = []
    event_counter = 1

    for account_number in range(1, TOTAL_ACCOUNTS + 1):

        account_id = f"CASA{account_number:06d}"

        partner_id = rng.choice(partner_ids)

        account_type = rng.choice(ACCOUNT_TYPES)

        acquisition_date = random_date(
            rng,
            TRANSACTION_START_DATE,
            latest_acquisition_date,
        )

        first_measurement_month = first_day_of_next_month(
            acquisition_date
        )

        # Account status progression:
        # An account may remain active, close, or become dormant
        # in its second measurement month.
        first_account_status = "ACTIVE"

        second_account_status = rng.choices(
            ["ACTIVE", "CLOSED", "DORMANT"],
            weights=[85, 10, 5],
            k=1,
        )[0]

        account_statuses = [
            first_account_status,
            second_account_status,
        ]

        for measurement_index in range(
            MEASUREMENTS_PER_ACCOUNT
        ):

            measurement_month = add_months(
                first_measurement_month,
                measurement_index,
            )

            # AMB is supplied by the synthetic source system.
            # No daily balance calculation is performed here.
            average_monthly_balance = round(
                rng.uniform(0, 500000),
                2,
            )

            eligibility_status = rng.choices(
                ELIGIBILITY_STATUSES,
                weights=[70, 20, 10],
                k=1,
            )[0]

            # AMB is nullable in the source schema.
            # Some pending records have not received an AMB value.
            if (
                eligibility_status == "PENDING"
                and rng.random() < 0.30
            ):
                average_monthly_balance = None

            source_event_timestamp = (
                random_month_end_timestamp(
                    rng,
                    measurement_month,
                )
            )

            created_at = (
                source_event_timestamp
                + timedelta(minutes=rng.randint(1, 120))
            )

            updated_at = None

            if rng.random() < 0.20:
                updated_at = (
                    created_at
                    + timedelta(hours=rng.randint(1, 72))
                )

            records.append({
                "acquisition_event_id": (
                    f"CASAEVT{event_counter:06d}"
                ),
                "account_id": account_id,
                "partner_id": partner_id,
                "product_id": CASA_PRODUCT_ID,
                "account_type": account_type,
                "acquisition_date": (
                    acquisition_date.isoformat()
                ),
                "measurement_month": (
                    measurement_month.isoformat()
                ),
                "average_monthly_balance": (
                    average_monthly_balance
                ),
                "currency_code": DEFAULT_CURRENCY,
                "account_status": (
                    account_statuses[measurement_index]
                ),
                "eligibility_status": eligibility_status,
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
# VALIDATE CASA ACQUISITIONS
# --------------------------------------------------

def validate_casa_acquisitions(
    casa_df,
    partner_df,
    product_df,
):

    expected_count = RECORD_COUNTS["src_casa_acquisitions"]

    expected_columns = [
        "acquisition_event_id",
        "account_id",
        "partner_id",
        "product_id",
        "account_type",
        "acquisition_date",
        "measurement_month",
        "average_monthly_balance",
        "currency_code",
        "account_status",
        "eligibility_status",
        "source_system",
        "source_event_timestamp",
        "created_at",
        "updated_at",
    ]

    if list(casa_df.columns) != expected_columns:
        raise ValueError(
            "Column names or column order mismatch."
        )

    if len(casa_df) != expected_count:
        raise ValueError(
            f"Expected {expected_count} records, "
            f"found {len(casa_df)}."
        )

    # Mandatory fields.
    mandatory_columns = [
        column
        for column in expected_columns
        if column not in [
            "average_monthly_balance",
            "updated_at",
        ]
    ]

    if casa_df[mandatory_columns].isnull().any().any():
        raise ValueError(
            "Null values found in mandatory columns."
        )

    # Primary key.
    if casa_df["acquisition_event_id"].duplicated().any():
        raise ValueError(
            "Duplicate acquisition event IDs found."
        )

    # Foreign keys.
    valid_partner_ids = set(
        partner_df["partner_id"].dropna().astype(str)
    )

    valid_casa_products = set(
        product_df.loc[
            product_df["product_category"] == "CASA",
            "product_id",
        ].dropna().astype(str)
    )

    if not set(casa_df["partner_id"]).issubset(
        valid_partner_ids
    ):
        raise ValueError(
            "Invalid partner references found."
        )

    if not set(casa_df["product_id"]).issubset(
        valid_casa_products
    ):
        raise ValueError(
            "Invalid or non-CASA product references found."
        )

    if not casa_df["product_id"].eq(
        CASA_PRODUCT_ID
    ).all():
        raise ValueError(
            "Unexpected product ID found."
        )

    # Account and event identifiers.
    if (casa_df["account_id"].str.strip() == "").any():
        raise ValueError("Blank account IDs found.")

    # One measurement per account and month.
    if casa_df.duplicated(
        subset=["account_id", "measurement_month"]
    ).any():
        raise ValueError(
            "Duplicate account and measurement month found."
        )

    # Measurement month must be the first day of a month.
    measurement_months = pd.to_datetime(
        casa_df["measurement_month"],
        errors="raise",
    )

    if not measurement_months.dt.day.eq(1).all():
        raise ValueError(
            "Measurement month must be the first day of a month."
        )

    # Acquisition date must not be after measurement month-end.
    acquisition_dates = pd.to_datetime(
        casa_df["acquisition_date"],
        errors="raise",
    ).dt.date

    measurement_month_ends = [
        month_end(value.date())
        for value in measurement_months
    ]

    for acquisition_date, measurement_month_end in zip(
        acquisition_dates,
        measurement_month_ends,
    ):
        if acquisition_date > measurement_month_end:
            raise ValueError(
                "Acquisition date is after measurement month-end."
            )

    # AMB must be non-negative when populated.
    populated_amb = casa_df[
        "average_monthly_balance"
    ].dropna()

    if (populated_amb < 0).any():
        raise ValueError(
            "Negative average monthly balance found."
        )

    # Controlled values.
    if not casa_df["account_type"].isin(
        ACCOUNT_TYPES
    ).all():
        raise ValueError("Invalid account type found.")

    if not casa_df["account_status"].isin(
        ACCOUNT_STATUSES
    ).all():
        raise ValueError("Invalid account status found.")

    if not casa_df["eligibility_status"].isin(
        ELIGIBILITY_STATUSES
    ).all():
        raise ValueError("Invalid eligibility status found.")

    if not casa_df["currency_code"].eq(
        DEFAULT_CURRENCY
    ).all():
        raise ValueError("Unexpected currency code found.")

    if not casa_df["source_system"].isin(
        SOURCE_SYSTEMS
    ).all():
        raise ValueError("Invalid source system found.")

    # Transaction date range.
    if not acquisition_dates.between(
        TRANSACTION_START_DATE,
        TRANSACTION_END_DATE,
    ).all():
        raise ValueError(
            "Acquisition date outside configured range."
        )

    if not measurement_months.dt.date.between(
        TRANSACTION_START_DATE,
        TRANSACTION_END_DATE,
    ).all():
        raise ValueError(
            "Measurement month outside configured range."
        )

    # Timestamp timezone validation.
    timestamp_columns = [
        "source_event_timestamp",
        "created_at",
    ]

    for column in timestamp_columns:
        if not casa_df[column].str.endswith(
            "+05:30"
        ).all():
            raise ValueError(
                f"{column} must contain the +05:30 timezone."
            )

    if not casa_df["updated_at"].dropna().str.endswith(
        "+05:30"
    ).all():
        raise ValueError(
            "Updated timestamps must contain the +05:30 timezone."
        )

    source_timestamps = pd.to_datetime(
        casa_df["source_event_timestamp"],
        utc=True,
        errors="raise",
    )

    created_timestamps = pd.to_datetime(
        casa_df["created_at"],
        utc=True,
        errors="raise",
    )

    if (created_timestamps < source_timestamps).any():
        raise ValueError(
            "Created timestamp precedes source event timestamp."
        )

    updated_timestamps = pd.to_datetime(
        casa_df["updated_at"],
        utc=True,
        errors="raise",
    )

    updated_mask = casa_df["updated_at"].notna()

    if (
        updated_timestamps[updated_mask]
        < created_timestamps[updated_mask]
    ).any():
        raise ValueError(
            "Updated timestamp precedes created timestamp."
        )

    # Source event timestamp must fall within measurement month.
    source_event_dates = (
        source_timestamps
        .dt.tz_convert("Asia/Kolkata")
        .dt.date
    )

    if not source_event_dates.equals(
        pd.Series(measurement_month_ends)
    ):
        raise ValueError(
            "Source event timestamp does not match measurement month-end."
        )

    # Account-level attributes must remain consistent.
    consistency_columns = [
        "partner_id",
        "product_id",
        "account_type",
        "acquisition_date",
    ]

    for column in consistency_columns:
        if (
            casa_df.groupby("account_id")[column]
            .nunique()
            .gt(1)
            .any()
        ):
            raise ValueError(
                f"Inconsistent {column} values within an account."
            )

    # Each account must have the configured number of measurements.
    account_measurement_counts = (
        casa_df.groupby("account_id").size()
    )

    if len(account_measurement_counts) != TOTAL_ACCOUNTS:
        raise ValueError(
            "Unexpected number of unique accounts."
        )

    if not account_measurement_counts.eq(
        MEASUREMENTS_PER_ACCOUNT
    ).all():
        raise ValueError(
            "Unexpected measurement count per account."
        )

    # Measurement months must be consecutive.
    for account_id, account_group in casa_df.groupby(
        "account_id"
    ):

        months = sorted(
            pd.to_datetime(
                account_group["measurement_month"]
            ).dt.date.tolist()
        )

        for previous_month, current_month in zip(
            months,
            months[1:],
        ):
            if add_months(previous_month, 1) != current_month:
                raise ValueError(
                    f"Non-consecutive measurement months for {account_id}."
                )

    # Display validation summary.
    print("CASA acquisition validation passed.")
    print(f"Total records: {len(casa_df)}")
    print(f"Unique accounts: {len(account_measurement_counts)}")
    print(
        "Measurements per account:",
        sorted(account_measurement_counts.unique().tolist()),
    )
    print(
        "Account types:",
        sorted(casa_df["account_type"].unique().tolist()),
    )
    print(
        "Account statuses:",
        sorted(casa_df["account_status"].unique().tolist()),
    )
    print(
        "Eligibility statuses:",
        sorted(casa_df["eligibility_status"].unique().tolist()),
    )
    print(
        "Null AMB records:",
        int(casa_df["average_monthly_balance"].isna().sum()),
    )
    print(
        "Source systems:",
        sorted(casa_df["source_system"].unique().tolist()),
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

    casa_df = generate_casa_acquisitions(
        partner_df,
        product_df,
    )

    validate_casa_acquisitions(
        casa_df,
        partner_df,
        product_df,
    )

    output_path = (
        GENERATED_DATA_DIR / "src_casa_acquisitions.csv"
    )

    casa_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    print(
        f"\nsrc_casa_acquisitions: "
        f"{len(casa_df)} records exported"
    )

    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()