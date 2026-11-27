import random
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

import pandas as pd

try:
    from .config import (
        GENERATED_DATA_DIR,
        RANDOM_SEED,
        TRANSACTION_START_DATE,
        TRANSACTION_END_DATE,
        AS_OF_DATE,
        RECORD_COUNTS,
        RATE_DECIMAL_PLACES,
        ensure_output_directories,
    )
except ImportError:
    from config import (
        GENERATED_DATA_DIR,
        RANDOM_SEED,
        TRANSACTION_START_DATE,
        TRANSACTION_END_DATE,
        AS_OF_DATE,
        RECORD_COUNTS,
        RATE_DECIMAL_PLACES,
        ensure_output_directories,
    )


# --------------------------------------------------
# 1. CONFIGURATION AND REFERENCE DATA
# --------------------------------------------------

random.seed(RANDOM_SEED)

IST = timezone(timedelta(hours=5, minutes=30))

PARTNER_TYPES = [
    "DSA",
    "AUTO_DEALER",
    "TRACTOR_DEALER",
    "CONNECTOR",
]

TAX_TYPES = ["TDS"]

CALCULATION_BASES = [
    "GROSS_COMMISSION",
    "COMMISSION_PLUS_INCENTIVE",
]

DATE_BASES = [
    "TRANSACTION_DATE",
    "INVOICE_DATE",
    "PAYOUT_DATE",
]

COLUMNS = [
    "tax_rule_id",
    "tax_rule_name",
    "partner_type",
    "tax_type",
    "tax_rate",
    "tax_calculation_basis",
    "tax_date_basis",
    "effective_from",
    "effective_to",
    "rule_status",
    "rule_version",
    "created_at",
    "updated_at",
]


# --------------------------------------------------
# 2. HELPER FUNCTIONS
# --------------------------------------------------

def make_timestamp(timestamp_date, hour=10, minute=0):
    """Create a timezone-aware IST timestamp."""

    return datetime.combine(
        timestamp_date,
        time(hour, minute),
        tzinfo=IST,
    )


def format_rate(rate):
    """Format a rate to the configured decimal precision."""

    return Decimal(str(rate)).quantize(
        Decimal("1").scaleb(-RATE_DECIMAL_PLACES)
    )


# --------------------------------------------------
# 3. GENERATE GENERAL TDS RULE VERSIONS
# --------------------------------------------------

def generate_general_rules():
    """
    Generate four sequential general TDS rule versions.

    General rules apply to all supported partner types
    when no partner-type-specific rule is available.
    """

    periods = [
        (date(2025, 1, 1), date(2025, 7, 1)),
        (date(2025, 7, 1), date(2026, 1, 1)),
        (date(2026, 1, 1), date(2026, 7, 1)),
        (date(2026, 7, 1), None),
    ]

    illustrative_rates = [
        Decimal("0.010000"),
        Decimal("0.012000"),
        Decimal("0.015000"),
        Decimal("0.020000"),
    ]

    records = []

    for index, ((effective_from, effective_to), rate) in enumerate(
        zip(periods, illustrative_rates),
        start=1,
    ):
        created_date = effective_from - timedelta(days=7)

        if effective_to is not None:
            updated_date = effective_to - timedelta(days=1)
            status = "INACTIVE"
        else:
            updated_date = AS_OF_DATE
            status = "ACTIVE"

        records.append({
            "tax_rule_id": f"TAX{index:04d}",
            "tax_rule_name": f"General TDS Rule V{index}",
            "partner_type": None,
            "tax_type": "TDS",
            "tax_rate": format_rate(rate),
            "tax_calculation_basis": "GROSS_COMMISSION",
            "tax_date_basis": "PAYOUT_DATE",
            "effective_from": effective_from,
            "effective_to": effective_to,
            "rule_status": status,
            "rule_version": f"V{index}",
            "created_at": make_timestamp(created_date),
            "updated_at": make_timestamp(updated_date),
        })

    return records


# --------------------------------------------------
# 4. GENERATE PARTNER-TYPE-SPECIFIC TDS RULES
# --------------------------------------------------

def generate_partner_type_rules():
    """
    Generate one current TDS rule for each partner type.

    These rules take precedence over general TDS rules
    when both are applicable for the same date.
    """

    partner_rates = {
        "DSA": Decimal("0.018000"),
        "AUTO_DEALER": Decimal("0.020000"),
        "TRACTOR_DEALER": Decimal("0.015000"),
        "CONNECTOR": Decimal("0.012000"),
    }

    calculation_bases = {
        "DSA": "GROSS_COMMISSION",
        "AUTO_DEALER": "COMMISSION_PLUS_INCENTIVE",
        "TRACTOR_DEALER": "GROSS_COMMISSION",
        "CONNECTOR": "COMMISSION_PLUS_INCENTIVE",
    }

    records = []

    for index, partner_type in enumerate(PARTNER_TYPES, start=5):

        effective_from = TRANSACTION_START_DATE
        created_date = effective_from - timedelta(days=3)

        records.append({
            "tax_rule_id": f"TAX{index:04d}",
            "tax_rule_name": f"{partner_type} TDS Rule",
            "partner_type": partner_type,
            "tax_type": "TDS",
            "tax_rate": format_rate(partner_rates[partner_type]),
            "tax_calculation_basis": calculation_bases[partner_type],
            "tax_date_basis": "PAYOUT_DATE",
            "effective_from": effective_from,
            "effective_to": None,
            "rule_status": "ACTIVE",
            "rule_version": "V1",
            "created_at": make_timestamp(created_date),
            "updated_at": make_timestamp(AS_OF_DATE),
        })

    return records


# --------------------------------------------------
# 5. VALIDATE TAX RULES
# --------------------------------------------------

def validate_tax_rules(df):

    expected_count = RECORD_COUNTS["src_tax_rules"]

    # Record count and schema.
    assert len(df) == expected_count, (
        f"Expected {expected_count} records, found {len(df)}"
    )

    assert list(df.columns) == COLUMNS, (
        "Tax rule columns do not match the expected schema."
    )

    # Primary key.
    assert df["tax_rule_id"].notna().all()
    assert df["tax_rule_id"].is_unique

    # Mandatory fields.
    mandatory_columns = [
        column
        for column in COLUMNS
        if column != "partner_type" and column != "effective_to"
    ]

    for column in mandatory_columns:
        assert df[column].notna().all(), (
            f"Null values found in mandatory column: {column}"
        )

    # Partner types.
    assert set(df["partner_type"].dropna()).issubset(
        set(PARTNER_TYPES)
    )

    # Tax type.
    assert set(df["tax_type"]) == {"TDS"}

    # Tax rates.
    assert df["tax_rate"].map(
        lambda value: Decimal(str(value)) >= Decimal("0")
    ).all()

    assert df["tax_rate"].map(
        lambda value: Decimal(str(value)).as_tuple().exponent
        >= -RATE_DECIMAL_PLACES
    ).all()

    # Calculation basis and date basis.
    assert set(df["tax_calculation_basis"]).issubset(
        set(CALCULATION_BASES)
    )

    assert set(df["tax_date_basis"]).issubset(
        set(DATE_BASES)
    )

    # Rule status and version.
    assert set(df["rule_status"]).issubset(
        {"ACTIVE", "INACTIVE"}
    )

    assert df["rule_version"].str.match(r"^V\d+$").all()

    # Effective dates.
    for row in df.itertuples(index=False):

        assert row.effective_from <= AS_OF_DATE or (
            row.rule_status == "INACTIVE"
        ), f"Unexpected future effective date: {row.tax_rule_id}"

        if row.effective_to is not None and pd.notna(row.effective_to):
            assert row.effective_to > row.effective_from, (
                f"Invalid effective period: {row.tax_rule_id}"
            )

        assert row.effective_from >= TRANSACTION_START_DATE, (
            f"Effective start before configured range: {row.tax_rule_id}"
        )

    # Audit timestamps.
    for row in df.itertuples(index=False):

        assert row.created_at.tzinfo is not None
        assert row.updated_at.tzinfo is not None

        assert row.created_at <= row.updated_at, (
            f"Updated timestamp precedes created timestamp: "
            f"{row.tax_rule_id}"
        )

        assert row.created_at.date() <= row.effective_from, (
            f"Created timestamp is after effective start: "
            f"{row.tax_rule_id}"
        )

        assert row.updated_at.date() <= AS_OF_DATE, (
            f"Updated timestamp exceeds as-of date: {row.tax_rule_id}"
        )

    # Expected rule distribution.
    general_rules = df[df["partner_type"].isna()]
    specific_rules = df[df["partner_type"].notna()]

    assert len(general_rules) == 4
    assert len(specific_rules) == 4

    assert set(specific_rules["partner_type"]) == set(PARTNER_TYPES)

    # Exactly one current general rule and one current rule
    # for each partner type.
    active_rules = df[df["rule_status"] == "ACTIVE"]

    assert len(active_rules[active_rules["partner_type"].isna()]) == 1

    for partner_type in PARTNER_TYPES:
        matching = active_rules[
            active_rules["partner_type"] == partner_type
        ]
        assert len(matching) == 1, (
            f"Expected exactly one active rule for {partner_type}"
        )

    # Check for overlapping effective periods at the same
    # applicability level, tax type and date basis.
    grouping_columns = [
        "partner_type",
        "tax_type",
        "tax_date_basis",
    ]

    for _, group in df.groupby(
        grouping_columns,
        dropna=False,
    ):
        ordered = group.sort_values("effective_from")

        previous_end = None

        for row in ordered.itertuples(index=False):

            if previous_end is not None:
                assert row.effective_from >= previous_end, (
                    f"Overlapping tax rules detected in group "
                    f"{row.partner_type}"
                )

            previous_end = row.effective_to

    # General rule versions must form continuous history.
    ordered_general = general_rules.sort_values("effective_from")

    for index in range(len(ordered_general) - 1):
        current = ordered_general.iloc[index]
        following = ordered_general.iloc[index + 1]

        assert current["effective_to"] == following["effective_from"], (
            "Gap or overlap detected in general rule history."
        )

    # Historical general rules must be inactive.
    assert (
        ordered_general.iloc[:-1]["rule_status"] == "INACTIVE"
    ).all()

    assert ordered_general.iloc[-1]["rule_status"] == "ACTIVE"

    # Partner-specific rules must remain active.
    assert (specific_rules["rule_status"] == "ACTIVE").all()

    print("Tax rule validation passed.")
    print(f"Total records: {len(df)}")
    print(f"General rules: {len(general_rules)}")
    print(f"Partner-type rules: {len(specific_rules)}")
    print(f"Active rules: {(df['rule_status'] == 'ACTIVE').sum()}")
    print(f"Inactive rules: {(df['rule_status'] == 'INACTIVE').sum()}")
    print(f"Tax types: {sorted(df['tax_type'].unique())}")
    print(
        "Calculation bases:",
        sorted(df["tax_calculation_basis"].unique()),
    )
    print(
        "Date bases:",
        sorted(df["tax_date_basis"].unique()),
    )


# --------------------------------------------------
# 6. MAIN GENERATION AND EXPORT
# --------------------------------------------------

def main():

    ensure_output_directories()

    records = (
        generate_general_rules()
        + generate_partner_type_rules()
    )

    df = pd.DataFrame(records, columns=COLUMNS)

    # Sort by identifier for deterministic output.
    df = df.sort_values("tax_rule_id").reset_index(drop=True)

    validate_tax_rules(df)

    output_path = GENERATED_DATA_DIR / "src_tax_rules.csv"

    df.to_csv(
        output_path,
        index=False,
        date_format="%Y-%m-%d",
    )

    print()
    print(f"src_tax_rules: {len(df)} records exported")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()