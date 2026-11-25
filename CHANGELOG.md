# Changelog

All notable changes to this project are documented in this file.

This project follows a simple versioning convention to track significant documentation and implementation milestones.

---

## [2.3] - 2026-11-25

### Added
- Created the Synthetic Source Data Dictionary covering all 11 source datasets.
- Defined dataset grains, primary keys, foreign keys, column data types, nullability and validation rules.
- Documented historical agreement and KYC handling, effective-dated rate cards, incentive slabs, configurable tax rules, adjustments and partner invoice structures.
- Established data-quality rules for duplicate events, referential integrity, conflicting records and financial adjustments.
- Finalized `docs/02_data_dictionary.md` as Version 1.0.

### Objective
Establish a clear source-data foundation and validated schema definitions before designing dataset relationships and generating synthetic data.

--- 

## [2.2] - 2026-11-24

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

## [2.1] - 2026-11-24

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

## [2.0] - 2026-11-24

### Updated
- Enhanced the initial Business Requirements Document.
- Improved business requirements, project objectives, scope, assumptions and constraints.
- Strengthened the overall documentation structure and clarity.

### Objective
Improve the completeness and engineering relevance of the business requirements documentation.

---

## [1.0] - 2026-11-24

### Added
- Created the initial Business Requirements Document.
- Established the project background, business problem, objectives and scope.
- Defined the initial simulated banking payout business scenario.

### Objective
Establish the foundational business requirements for the Banking Payout Data Engineering project.