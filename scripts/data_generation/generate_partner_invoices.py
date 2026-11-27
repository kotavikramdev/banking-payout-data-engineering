import random
import calendar
from datetime import datetime, date, time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from zoneinfo import ZoneInfo

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
# CONFIGURATION
# --------------------------------------------------

random.seed(RANDOM_SEED)

IST = ZoneInfo("Asia/Kolkata")

INVOICE_STATUSES = [
    "VALIDATED",
    "SUBMITTED",
    "REJECTED",
]

STATUS_COUNTS = {
    "VALIDATED": 60,
    "SUBMITTED": 25,
    "REJECTED": 15,
}

VALIDATION_REASONS = {
    "SUBMITTED": [
        "AWAITING_VALIDATION",
        "DOCUMENT_REVIEW_PENDING",
        "TAX_DETAILS_UNDER_REVIEW",
    ],
    "REJECTED": [
        "PARTNER_TAX_PROFILE_MISMATCH",
        "GST_AMOUNT_MISMATCH",
        "INVALID_INVOICE_DETAILS",
    ],
}

SOURCE_SYSTEMS = [
    "PARTNER_PORTAL",
    "INVOICE_MANAGEMENT",
]

PAYOUT_CYCLE = "MONTHLY"

# Illustrative synthetic GST rate; not a statutory assertion.
SYNTHETIC_GST_RATE = Decimal("0.18")

MONEY_QUANTUM = Decimal(
    "1"
).scaleb(-MONEY_DECIMAL_PLACES)

EXPECTED_COLUMNS = [
    "invoice_id",
    "partner_id",
    "invoice_number",
    "invoice_date",
    "invoice_period_start",
    "invoice_period_end",
    "taxable_amount",
    "gst_amount",
    "total_invoice_amount",
    "currency_code",
    "invoice_status",
    "validation_reason",
    "source_system",
    "payout_cycle",
    "created_at",
    "updated_at",
]


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def money(value):
    """Round a monetary value using the project convention."""

    return Decimal(str(value)).quantize(
        MONEY_QUANTUM,
        rounding=ROUND_HALF_UP,
    )


def random_timestamp(invoice_date):
    """Generate a timezone-aware IST timestamp."""

    hour = random.randint(9, 17)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    return datetime.combine(
        invoice_date,
        time(hour, minute, second),
    ).replace(tzinfo=IST)


def month_period(year, month):
    """Return the first and last dates of a calendar month."""

    last_day = calendar.monthrange(year, month)[1]

    return (
        date(year, month, 1),
        date(year, month, last_day),
    )


# --------------------------------------------------
# GENERATE PARTNER INVOICES
# --------------------------------------------------

def generate_partner_invoices(partner_df):

    total_records = RECORD_COUNTS[
        "src_partner_invoices"
    ]

    if total_records != 100:
        raise ValueError(
            "This generation design expects "
            "RECORD_COUNTS['src_partner_invoices'] = 100."
        )

    partner_ids = partner_df["partner_id"].dropna().unique().tolist()

    if len(partner_ids) < 10:
        raise ValueError(
            "At least 10 valid partners are required."
        )

    # Build the exact planned invoice status distribution.
    invoice_statuses = []

    for status, count in STATUS_COUNTS.items():
        invoice_statuses.extend([status] * count)

    random.shuffle(invoice_statuses)

    records = []
    invoice_index = 1
    status_index = 0

    # Generate 10 invoices for each month from January to October 2026.
    for month in range(1, 11):

        period_start, period_end = month_period(
            2026,
            month,
        )

        # Avoid more than one invoice for the same partner
        # in a given monthly invoice period.
        monthly_partners = random.sample(
            partner_ids,
            10,
        )

        for partner_id in monthly_partners:

            invoice_status = invoice_statuses[
                status_index
            ]

            status_index += 1

            # Generate a positive taxable amount.
            taxable_amount = money(
                Decimal(
                    str(random.randint(8000, 150000))
                )
            )

            # Synthetic GST amount.
            gst_amount = money(
                taxable_amount * SYNTHETIC_GST_RATE
            )

            total_invoice_amount = money(
                taxable_amount + gst_amount
            )

            # Invoice date is the last day of its invoice period.
            invoice_date = period_end

            validation_reason = None

            if invoice_status in VALIDATION_REASONS:
                validation_reason = random.choice(
                    VALIDATION_REASONS[invoice_status]
                )

            created_at = random_timestamp(invoice_date)

            if invoice_status == "VALIDATED":
                updated_at = created_at + timedelta(
                    hours=random.randint(1, 3)
                )
            elif invoice_status == "REJECTED":
                updated_at = created_at + timedelta(
                    hours=random.randint(1, 3)
                )
            else:
                # Submitted invoices have not completed validation.
                updated_at = created_at

            invoice_id = f"INV{invoice_index:04d}"

            invoice_number = (
                f"INV-{partner_id}-{period_start:%Y%m}"
            )

            records.append({
                "invoice_id": invoice_id,
                "partner_id": partner_id,
                "invoice_number": invoice_number,
                "invoice_date": invoice_date,
                "invoice_period_start": period_start,
                "invoice_period_end": period_end,
                "taxable_amount": taxable_amount,
                "gst_amount": gst_amount,
                "total_invoice_amount": total_invoice_amount,
                "currency_code": DEFAULT_CURRENCY,
                "invoice_status": invoice_status,
                "validation_reason": validation_reason,
                "source_system": random.choice(SOURCE_SYSTEMS),
                "payout_cycle": PAYOUT_CYCLE,
                "created_at": created_at,
                "updated_at": updated_at,
            })

            invoice_index += 1

    invoice_df = pd.DataFrame(
        records,
        columns=EXPECTED_COLUMNS,
    )

    return invoice_df


# --------------------------------------------------
# VALIDATE PARTNER INVOICES
# --------------------------------------------------

def validate_partner_invoices(invoice_df, partner_df):

    expected_count = RECORD_COUNTS[
        "src_partner_invoices"
    ]

    assert len(invoice_df) == expected_count, (
        f"Expected {expected_count} records, "
        f"found {len(invoice_df)}."
    )

    assert invoice_df.columns.tolist() == EXPECTED_COLUMNS, (
        "Invoice schema or column order mismatch."
    )

    # Primary key validation.
    assert invoice_df["invoice_id"].notna().all()
    assert invoice_df["invoice_id"].is_unique

    # Partner reference validation.
    valid_partner_ids = set(
        partner_df["partner_id"].dropna()
    )

    assert invoice_df["partner_id"].notna().all()

    assert set(
        invoice_df["partner_id"]
    ).issubset(valid_partner_ids)

    # Partner invoice number uniqueness.
    assert not invoice_df.duplicated(
        subset=["partner_id", "invoice_number"]
    ).any()

    assert invoice_df["invoice_number"].notna().all()

    # Required fields.
    required_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column != "validation_reason"
    ]

    assert invoice_df[required_columns].notna().all().all()

    # Date validations.
    invoice_df["invoice_date"] = pd.to_datetime(
        invoice_df["invoice_date"]
    ).dt.date

    invoice_df["invoice_period_start"] = pd.to_datetime(
        invoice_df["invoice_period_start"]
    ).dt.date

    invoice_df["invoice_period_end"] = pd.to_datetime(
        invoice_df["invoice_period_end"]
    ).dt.date

    assert (
        invoice_df["invoice_period_start"]
        <= invoice_df["invoice_period_end"]
    ).all()

    assert (
        invoice_df["invoice_date"]
        >= invoice_df["invoice_period_start"]
    ).all()

    assert (
        invoice_df["invoice_date"]
        <= invoice_df["invoice_period_end"]
    ).all()

    assert (
        invoice_df["invoice_date"]
        <= TRANSACTION_END_DATE
    ).all()

    # Invoice period must be a calendar month.
    assert (
        invoice_df["invoice_period_start"].apply(
            lambda value: value.day == 1
        )
    ).all()

    assert (
        invoice_df["invoice_period_end"].apply(
            lambda value: value.day
            == calendar.monthrange(
                value.year,
                value.month,
            )[1]
        )
    ).all()

    # Financial validations.
    assert (
        invoice_df["taxable_amount"].apply(
            lambda value: Decimal(str(value)) >= 0
        )
    ).all()

    assert (
        invoice_df["gst_amount"].apply(
            lambda value: Decimal(str(value)) >= 0
        )
    ).all()

    assert (
        invoice_df.apply(
            lambda row: money(
                Decimal(str(row["taxable_amount"]))
                + Decimal(str(row["gst_amount"]))
            ) == money(row["total_invoice_amount"]),
            axis=1,
        )
    ).all()

    # Synthetic GST calculation validation.
    assert (
        invoice_df.apply(
            lambda row: money(
                Decimal(str(row["taxable_amount"]))
                * SYNTHETIC_GST_RATE
            ) == money(row["gst_amount"]),
            axis=1,
        )
    ).all()

    # Allowed values.
    assert set(
        invoice_df["invoice_status"].unique()
    ).issubset(set(INVOICE_STATUSES))

    assert set(
        invoice_df["currency_code"].unique()
    ) == {DEFAULT_CURRENCY}

    assert set(
        invoice_df["payout_cycle"].unique()
    ) == {PAYOUT_CYCLE}

    assert set(
        invoice_df["source_system"].unique()
    ).issubset(set(SOURCE_SYSTEMS))

    # Status and validation-reason rules.
    validated = invoice_df[
        invoice_df["invoice_status"] == "VALIDATED"
    ]

    submitted = invoice_df[
        invoice_df["invoice_status"] == "SUBMITTED"
    ]

    rejected = invoice_df[
        invoice_df["invoice_status"] == "REJECTED"
    ]

    assert validated["validation_reason"].isna().all()

    assert submitted["validation_reason"].notna().all()

    assert rejected["validation_reason"].notna().all()

    assert submitted["validation_reason"].isin(
        VALIDATION_REASONS["SUBMITTED"]
    ).all()

    assert rejected["validation_reason"].isin(
        VALIDATION_REASONS["REJECTED"]
    ).all()

    # Exact status distribution.
    actual_status_counts = (
        invoice_df["invoice_status"]
        .value_counts()
        .to_dict()
    )

    assert actual_status_counts == STATUS_COUNTS, (
        f"Unexpected invoice status distribution: "
        f"{actual_status_counts}"
    )

    # Ten invoices per monthly period.
    monthly_counts = (
        invoice_df.groupby("invoice_period_start")
        .size()
    )

    assert len(monthly_counts) == 10
    assert (monthly_counts == 10).all()

    # Timestamp validations.
    created_timestamps = pd.to_datetime(
        invoice_df["created_at"],
        utc=True,
    )

    updated_timestamps = pd.to_datetime(
        invoice_df["updated_at"],
        utc=True,
    )

    assert (updated_timestamps >= created_timestamps).all()

    assert created_timestamps.notna().all()
    assert updated_timestamps.notna().all()

    print("Partner invoice validation passed.")
    print(f"Total records: {len(invoice_df)}")
    print(
        "Unique partners:",
        invoice_df["partner_id"].nunique(),
    )

    print("\nInvoice status distribution:")
    print(invoice_df["invoice_status"].value_counts())

    print("\nMonthly invoice distribution:")
    print(
        invoice_df.groupby("invoice_period_start")
        .size()
    )

    print("\nSource systems:")
    print(sorted(invoice_df["source_system"].unique()))

    print("\nFinancial reconciliation:")
    print("All invoice totals equal taxable amount + GST.")
    print("All synthetic GST amounts reconcile at 18%.")


# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------

def main():

    ensure_output_directories()

    partner_file = (
        GENERATED_DATA_DIR / "src_partner_master.csv"
    )

    if not partner_file.exists():
        raise FileNotFoundError(
            f"Partner master file not found: {partner_file}"
        )

    partner_df = pd.read_csv(
        partner_file,
        dtype={"partner_id": "string"},
    )

    invoice_df = generate_partner_invoices(
        partner_df
    )

    validate_partner_invoices(
        invoice_df,
        partner_df,
    )

    output_file = (
        GENERATED_DATA_DIR / "src_partner_invoices.csv"
    )

    invoice_df.to_csv(
        output_file,
        index=False,
    )

    print(
        f"\nsrc_partner_invoices: "
        f"{len(invoice_df)} records exported"
    )

    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()