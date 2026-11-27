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


# --------------------------------------------------
# REFERENCE CONFIGURATION
# --------------------------------------------------

SLAB_BOUNDARIES = [
    (0, 1_000_000),
    (1_000_000, 2_500_000),
    (2_500_000, 5_000_000),
    (5_000_000, None),
]

PARTNER_TYPE = "PARTNER_TYPE"
PARTNER_SPECIFIC = "PARTNER_SPECIFIC"


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def random_date(rng, start_date, end_date):
    total_days = (end_date - start_date).days
    return start_date + timedelta(
        days=rng.randint(0, total_days)
    )


def generate_effective_dates(rng, is_active):
    latest_start_date = AS_OF_DATE - timedelta(days=30)

    effective_from = random_date(
        rng,
        TRANSACTION_START_DATE,
        latest_start_date,
    )

    if is_active:
        effective_to = None
        rule_status = "ACTIVE"
        updated_at = None

    else:
        effective_to = random_date(
            rng,
            effective_from + timedelta(days=30),
            AS_OF_DATE,
        )
        rule_status = "INACTIVE"
        updated_at = (
            pd.Timestamp(effective_to)
            + pd.Timedelta(hours=12)
        ).isoformat()

    created_at = (
        pd.Timestamp(effective_from)
        + pd.Timedelta(hours=10)
    ).isoformat()

    return (
        effective_from,
        effective_to,
        rule_status,
        created_at,
        updated_at,
    )


# --------------------------------------------------
# GENERATE INCENTIVE SLABS
# --------------------------------------------------

def generate_incentive_slabs(partner_df, product_df):

    rng = random.Random(RANDOM_SEED)

    partner_types = sorted(
        partner_df["partner_type"].dropna().unique().tolist()
    )

    loan_product_ids = sorted(
        product_df.loc[
            product_df["product_category"] == "LOAN",
            "product_id",
        ].dropna().unique().tolist()
    )

    partner_ids = partner_df["partner_id"].dropna().tolist()

    if len(partner_types) != 4:
        raise ValueError(
            f"Expected 4 partner types, found {len(partner_types)}."
        )

    if len(loan_product_ids) != 5:
        raise ValueError(
            f"Expected 5 loan products, found {len(loan_product_ids)}."
        )

    if len(partner_ids) < 5:
        raise ValueError(
            "At least 5 partners are required."
        )

    selected_partner_ids = rng.sample(partner_ids, 5)

    # Five partner-type groups and five partner-specific groups.
    group_definitions = []

    for index, product_id in enumerate(loan_product_ids):
        group_definitions.append({
            "scope": PARTNER_TYPE,
            "partner_type": partner_types[index % len(partner_types)],
            "partner_id": None,
            "product_id": product_id,
            "is_active": True,
        })

    for index, product_id in enumerate(loan_product_ids):
        group_definitions.append({
            "scope": PARTNER_SPECIFIC,
            "partner_type": None,
            "partner_id": selected_partner_ids[index],
            "product_id": product_id,
            # Three active and two historical configurations.
            "is_active": index < 3,
        })

    records = []
    slab_counter = 1

    for group_number, definition in enumerate(
        group_definitions,
        start=1,
    ):

        calculation_group_id = f"INCGRP{group_number:04d}"

        (
            effective_from,
            effective_to,
            rule_status,
            created_at,
            updated_at,
        ) = generate_effective_dates(
            rng,
            definition["is_active"],
        )

        payout_cycle = (
            "QUARTERLY" if group_number in (5, 10) else "MONTHLY"
        )

        slab_calculation_type = (
            "RETROACTIVE" if group_number % 2 == 1 else "MARGINAL"
        )

        # Rates increase with each successive volume slab.
        base_rate = rng.choice([
            0.000300,
            0.000400,
            0.000500,
            0.000600,
        ])

        for slab_index, (lower_bound, upper_bound) in enumerate(
            SLAB_BOUNDARIES
        ):

            incentive_rate = round(
                base_rate + (slab_index * 0.000200),
                6,
            )

            records.append({
                "slab_id": f"INCSLAB{slab_counter:04d}",
                "calculation_group_id": calculation_group_id,
                "partner_type": definition["partner_type"],
                "partner_id": definition["partner_id"],
                "product_id": definition["product_id"],
                "payout_cycle": payout_cycle,
                "slab_calculation_type": slab_calculation_type,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "incentive_rate": incentive_rate,
                "effective_from": effective_from.isoformat(),
                "effective_to": (
                    effective_to.isoformat()
                    if effective_to else None
                ),
                "rule_status": rule_status,
                "rule_version": "V1",
                "created_at": created_at,
                "updated_at": updated_at,
            })

            slab_counter += 1

    return pd.DataFrame(records)


# --------------------------------------------------
# VALIDATE INCENTIVE SLABS
# --------------------------------------------------

def validate_incentive_slabs(
    incentive_df,
    partner_df,
    product_df,
):

    expected_count = RECORD_COUNTS["src_incentive_slabs"]

    if len(incentive_df) != expected_count:
        raise ValueError(
            f"Expected {expected_count} records, "
            f"found {len(incentive_df)}."
        )

    if incentive_df["slab_id"].isna().any():
        raise ValueError("Null slab_id values found.")

    if incentive_df["slab_id"].duplicated().any():
        raise ValueError("Duplicate slab_id values found.")

    if incentive_df["calculation_group_id"].isna().any():
        raise ValueError("Null calculation_group_id values found.")

    if incentive_df["product_id"].isna().any():
        raise ValueError("Null product_id values found.")

    if not set(incentive_df["product_id"]).issubset(
        set(product_df["product_id"])
    ):
        raise ValueError("Invalid product references found.")

    if not set(incentive_df["product_id"]).issubset(
        set(
            product_df.loc[
                product_df["product_category"] == "LOAN",
                "product_id",
            ]
        )
    ):
        raise ValueError("Non-loan product found in incentive slabs.")

    valid_partner_ids = set(partner_df["partner_id"])

    populated_partner_ids = set(
        incentive_df["partner_id"].dropna()
    )

    if not populated_partner_ids.issubset(valid_partner_ids):
        raise ValueError("Invalid partner references found.")

    valid_partner_types = set(partner_df["partner_type"])

    populated_partner_types = set(
        incentive_df["partner_type"].dropna()
    )

    if not populated_partner_types.issubset(valid_partner_types):
        raise ValueError("Invalid partner_type values found.")

    scope_count = (
        incentive_df["partner_id"].notna().astype(int)
        + incentive_df["partner_type"].notna().astype(int)
    )

    if not scope_count.eq(1).all():
        raise ValueError(
            "Exactly one of partner_id and partner_type "
            "must be populated."
        )

    if not incentive_df["payout_cycle"].isin(
        ["MONTHLY", "QUARTERLY"]
    ).all():
        raise ValueError("Invalid payout_cycle values found.")

    if not incentive_df["slab_calculation_type"].isin(
        ["RETROACTIVE", "MARGINAL"]
    ).all():
        raise ValueError("Invalid slab calculation types found.")

    if not incentive_df["rule_status"].isin(
        ["ACTIVE", "INACTIVE"]
    ).all():
        raise ValueError("Invalid rule_status values found.")

    if (incentive_df["lower_bound"] < 0).any():
        raise ValueError("Negative lower_bound values found.")

    invalid_upper_bounds = incentive_df[
        incentive_df["upper_bound"].notna()
        & (
            incentive_df["upper_bound"]
            <= incentive_df["lower_bound"]
        )
    ]

    if not invalid_upper_bounds.empty:
        raise ValueError("Invalid upper_bound values found.")

    if (incentive_df["incentive_rate"] < 0).any():
        raise ValueError("Negative incentive rates found.")

    # Every calculation group must contain exactly four slabs.
    group_sizes = incentive_df.groupby(
        "calculation_group_id"
    ).size()

    if not group_sizes.eq(4).all():
        raise ValueError(
            "Every calculation group must contain exactly 4 slabs."
        )

    expected_boundaries = SLAB_BOUNDARIES

    for group_id, group in incentive_df.groupby(
        "calculation_group_id"
    ):

        group = group.sort_values("lower_bound")

        actual_boundaries = [
            (
                int(lower),
                None if pd.isna(upper) else int(upper),
            )
            for lower, upper in zip(
                group["lower_bound"],
                group["upper_bound"],
            )
        ]

        if actual_boundaries != expected_boundaries:
            raise ValueError(
                f"Invalid or discontinuous slab boundaries "
                f"in {group_id}."
            )

        # Configuration-level attributes must remain consistent.
        consistent_columns = [
            "partner_id",
            "partner_type",
            "product_id",
            "payout_cycle",
            "slab_calculation_type",
            "effective_from",
            "effective_to",
            "rule_status",
            "rule_version",
            "created_at",
            "updated_at",
        ]

        for column in consistent_columns:
            if group[column].nunique(dropna=False) != 1:
                raise ValueError(
                    f"Inconsistent {column} values in {group_id}."
                )

    print("Incentive slab validation passed.")
    print(f"Total records: {len(incentive_df)}")
    print(f"Calculation groups: {incentive_df['calculation_group_id'].nunique()}")
    print(f"Slabs per group: {group_sizes.unique().tolist()}")
    print(f"Partner-type records: {incentive_df['partner_type'].notna().sum()}")
    print(f"Partner-specific records: {incentive_df['partner_id'].notna().sum()}")
    print(
        "Calculation types:",
        sorted(incentive_df["slab_calculation_type"].unique()),
    )
    print(
        "Payout cycles:",
        sorted(incentive_df["payout_cycle"].unique()),
    )


# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------

def main():

    ensure_output_directories()

    partner_path = GENERATED_DATA_DIR / "src_partner_master.csv"
    product_path = GENERATED_DATA_DIR / "src_product_master.csv"

    if not partner_path.exists():
        raise FileNotFoundError(
            "src_partner_master.csv not found."
        )

    if not product_path.exists():
        raise FileNotFoundError(
            "src_product_master.csv not found."
        )

    partner_df = pd.read_csv(partner_path)
    product_df = pd.read_csv(product_path)

    incentive_df = generate_incentive_slabs(
        partner_df,
        product_df,
    )

    validate_incentive_slabs(
        incentive_df,
        partner_df,
        product_df,
    )

    output_path = (
        GENERATED_DATA_DIR / "src_incentive_slabs.csv"
    )

    incentive_df.to_csv(
        output_path,
        index=False,
        encoding="utf-8",
    )

    print(
        f"\nsrc_incentive_slabs: "
        f"{len(incentive_df)} records exported"
    )
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()