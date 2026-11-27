from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "generated"

DATASETS = {
    "partners": "src_partner_master.csv",
    "products": "src_product_master.csv",
    "agreements": "src_partner_agreements.csv",
    "kyc": "src_partner_kyc.csv",
    "rate_cards": "src_rate_cards.csv",
    "incentive_slabs": "src_incentive_slabs.csv",
    "tax_rules": "src_tax_rules.csv",
    "disbursements": "src_disbursements.csv",
    "casa": "src_casa_acquisitions.csv",
    "adjustments": "src_adjustments.csv",
    "invoices": "src_partner_invoices.csv",
}

PRIMARY_KEYS = {
    "partners": "partner_id",
    "products": "product_id",
    "agreements": "agreement_id",
    "kyc": "kyc_record_id",
    "rate_cards": "rate_card_id",
    "incentive_slabs": "slab_id",
    "tax_rules": "tax_rule_id",
    "disbursements": "disbursement_event_id",
    "casa": "acquisition_event_id",
    "adjustments": "adjustment_id",
    "invoices": "invoice_id",
}

ALLOWED_PARTNER_TYPES = {
    "DSA",
    "AUTO_DEALER",
    "TRACTOR_DEALER",
    "CONNECTOR",
}


# ---------------------------------------------------------------------
# Reporting helpers
# ---------------------------------------------------------------------

issues = []


def add_issue(check, dataset, count, samples=None):
    """Record a validation failure without modifying source data."""
    if count == 0:
        return

    issues.append({
        "check": check,
        "dataset": dataset,
        "count": int(count),
        "samples": list(samples or [])[:5],
    })


def load_datasets():
    """Load all generated CSV files as strings."""
    data = {}

    for key, filename in DATASETS.items():
        path = DATA_DIR / filename

        if not path.exists():
            raise FileNotFoundError(
                f"Required source file not found: {path}"
            )

        data[key] = pd.read_csv(
            path,
            dtype=str,
            keep_default_na=False,
        )

    return data


def validate_primary_keys(data):
    """Check that every dataset has unique, populated primary keys."""
    print("\n--- Primary Key Validation ---")

    for dataset, key_column in PRIMARY_KEYS.items():
        df = data[dataset]

        blank_mask = df[key_column].str.strip().eq("")
        duplicate_mask = (
            df[key_column].ne("")
            & df[key_column].duplicated(keep=False)
        )

        add_issue(
            "NULL_OR_BLANK_PRIMARY_KEY",
            dataset,
            blank_mask.sum(),
            df.loc[blank_mask].index.tolist(),
        )

        add_issue(
            "DUPLICATE_PRIMARY_KEY",
            dataset,
            df.loc[duplicate_mask, key_column].nunique(),
            df.loc[duplicate_mask, key_column].unique().tolist(),
        )

        print(
            f"{dataset}: {key_column} | "
            f"rows={len(df)} | "
            f"blank={blank_mask.sum()} | "
            f"duplicate_keys="
            f"{df.loc[duplicate_mask, key_column].nunique()}"
        )


def validate_foreign_key(
    child_df,
    child_dataset,
    child_column,
    parent_df,
    parent_column,
    parent_dataset,
    optional=False,
):
    """Validate mandatory or populated optional foreign-key references."""
    values = child_df[child_column].str.strip()

    if optional:
        reference_mask = values.ne("")
    else:
        blank_mask = values.eq("")

        add_issue(
            f"NULL_OR_BLANK_FK_{child_column}",
            child_dataset,
            blank_mask.sum(),
            child_df.loc[blank_mask].index.tolist(),
        )

        reference_mask = values.ne("")

    parent_values = set(
        parent_df[parent_column].str.strip()
    )

    orphan_mask = reference_mask & ~values.isin(parent_values)

    add_issue(
        f"ORPHAN_FK_{child_column}",
        child_dataset,
        orphan_mask.sum(),
        values.loc[orphan_mask].unique().tolist(),
    )


def validate_foreign_keys(data):
    """Validate relationships defined in the relationship document."""
    print("\n--- Foreign Key Validation ---")

    partners = data["partners"]
    products = data["products"]

    partner_relationships = [
        ("agreements", "partner_id"),
        ("kyc", "partner_id"),
        ("disbursements", "partner_id"),
        ("casa", "partner_id"),
        ("invoices", "partner_id"),
        ("adjustments", "partner_id"),
    ]

    for child_name, column in partner_relationships:
        validate_foreign_key(
            data[child_name],
            child_name,
            column,
            partners,
            "partner_id",
            "partners",
        )

    product_relationships = [
        ("disbursements", "product_id"),
        ("casa", "product_id"),
        ("rate_cards", "product_id"),
        ("incentive_slabs", "product_id"),
        ("adjustments", "product_id"),
    ]

    for child_name, column in product_relationships:
        validate_foreign_key(
            data[child_name],
            child_name,
            column,
            products,
            "product_id",
            "products",
        )

    # Partner-specific rule references are optional, but must resolve
    # whenever partner_id is populated.
    for child_name in ("rate_cards", "incentive_slabs"):
        validate_foreign_key(
            data[child_name],
            child_name,
            "partner_id",
            partners,
            "partner_id",
            "partners",
            optional=True,
        )


def validate_rule_applicability(data):
    """Exactly one of partner_id or partner_type must be populated."""
    print("\n--- Rule Applicability Validation ---")

    for dataset in ("rate_cards", "incentive_slabs"):
        df = data[dataset]

        has_partner_id = df["partner_id"].str.strip().ne("")
        has_partner_type = df["partner_type"].str.strip().ne("")

        invalid_mask = has_partner_id.eq(has_partner_type)

        add_issue(
            "INVALID_RULE_APPLICABILITY",
            dataset,
            invalid_mask.sum(),
            df.loc[
                invalid_mask,
                PRIMARY_KEYS[dataset],
            ].tolist(),
        )

        invalid_type_mask = (
            has_partner_type
            & ~df["partner_type"].isin(ALLOWED_PARTNER_TYPES)
        )

        add_issue(
            "INVALID_PARTNER_TYPE",
            dataset,
            invalid_type_mask.sum(),
            df.loc[
                invalid_type_mask,
                "partner_type",
            ].unique().tolist(),
        )

    # Validate partner types in the partner master.
    partner_type_mask = ~data["partners"]["partner_type"].isin(
        ALLOWED_PARTNER_TYPES
    )

    add_issue(
        "INVALID_PARTNER_MASTER_TYPE",
        "partners",
        partner_type_mask.sum(),
        data["partners"].loc[
            partner_type_mask,
            "partner_type",
        ].unique().tolist(),
    )

    # Tax rules: NULL partner_type means a general rule.
    tax_types = data["tax_rules"]["partner_type"].str.strip()
    invalid_tax_type_mask = (
        tax_types.ne("")
        & ~tax_types.isin(ALLOWED_PARTNER_TYPES)
    )

    add_issue(
        "INVALID_TAX_RULE_PARTNER_TYPE",
        "tax_rules",
        invalid_tax_type_mask.sum(),
        tax_types.loc[invalid_tax_type_mask].unique().tolist(),
    )


def validate_product_categories(data):
    """Validate transaction product categories."""
    print("\n--- Product Category Validation ---")

    products = data["products"]

    product_category_map = (
        products.drop_duplicates("product_id")
        .set_index("product_id")["product_category"]
        .to_dict()
    )

    expected_categories = {
        "disbursements": "LOAN",
        "casa": "CASA",
    }

    for dataset, expected_category in expected_categories.items():
        df = data[dataset]

        actual_categories = df["product_id"].map(
            product_category_map
        )

        invalid_mask = actual_categories.ne(expected_category)

        add_issue(
            f"INVALID_PRODUCT_CATEGORY_{expected_category}",
            dataset,
            invalid_mask.sum(),
            df.loc[
                invalid_mask,
                ["product_id"],
            ].drop_duplicates().to_dict("records"),
        )

    # Product master category values must be supported.
    invalid_master_mask = ~products["product_category"].isin(
        {"LOAN", "CASA"}
    )

    add_issue(
        "INVALID_PRODUCT_MASTER_CATEGORY",
        "products",
        invalid_master_mask.sum(),
        products.loc[
            invalid_master_mask,
            ["product_id", "product_category"],
        ].to_dict("records"),
    )


def validate_adjustment_references(data):
    """Resolve polymorphic adjustment references to their source events."""
    print("\n--- Adjustment Event Reference Validation ---")

    adjustments = data["adjustments"]

    disbursement_ids = set(
        data["disbursements"]["disbursement_event_id"]
    )
    casa_ids = set(
        data["casa"]["acquisition_event_id"]
    )

    invalid_type_mask = ~adjustments[
        "original_source_event_type"
    ].isin({"DISBURSEMENT", "CASA_ACQUISITION"})

    add_issue(
        "INVALID_ADJUSTMENT_EVENT_TYPE",
        "adjustments",
        invalid_type_mask.sum(),
        adjustments.loc[
            invalid_type_mask,
            "original_source_event_type",
        ].unique().tolist(),
    )

    blank_event_mask = adjustments[
        "original_source_event_id"
    ].str.strip().eq("")

    add_issue(
        "BLANK_ADJUSTMENT_SOURCE_EVENT_ID",
        "adjustments",
        blank_event_mask.sum(),
        adjustments.loc[
            blank_event_mask,
            "adjustment_id",
        ].tolist(),
    )

    disbursement_mask = (
        adjustments["original_source_event_type"]
        .eq("DISBURSEMENT")
    )

    casa_mask = (
        adjustments["original_source_event_type"]
        .eq("CASA_ACQUISITION")
    )

    missing_disbursement = (
        disbursement_mask
        & ~adjustments["original_source_event_id"].isin(
            disbursement_ids
        )
    )

    missing_casa = (
        casa_mask
        & ~adjustments["original_source_event_id"].isin(
            casa_ids
        )
    )

    add_issue(
        "UNRESOLVED_DISBURSEMENT_EVENT",
        "adjustments",
        missing_disbursement.sum(),
        adjustments.loc[
            missing_disbursement,
            "original_source_event_id",
        ].tolist(),
    )

    add_issue(
        "UNRESOLVED_CASA_EVENT",
        "adjustments",
        missing_casa.sum(),
        adjustments.loc[
            missing_casa,
            "original_source_event_id",
        ].tolist(),
    )

    # The referenced event must have the same partner and product.
    disbursement_lookup = (
        data["disbursements"]
        .drop_duplicates("disbursement_event_id")
        .set_index("disbursement_event_id")[
            ["partner_id", "product_id"]
        ]
        .to_dict("index")
    )

    casa_lookup = (
        data["casa"]
        .drop_duplicates("acquisition_event_id")
        .set_index("acquisition_event_id")[
            ["partner_id", "product_id"]
        ]
        .to_dict("index")
    )

    mismatch_ids = []

    for row in adjustments.itertuples(index=False):
        event_type = row.original_source_event_type
        event_id = row.original_source_event_id

        if event_type == "DISBURSEMENT":
            source = disbursement_lookup.get(event_id)
        elif event_type == "CASA_ACQUISITION":
            source = casa_lookup.get(event_id)
        else:
            continue

        if source is None:
            continue

        if (
            source["partner_id"] != row.partner_id
            or source["product_id"] != row.product_id
        ):
            mismatch_ids.append(row.adjustment_id)

    add_issue(
        "ADJUSTMENT_PARTNER_PRODUCT_MISMATCH",
        "adjustments",
        len(mismatch_ids),
        mismatch_ids,
    )


def validate_casa_measurement_conflicts(data):
    """
    Different acquisition event IDs with different AMB values
    for the same account and measurement month are conflicts.
    """
    print("\n--- CASA Measurement Conflict Validation ---")

    df = data["casa"].copy()

    df["average_monthly_balance_numeric"] = pd.to_numeric(
        df["average_monthly_balance"],
        errors="coerce",
    )

    grouped = df.groupby(
        ["account_id", "measurement_month"],
        dropna=False,
    )

    conflicts = []

    for (account_id, measurement_month), group in grouped:
        distinct_event_ids = group[
            "acquisition_event_id"
        ].nunique()

        distinct_amb_values = group[
            "average_monthly_balance_numeric"
        ].nunique(dropna=True)

        if distinct_event_ids > 1 and distinct_amb_values > 1:
            conflicts.append(
                f"{account_id}/{measurement_month}"
            )

    add_issue(
        "CASA_AMB_MEASUREMENT_CONFLICT",
        "casa",
        len(conflicts),
        conflicts,
    )


def validate_invoice_business_key(data):
    """Invoice numbers must be unique within a partner."""
    print("\n--- Invoice Business Key Validation ---")

    df = data["invoices"]

    duplicate_mask = df.duplicated(
        subset=["partner_id", "invoice_number"],
        keep=False,
    )

    duplicate_keys = (
        df.loc[
            duplicate_mask,
            ["partner_id", "invoice_number"],
        ]
        .drop_duplicates()
    )

    add_issue(
        "DUPLICATE_PARTNER_INVOICE_NUMBER",
        "invoices",
        len(duplicate_keys),
        duplicate_keys.to_dict("records"),
    )


def print_report(data):
    """Print dataset counts and validation results."""
    print("\n" + "=" * 70)
    print("SOURCE DATA INTEGRITY VALIDATION")
    print("=" * 70)

    print("\n--- Dataset Record Counts ---")

    total_records = 0

    for dataset, df in data.items():
        print(f"{DATASETS[dataset]:35} {len(df):>6}")
        total_records += len(df)

    print(f"\nTotal source records: {total_records}")

    print("\n--- Validation Results ---")

    if not issues:
        print("All source integrity checks passed.")
        print("\nNo referential-integrity or business-key issues found.")
        return True

    total_failures = sum(issue["count"] for issue in issues)

    for issue in issues:
        print(
            f"\n[FAIL] {issue['check']} | "
            f"Dataset: {issue['dataset']} | "
            f"Count: {issue['count']}"
        )
        print(f"       Samples: {issue['samples']}")

    print("\n" + "-" * 70)
    print(f"Failed validation checks: {len(issues)}")
    print(f"Total failure occurrences: {total_failures}")
    print("Source integrity validation FAILED.")
    print("-" * 70)

    return False


def main():
    print("Loading generated source datasets...")
    print(f"Data directory: {DATA_DIR}")

    data = load_datasets()

    # Check primary keys before using datasets as reference parents.
    validate_primary_keys(data)

    validate_foreign_keys(data)
    validate_rule_applicability(data)
    validate_product_categories(data)
    validate_adjustment_references(data)
    validate_casa_measurement_conflicts(data)
    validate_invoice_business_key(data)

    passed = print_report(data)

    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()