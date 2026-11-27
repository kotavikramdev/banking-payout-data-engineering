# Changelog

All notable changes to this project are documented in this file.

This project follows a simple versioning convention to track significant documentation and implementation milestones.

---

## [Phase 2B — Bronze Layer Initial Ingestion] — 2026-11-27

### Added
- Created the Databricks notebook `notebooks/bronze/01_bronze_source_ingestion.ipynb`.
- Implemented initial ingestion of all 11 synthetic source CSV datasets into managed Delta tables in the `banking_payout.bronze` schema.
- Added ingestion metadata columns:
  - `source_file_name`
  - `ingestion_timestamp`
  - `batch_id`

### Validated
- Successfully ingested all 11 source datasets, totaling **3,754 records**.
- Verified expected record counts for every Bronze table.
- Validated source column schemas and ingestion metadata.
- Confirmed all 11 datasets passed validation with zero failures.

### Platform
- Databricks Free Edition
- PySpark
- Delta Lake
- Unity Catalog

---

## [Phase 2A — Source Integration Readiness] — 2026-11-27

### Added

**Component:** Source Data Validation  
**Status:** Completed

- Added `scripts/data_validation/validate_source_integrity.py` for cross-dataset validation of all 11 generated source datasets.
- Validated primary-key uniqueness and non-null constraints.
- Validated mandatory and conditional foreign-key references.
- Validated partner-rule applicability and product-category constraints.
- Validated polymorphic adjustment references against disbursement and CASA source events, including partner/product consistency.
- Checked for conflicting CASA account-month AMB measurements.
- Checked partner-scoped invoice business-key uniqueness.

### Validation
- Datasets checked: 11
- Total records checked: 3,754
- Result: All source integrity checks passed.
- Data corrections required: None identified by this validator.

### Next 
Begin Bronze-layer ingestion design and implementation.

--- 

## [Phase 1 — Source Data Generation Complete] — 2026-11-27

### Added
- Generated all 11 synthetic source datasets as defined by the project source data dictionary.
- Added independent Python generation scripts for the source datasets.
- Used centralized project configuration for record counts, random seed, transaction dates, currency, and output paths.
- Generated 3,754 source records across partner, product, agreement, KYC, rate-card, incentive, transaction, tax, adjustment, and invoice datasets.
- Exported generated datasets to `data/generated/` as CSV files.

### Validation
- Completed dataset-level schema and record-count validations.
- Validated primary keys, required fields, allowed values, and applicable date/timestamp rules.
- Validated foreign-key references and business constraints where applicable during individual dataset generation.
- Validated financial reconciliation for partner invoices, including taxable amount + GST = total invoice amount.
- Confirmed all 11 dataset generators completed successfully.

### Outcome
- Phase 1 source data generation is complete.
- Generated source datasets are ready for cross-dataset integration checks and subsequent Bronze-layer ingestion.

### Next
- Begin Phase 2: source dataset integration readiness and data pipeline foundation.
- Implement Bronze ingestion, followed by Silver data quality and business transformations, and Gold dimensional and financial models.

---

## [2.4] — 2026-11-25

### Added
- Created and finalized `docs/03_data_relationships.md` (Version 1.0).
- Documented source dataset relationships, cardinalities and dependency order.
- Defined referential integrity, effective dating, rule precedence and historical validity checks.
- Established orphan, duplicate and conflicting record handling, including quarantine and reprocessing principles.
- Documented design assumptions covering source data, financial processing and technology constraints.

### Objective
Complete the source data relationship and dependency design before beginning synthetic data generation and implementation.

---

## [2.3] — 2026-11-25

### Added
- Created the Synthetic Source Data Dictionary covering all 11 source datasets.
- Defined dataset grains, primary keys, foreign keys, column data types, nullability and validation rules.
- Documented historical agreement and KYC handling, effective-dated rate cards, incentive slabs, configurable tax rules, adjustments and partner invoice structures.
- Established data-quality rules for duplicate events, referential integrity, conflicting records and financial adjustments.
- Finalized `docs/02_data_dictionary.md` as Version 1.0.

### Objective
Establish a clear source-data foundation and validated schema definitions before designing dataset relationships and generating synthetic data.

--- 

## [2.2] — 2026-11-24

### Updated

- Updated author metadata to Kota Vikramdev.
- Aligned the project scope to 6 products and 4 channels.
- Defined key table names and table grains.
- Added configurable tax rules and effective-date logic.
- Documented CASA calculation methods and carry-forward formulas.
- Defined signed ledger conventions and reversal policies.
- Introduced deterministic idempotency key design with rule versioning.
- Added historical KYC guidance and slab boundary definitions.
- Improved reconciliation rules between summary and ledger data.
- Strengthened auditability, traceability, and data governance controls.

### Objective

Freeze the project scope and establish a stable baseline for solution design, data modeling, and implementation.

---

## [2.1] — 2026-11-24

### Updated
- Explicitly established the project as a single-handed, self-learning Data Engineering portfolio project.
- Added a prominent non-affiliation disclaimer clarifying that the project does not represent, reference, or derive requirements from any real banking institution.
- Incorporated individual technical learning objectives alongside simulated business requirements.
- Clarified that business and engineering responsibilities are simulated and performed independently by the project developer.
- Retained engineering complexity, including:
  - Payout eligibility and dual-gate validation.
  - Financial reconciliation and mathematical calculations.
  - Clawback processing scenarios.
  - Slowly Changing Dimensions (SCD).
  - Multi-source data ingestion.
  - Data quality validation and quarantine handling.
  - Exception management.

### Objective
Establish a realistic but entirely fictional banking payout scenario that demonstrates end-to-end Data Engineering skills while maintaining a clear self-learning and portfolio context.

---

## [2.0] — 2026-11-24

### Updated
- Enhanced the initial Business Requirements Document.
- Improved business requirements, project objectives, scope, assumptions and constraints.
- Strengthened the overall documentation structure and clarity.

### Objective
Improve the completeness and engineering relevance of the business requirements documentation.

---

## [1.0] — 2026-11-24

### Added
- Created the initial Business Requirements Document.
- Established the project background, business problem, objectives and scope.
- Defined the initial simulated banking payout business scenario.

### Objective
Establish the foundational business requirements for the Banking Payout Data Engineering project.