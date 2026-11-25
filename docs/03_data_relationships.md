# Data Relationships and Dependency Design

## Document Information

| Attribute | Details |
|---|---|
| Document Name | Data Relationships and Dependency Design |
| Version | 1.0 |
| Project | Banking Partner Commission and Payout Data Engineering Solution |
| Last Updated | 2026-11-25 |

---

## 1. Purpose

This document defines the relationships, dependencies, and referential-integrity rules between the synthetic source datasets used in the Banking Partner Commission and Payout Data Engineering Solution.

It establishes how source datasets are connected, how records are validated, and how data dependencies are managed across source generation, ingestion and downstream transformation.

## 2. Scope

This document covers:

- Primary-key and foreign-key relationships.

- Relationship cardinalities.

- Dataset dependency order.

- Referential-integrity validation.

- Effective-dated relationships.

- Orphan, duplicate, and conflicting-record handling.

## 3. Dataset Relationship Matrix

This section defines the parent-child relationships between the source datasets, including primary keys, foreign keys, and conditional business references.

### 3.1 Partner-Related Relationships

| Parent Dataset | Child Dataset | Parent Primary Key | Child Foreign Key | Cardinality |
|---|---|---|---|---|
| src_partner_master | src_partner_agreements | partner_id | partner_id | One-to-Many (1:N) |
| src_partner_master | src_partner_kyc | partner_id | partner_id | One-to-Many (1:N) |
| src_partner_master | src_disbursements | partner_id | partner_id | One-to-Many (1:N) |
| src_partner_master | src_casa_acquisitions | partner_id | partner_id | One-to-Many (1:N) |
| src_partner_master | src_partner_invoices | partner_id | partner_id | One-to-Many (1:N) |

### 3.2 Product-Related Relationships

| Parent Dataset | Child Dataset | Parent Primary Key | Child Foreign Key | Cardinality |
|---|---|---|---|---|
| src_product_master | src_disbursements | product_id | product_id | One-to-Many (1:N) |
| src_product_master | src_casa_acquisitions | product_id | product_id | One-to-Many (1:N) |
| src_product_master | src_rate_cards | product_id | product_id | One-to-Many (1:N) |
| src_product_master | src_incentive_slabs | product_id | product_id | One-to-Many (1:N) |

### 3.3 Conditional Rule Relationships

| Parent Dataset | Child Dataset | Reference Column | Relationship Rule |
|---|---|---|---|
| src_partner_master | src_rate_cards | partner_id | Optional partner-specific reference |
| src_partner_master | src_incentive_slabs | partner_id | Optional partner-specific reference |

For rate cards and incentive slabs, applicability is determined using either a specific partner_id or a partner_type.

Exactly one of partner_id or partner_type must be populated for each applicable rule record.

Partner-specific rules take precedence over partner-type rules, subject to effective-date validity and ambiguity checks.

### 3.4 Adjustment Relationships

The src_adjustments dataset references an original source event using original_source_event_type and original_source_event_id.

| Original Source Event Type | Parent Dataset | Parent Primary Key | Child Reference |
|---|---|---|---|
| DISBURSEMENT | src_disbursements | disbursement_event_id | original_source_event_id |
| CASA_ACQUISITION | src_casa_acquisitions | acquisition_event_id | original_source_event_id |

The event reference must be validated against the parent dataset specified by original_source_event_type.

This is a conditional reference and not a conventional single-column foreign key.

### 3.5 Tax Rule Applicability

The src_tax_rules dataset uses partner_type to determine rule applicability.

- A populated partner_type identifies a partner category-specific rule.

- A NULL partner_type identifies a general rule applicable to all supported partner categories.

- A category-specific rule takes precedence over a general rule.

- Multiple applicable rules at the same precedence level must be treated as a data-quality exception.

### 3.6 Relationship Design Principles

- Every child record referencing a parent must contain a valid parent identifier.

- Primary keys must be unique and non-null.

- Foreign-key references must be validated before downstream financial calculations.

- Conditional references must be validated using their associated type or applicability attributes.

- Historical agreement and KYC relationships must be evaluated using effective dates rather than only current status.

- Invalid or unresolved references must be recorded as data-quality exceptions or quarantined according to severity.

## 4. Relationship Cardinality

Relationship cardinality defines the number of records that can be associated between parent and child datasets.

### 4.1 One-to-Many (1:N) Relationships

The project primarily uses One-to-Many relationships.

| Parent Dataset | Child Dataset | Parent Perspective | Child Perspective |
|---|---|---|---|
| src_partner_master | src_partner_agreements | One partner can have multiple agreements | Each agreement belongs to one partner |
| src_partner_master | src_partner_kyc | One partner can have multiple KYC records | Each KYC record belongs to one partner |
| src_partner_master | src_disbursements | One partner can have multiple disbursement events | Each disbursement references one partner |
| src_partner_master | src_casa_acquisitions | One partner can have multiple CASA acquisition records | Each CASA record references one partner |
| src_partner_master | src_partner_invoices | One partner can have multiple invoices | Each invoice belongs to one partner |
| src_product_master | src_disbursements | One product can have multiple disbursement events | Each disbursement references one product |
| src_product_master | src_casa_acquisitions | One product can have multiple CASA records | Each CASA record references one product |
| src_product_master | src_rate_cards | One product can have multiple rate-card versions | Each rate card references one product |
| src_product_master | src_incentive_slabs | One product can have multiple incentive-slab records | Each incentive-slab record references one product |

### 4.2 Conditional Relationships

Some relationships depend on business attributes rather than a single conventional foreign key.

| Dataset | Relationship | Cardinality / Rule |
|---|---|---|
| src_partner_master and src_rate_cards | Partner-specific rate applicability | One partner can have multiple applicable rate-card records over time |
| src_partner_master and src_incentive_slabs | Partner-specific incentive applicability | One partner can have multiple applicable incentive-slab records |
| src_disbursements / src_casa_acquisitions and src_adjustments | Original event reference | One source event can have multiple adjustment records, subject to adjustment rules |

For rate cards and incentive slabs, partner-specific applicability is established through partner_id. General applicability is established through partner_type.

For adjustments, the original event is identified using original_source_event_type and original_source_event_id.

### 4.3 One-to-One (1:1) Relationships

No mandatory One-to-One relationships are currently defined between the 11 source datasets.

The project will not introduce artificial One-to-One relationships without a valid business requirement.

### 4.4 Many-to-Many (N:M) Relationships

At the business level, partners can work with multiple products, and products can be associated with multiple partners.

This creates a conceptual Many-to-Many relationship.

The current source design resolves this through transactional and rule datasets such as:

- src_disbursements

- src_rate_cards

- src_incentive_slabs

A separate partner-product bridge dataset is not required within the current project scope.

### 4.5 Optional and Mandatory Participation

Parent records may exist without corresponding child records.

Examples:

- A partner may exist without any disbursement events.

- A product may exist without an active rate card.

- A partner may not yet have submitted an invoice.

However, when a child record is present, its mandatory foreign-key references must resolve to valid parent records.

Conditional references must satisfy their corresponding business validation rules.

### 4.6 Cardinality Validation Principles

- Parent primary keys must be unique and non-null.

- Mandatory child foreign keys must be populated.

- Each mandatory foreign-key reference must resolve to exactly one parent record.

- Multiple child records may reference the same parent.

- Historical records must be retained where required.

- Conditional relationships must be validated using their associated event type or rule applicability attributes.

## 5. Dataset Dependency Order

Dataset dependency order defines the sequence in which source datasets are generated, validated, and processed to ensure that required parent records and reference data are available.

The dependency design helps prevent orphan records and ensures that downstream transformations use valid reference data.

### 5.1 Dataset Dependency Classification

#### Level 1: Foundation Datasets

These datasets do not depend on other source datasets.

- src_partner_master

- src_product_master

#### Level 2: Dependent Master and Rule Datasets

These datasets depend on foundation datasets or define configuration rules for downstream processing.

- src_partner_agreements

- src_partner_kyc

- src_rate_cards

- src_incentive_slabs

- src_tax_rules

#### Level 3: Transaction and Operational Datasets

These datasets contain business events or supporting operational records.

- src_disbursements

- src_casa_acquisitions

- src_adjustments

- src_partner_invoices

### 5.2 Dataset Dependency Matrix

| Dataset | Depends On | Dependency Reason |
|---|---|---|
| src_partner_master | None | Foundation dataset |
| src_product_master | None | Foundation dataset |
| src_partner_agreements | src_partner_master | Requires a valid partner reference |
| src_partner_kyc | src_partner_master | Requires a valid partner reference |
| src_rate_cards | src_product_master; optionally src_partner_master | Requires a valid product and, when partner-specific, a valid partner |
| src_incentive_slabs | src_product_master; optionally src_partner_master | Requires a valid product and, when partner-specific, a valid partner |
| src_tax_rules | None | Uses partner_type as a rule applicability attribute |
| src_disbursements | src_partner_master, src_product_master | Requires valid partner and product references |
| src_casa_acquisitions | src_partner_master, src_product_master | Requires valid partner and CASA product references |
| src_adjustments | src_partner_master, src_product_master, src_disbursements or src_casa_acquisitions | Requires valid partner, product and original source event references |
| src_partner_invoices | src_partner_master | Requires a valid partner reference |

### 5.3 Recommended Dataset Generation Order

The following sequence will be used for synthetic data generation:

1\. src_partner_master

2\. src_product_master

3\. src_partner_agreements

4\. src_partner_kyc

5\. src_rate_cards

6\. src_incentive_slabs

7\. src_tax_rules

8\. src_disbursements

9\. src_casa_acquisitions

10\. src_adjustments

11\. src_partner_invoices

Independent datasets may be generated within the same execution stage where their dependencies permit.

### 5.4 Generation, Ingestion and Transformation Order

Generation, ingestion and transformation are separate pipeline activities.

- Generation order determines when synthetic source records are created.

- Ingestion order determines when source datasets are read and loaded into the Bronze layer.

- Transformation order determines when datasets are validated, joined and processed for downstream consumption.

Raw Bronze ingestion may preserve records before all parent datasets are available.

Referential-integrity validation will be performed at the appropriate validation stage, primarily during Silver processing, once the required reference datasets are available.

### 5.5 Dependency Management Principles

- Foundation datasets must be available before generating dependent records.

- Every mandatory foreign-key reference must resolve to a valid parent record during validation.

- Partner-specific rules must reference an existing partner.

- Adjustments must reference an existing original source event in the dataset identified by original_source_event_type.

- CASA acquisition records must reference a valid CASA product.

- Independent rule datasets may be generated without unnecessary dependencies.

- Circular dependencies must be avoided.

- Failed dependency validation must be recorded and handled according to the data-quality and quarantine rules.

## 6. Referential Integrity Rules

### 6.1 Purpose

Referential integrity ensures that records referencing another dataset point to valid and existing parent records.

For this project, every mandatory foreign key must resolve to exactly one valid parent record. Conditional references and polymorphic references must be validated according to their defined business rules.

These validations will primarily be performed during the Silver-layer data-quality process. Raw records may first be retained in Bronze without requiring all parent datasets to be available at ingestion time.

### 6.2 Referential Integrity Validation Matrix

| Child Dataset | Reference Field | Parent Dataset | Parent Field | Validation Rule |
|---|---|---|---|---|
| src_partner_agreements | partner_id | src_partner_master | partner_id | Mandatory; must resolve to an existing partner. |
| src_partner_kyc | partner_id | src_partner_master | partner_id | Mandatory; must resolve to an existing partner. |
| src_disbursements | partner_id | src_partner_master | partner_id | Mandatory; must resolve to an existing partner. |
| src_disbursements | product_id | src_product_master | product_id | Mandatory; must resolve to an existing product. |
| src_casa_acquisitions | partner_id | src_partner_master | partner_id | Mandatory; must resolve to an existing partner. |
| src_casa_acquisitions | product_id | src_product_master | product_id | Mandatory; must resolve to an existing product. Product must be CASA category. |
| src_rate_cards | product_id | src_product_master | product_id | Mandatory; must resolve to an existing product. |
| src_rate_cards | partner_id | src_partner_master | partner_id | Conditional; validate when populated. |
| src_incentive_slabs | product_id | src_product_master | product_id | Mandatory; must resolve to an existing product. |
| src_incentive_slabs | partner_id | src_partner_master | partner_id | Conditional; validate when populated. |
| src_adjustments | partner_id | src_partner_master | partner_id | Mandatory; must resolve to an existing partner. |
| src_adjustments | product_id | src_product_master | product_id | Mandatory; must resolve to an existing product. |
| src_adjustments | original_source_event_id | Source transaction dataset | Event ID | Resolve against the dataset identified by original_source_event_type. |
| src_partner_invoices | partner_id | src_partner_master | partner_id | Mandatory; must resolve to an existing partner. |

****Additional validation for conditional references:****

- In `src_rate_cards` and `src_incentive_slabs`, exactly one of `partner_id` or `partner_type` must be populated.

- When `partner_id` is populated, it must exist in `src_partner_master`.

- When `partner_type` is populated, it must match an allowed partner type.

- Partner-specific rules take precedence over partner-type rules, as defined in the Business Requirements Document.

### 6.3 Polymorphic Reference Validation — Adjustments

The `src_adjustments` dataset contains a polymorphic reference because an adjustment can refer to either a loan disbursement or a CASA acquisition.

Validation must use `original_source_event_type` to identify the correct source dataset.

| original_source_event_type | Dataset to Validate Against | Reference Field |
|---|---|---|
| DISBURSEMENT | src_disbursements | disbursement_event_id |
| CASA_ACQUISITION | src_casa_acquisitions | acquisition_event_id |

Rules:

1\. `original_source_event_type` must contain one of the two supported values.

2\. `original_source_event_id` must exist in the corresponding source dataset.

3\. The referenced event must belong to the same `partner_id` and `product_id` recorded in the adjustment.

4\. An invalid event type or unresolved event reference must be recorded as a data-quality exception.

5\. An adjustment must not be posted to the payout ledger until its source event reference is validated and its approval status is APPROVED.

### 6.4 Product-Specific Referential Validation

A valid product ID alone is not sufficient for every transaction. Additional business validation is required.

| Dataset | Additional Rule |
|---|---|
| src_disbursements | Referenced product must belong to the LOAN category. |
| src_casa_acquisitions | Referenced product must belong to the CASA category. |
| src_rate_cards | Commission mode must be compatible with the referenced product category. |
| src_incentive_slabs | Referenced product must be valid for the applicable incentive rule. |

For example, a CASA acquisition referencing `PROD001` (New Car Loan) has a valid product foreign key if that product exists, but it violates the product-category rule.

This should be treated as a business data-quality failure.

### 6.5 Parent Key and Foreign Key Validation

The following rules apply across the source datasets:

****Parent key rules:****

- Every primary key must be populated.

- Every primary key must be unique within its dataset.

- Parent records with missing or duplicate primary keys must not be treated as valid reference records until the issue is resolved.

****Mandatory foreign key rules:****

- Mandatory foreign keys must not be NULL or blank.

- Every mandatory foreign key must resolve to exactly one valid parent record.

- Unresolved references must not silently pass validation.

****Conditional foreign key rules:****

- Optional references must be validated whenever populated.

- Conditional applicability rules must also be checked.

- A NULL value is acceptable only when permitted by the dataset's business rules.

### 6.6 Handling Referential Integrity Failures

| Scenario | Example | Expected Handling |
|---|---|---|
| Missing mandatory foreign key | Disbursement has NULL partner_id. | Quarantine the affected record and create an exception. |
| Unresolved parent reference | Disbursement references P999, which does not exist. | Quarantine the affected record and create an exception. |
| Invalid product category | CASA acquisition references a LOAN product. | Quarantine the affected record and create an exception. |
| Invalid conditional reference | Rate card references a non-existent partner_id. | Quarantine the affected record and create an exception. |
| Invalid polymorphic reference | Adjustment references a disbursement ID that does not exist. | Quarantine the affected record and create an exception. |
| Parent primary-key duplication | Two partner records have the same partner_id. | Flag the parent data-quality issue; do not use an ambiguous parent reference. |
| Valid parent without child records | Partner exists but has no disbursements. | Accept; this is not a referential integrity failure. |

### 6.7 Validation Timing and Processing Approach

Referential integrity checks will be performed primarily during Silver-layer processing.

The intended approach is:

1\. Preserve incoming source records in the Bronze layer.

2\. Load and validate parent datasets such as partner and product masters.

3\. Validate mandatory and conditional foreign keys in dependent datasets.

4\. Apply product-category and polymorphic-reference checks.

5\. Separate valid records from invalid records.

6\. Record invalid records in the exception dataset with an appropriate exception reason.

7\. Allow only validated records to proceed to downstream business transformations.

A missing parent record should not automatically result in permanent rejection if the parent dataset has not yet arrived. The pipeline should first ensure that the relevant parent data has been loaded and the validation window is complete.

### 6.8 Design Principles

- Never silently discard records that fail referential integrity checks.

- Preserve raw source records in Bronze for traceability.

- Quarantine invalid records rather than allowing them into financial calculations.

- Record the affected dataset, record identifier, validation rule and exception reason.

- Do not confuse a missing child record with an invalid child reference.

- Revalidate quarantined records when missing or corrected parent data becomes available.

- Ensure only validated transaction and adjustment records are considered for payout processing.

## 7. Effective-Dated Relationships

### 7.1 Purpose

Effective dating maintains historical versions of business records according to their validity periods.

In this project, effective dating ensures that historical transactions use the agreements, KYC statuses, commission rates, incentive rules and tax rules applicable at the relevant business date.

Existing historical records must not be overwritten merely because a new version becomes effective.

### 7.2 Effective-Date Convention

All effective-dated source datasets follow these conventions:

- effective_from is inclusive.

- effective_to is exclusive.

- NULL effective_to represents an open-ended validity period.

- effective_to, when populated, must be greater than effective_from.

A record is valid for a transaction date when:

effective_from <= transaction_date

AND

(transaction_date < effective_to OR effective_to IS NULL)

This convention avoids ambiguity at period boundaries.

### 7.3 Effective-Dated Datasets

| Dataset | Effective-Date Purpose | Applicable Business Date |
|---|---|---|
| src_partner_agreements | Agreement validity | Disbursement date |
| src_partner_kyc | KYC status validity | Relevant transaction or eligibility date, as defined by the business rule |
| src_rate_cards | Commission rule validity | Disbursement date or CASA measurement date, as applicable |
| src_incentive_slabs | Incentive rule validity | Applicable incentive calculation date or measurement period |
| src_tax_rules | Tax rule validity | Date selected through tax_date_basis: TRANSACTION_DATE, INVOICE_DATE or PAYOUT_DATE |

The applicable date for each dataset must be explicitly defined during business-rule implementation.

### 7.4 Historical Record Selection

The pipeline must select the record whose effective period covers the relevant business date.

The selection process includes:

1\. Match the relevant business key, such as partner_id or product_id.

2\. Match the applicable product, partner type or other rule dimensions.

3\. Check that the rule or record is active and otherwise eligible.

4\. Apply the effective-date condition.

5\. Apply the defined rule-precedence logic where applicable.

6\. Confirm that exactly one applicable record remains at the selected precedence.

The latest record must not automatically be selected in place of the historically valid record.

### 7.5 Effective-Date Overlap Validation

Overlapping effective periods must be checked before historical record selection.

Rules:

- Partner agreement periods must not overlap for the same partner.

- KYC status periods must not overlap for the same partner.

- Rate card periods must not overlap for identical applicability dimensions and the same rule precedence.

- Effective periods for competing incentive-rule definitions must not overlap for identical applicability dimensions and the same rule precedence.
- Different tiers within the same calculation_group_id may share the same effective period; their monetary threshold ranges must be non-overlapping, using the defined lower-inclusive and upper-exclusive boundaries.

- Tax rule periods must not overlap for the same applicability dimensions and precedence.

- Partner-specific and partner-type rules may overlap when the defined precedence resolves the applicability.

- Multiple equally applicable rules at the same precedence must result in a data-quality exception.

For incentive slabs, validate both effective-period applicability and tier threshold ranges within the relevant calculation group. Adjacent ranges that meet at a boundary are valid under the lower-inclusive, upper-exclusive convention.

Overlapping competing records must not be resolved by arbitrarily selecting the latest record.

### 7.6 Effective-Date Gap Handling

A gap exists when no record covers a particular business date between otherwise defined validity periods.

Gap handling depends on the dataset and business process:

| Dataset | Gap Handling |
|---|---|
| Partner agreements | Transaction must fail agreement eligibility validation if no valid agreement exists. |
| Partner KYC | Apply the configured KYC eligibility policy; unresolved or missing status must not be treated as verified. |
| Rate cards | Do not calculate commission without an applicable rate card; create an exception. |
| Incentive slabs | Apply the defined incentive policy; do not invent or extrapolate a slab. |
| Tax rules | Do not silently assume a tax rate; create an exception for unresolved applicable tax rules. |

A gap is not necessarily an invalid source record, but it may prevent a transaction from proceeding.

### 7.7 Effective Dating and Rule Precedence

Where multiple rules could apply, effective-date validation must be combined with rule-precedence logic.

For rate cards and incentive slabs:

- Partner-specific rules take precedence over partner-type rules.

- A partner-specific rule must reference an existing partner.

- A partner-type rule must use a supported partner type.

- Multiple applicable rules at the same precedence must result in an exception.

- The applicable rule must also cover the relevant business date.

For tax rules:

- Partner-type-specific rules take precedence over general rules where both are applicable.

- A general rule is represented by NULL partner_type.

- Multiple applicable rules at the same precedence must result in an exception.

### 7.8 Effective Dating and Historical Reproducibility

Historical payout calculations must retain sufficient rule and source references to reproduce the original financial result.

The payout processing design should preserve:

- Source transaction or acquisition event identifier.

- Selected agreement or eligibility reference, where applicable.

- Selected rate card identifier and rule version.

- Selected incentive slab identifier and rule version, where applicable.

- Selected tax rule identifier and rule version, where applicable.

- Relevant business date used for each effective-date lookup.

A change in a business rule must not silently overwrite previously posted financial results. Corrections must follow the reversal and replacement approach defined in the BRD.

### 7.9 Effective Dating and SCD Type 2

Effective dating and Slowly Changing Dimension Type 2 (SCD Type 2) are related concepts but serve different purposes.

- Effective dating represents the business validity of source agreements, KYC statuses and commission rules.

- SCD Type 2 preserves historical versions of warehouse dimension records.

The dim_channel_partner dimension will use SCD Type 2 to retain historical partner attribute versions.

Business effective dates and warehouse history dates must not be assumed to represent the same concept.

### 7.10 Design Principles

- Never overwrite historical effective-dated records when a new version is introduced.

- Use inclusive start dates and exclusive end dates consistently.

- Validate effective_from and effective_to before processing.

- Detect overlaps before selecting applicable rules.

- Treat gaps according to the relevant business process.

- Never select a rule merely because it is the latest available record.

- Retain rule identifiers and versions for financial reproducibility.

- Apply rule precedence only after identifying records valid for the relevant business date.

## 8. Orphan, Duplicate and Conflicting Record Handling

### 8.1 Purpose

This section defines how the pipeline identifies and handles orphan records, duplicate records and conflicting records.

These checks protect the accuracy, completeness and financial integrity of downstream commission and payout calculations.

Invalid records must be retained for traceability and must not silently enter financial processing.

### 8.2 Orphan Record Handling

An orphan record is a child record that references a parent or source event that cannot be resolved.

Examples:

- A disbursement references a partner_id that does not exist in src_partner_master.

- A CASA acquisition references a product_id that does not exist in src_product_master.

- An adjustment references an original event that cannot be found in the dataset identified by original_source_event_type.

Handling rules:

1\. Preserve the raw record in Bronze.

2\. Identify the unresolved reference during Silver validation.

3\. Create a data-quality exception with the affected dataset and record identifier.

4\. Quarantine the affected record.

5\. Do not allow the record into downstream financial calculations.

6\. Revalidate the record when the missing parent or source event becomes available.

An orphan record may be caused by delayed parent ingestion and is not necessarily permanently invalid.

### 8.3 Duplicate Record Handling

A duplicate occurs when the same source record or business event is received more than once.

#### Exact duplicates

Exact duplicates have the same business event identifier and identical relevant business attributes.

Handling rules:

- Identify duplicates using the dataset's defined primary or business event key.

- Retain one canonical record for downstream processing.

- Preserve duplicate occurrence information for auditability.

- Ensure duplicate deliveries do not create additional financial effects.

#### Legitimate repeated business events

Multiple records for the same loan or account are not automatically duplicates.

For example, multiple partial disbursements against the same loan are valid when each has a distinct disbursement_event_id and a valid disbursement_sequence.

Deduplication must use the correct event identifier and must not rely only on loan_id or account_id.

Note : Duplicate occurrences are tracked for auditability, but aren't automatically financial exceptions.

### 8.4 Conflicting Record Handling

A conflict occurs when the same business identifier appears with different relevant business attributes.

Example: the same disbursement_event_id is received with different disbursed_amount values.

Handling rules:

1\. Identify the conflicting business identifier.

2\. Preserve the conflicting source records in Bronze.

3\. Create a data-quality exception.

4\. Quarantine the affected event.

5\. Do not select the latest, highest or otherwise preferred value without an authoritative business rule.

6\. Do not combine conflicting records or create financial effects from them.

7\. Reprocess only after an authoritative correction or approved resolution.

### 8.5 Dataset-Specific Duplicate and Conflict Rules

| Dataset | Validation and Handling |
|---|---|
| src_partner_master | partner_id must be unique. Conflicting partner attributes require investigation. |
| src_partner_agreements | agreement_id must be unique. Overlapping agreement periods for the same partner must be flagged. |
| src_partner_kyc | kyc_record_id must be unique. Overlapping KYC status periods for the same partner must be flagged. |
| src_product_master | product_id must be unique. Conflicting product definitions require investigation. |
| src_disbursements | Exact duplicate disbursement_event_id records are deduplicated. Conflicting attributes for the same event ID are quarantined. |
| src_casa_acquisitions | Exact duplicate acquisition_event_id records are deduplicated. Conflicting AMB records for the same account_id and measurement_month require authoritative resolution. |
| src_rate_cards | rate_card_id must be unique. Overlapping equally applicable rules must be flagged. |
| src_incentive_slabs | slab_id must be unique. Duplicate or overlapping applicable slab definitions must be validated. |
| src_tax_rules | tax_rule_id must be unique. Overlapping equally applicable tax rules must be flagged. |
| src_adjustments | adjustment_id must be unique. Duplicate adjustment deliveries must not create repeated financial effects. Conflicting adjustment attributes require investigation. |
| src_partner_invoices | invoice_id must be unique. Repeated invoice numbers must be checked within the applicable business scope (at minimum, partner_id and invoice_number); conflicting invoice details must be investigated. |

### 8.6 CASA Account and Measurement Conflict Handling

The CASA acquisition dataset requires an additional business-level uniqueness check.

The expected commission measurement grain is one authoritative AMB record per account_id and measurement_month.

Rules:

- Multiple records for the same account in different measurement months are legitimate.

- Exact duplicate acquisition events must not create duplicate financial effects.

- Different acquisition_event_id values with different AMB values for the same account_id and measurement_month must be treated as a business-level conflict until an authoritative record is established; they are not exact duplicate events.

- The pipeline must not arbitrarily select the highest or latest AMB.

- Unrelated account/month measurements may continue if they pass validation.

Note : Different acquisition event IDs with conflicting AMB values for the same account/month are business-level conflicts, not exact duplicates.

### 8.7 Quarantine and Reprocessing

The pipeline must maintain a controlled approach for invalid records.

For each quarantined record, retain sufficient information to support investigation and reprocessing.

At a minimum, the exception should identify:

- Source dataset.

- Source record or business event identifier.

- Batch identifier, where available.

- Validation rule or exception code.

- Exception description.

- Detection timestamp.

- Resolution or reprocessing status.

Quarantined records must not be permanently discarded.

After the underlying issue is corrected, the pipeline should revalidate the affected records and allow eligible records to proceed without creating duplicate financial effects.

### 8.8 Relationship Between Deduplication and Idempotency

Deduplication and idempotency are related but distinct controls.

- Deduplication prevents duplicate source records from being processed as separate business events.

- Idempotency ensures repeated processing of the same event does not create additional financial postings.

The project will implement the composite idempotency key defined in the BRD using:

source_event_id + posting_component + calculation_group_id + payout_cycle + rule_id + rule_version

Repeated processing with the same key and unchanged calculation inputs must not create an additional financial effect.

Changes to rules or source data after a financial posting must follow the reversal and replacement process defined in the BRD.

### 8.9 Design Principles

- Preserve raw source records in Bronze.

- Perform duplicate, conflict and relationship validations primarily in Silver.

- Do not silently discard invalid records.

- Do not confuse repeated business events with duplicate deliveries.

- Do not arbitrarily resolve conflicting financial data.

- Maintain traceability between source records, exceptions and downstream financial postings.

- Support controlled reprocessing after data correction.

- Ensure duplicate source events and repeated pipeline runs cannot create duplicate financial effects.

## 9. Design Assumptions

### 9.1 Purpose

This section documents the assumptions and implementation constraints used while designing the data relationships and dependency structure.

These assumptions provide a consistent foundation for synthetic data generation, source ingestion, data-quality validation and downstream business processing.

Any change to these assumptions must be reviewed against the Business Requirements Document and Source Data Dictionary.

### 9.2 Source Data Assumptions

- All source datasets follow the Source Data Dictionary.

- Each source dataset has a defined grain and primary key.

- Identifiers are represented as STRING values.

- Monetary amounts use DECIMAL(18,2).

- Commission and tax rates use DECIMAL(9,6).

- Dates follow ISO YYYY-MM-DD format.

- Timestamps follow ISO 8601 format with timezone information.

- INR is the reporting and transaction currency for this educational implementation.

- Source records contain sufficient attributes to identify and validate their business events.

- Source datasets are synthetic and do not represent actual banking customer or partner information.

### 9.3 Relationship Assumptions

- src_partner_master and src_product_master are foundational parent datasets.

- Mandatory foreign keys must resolve to valid parent records.

- Optional partner references in rate cards and incentive slabs follow the documented applicability rules.

- Adjustment source references are resolved using original_source_event_type.

- One partner may have multiple agreements, KYC records, disbursements, CASA acquisitions and invoices.

- One loan may have multiple legitimate partial disbursement events.

- One CASA account may have multiple acquisition or measurement records across different measurement months.

- Parent records are not required to have corresponding child records.

### 9.4 Historical Data Assumptions

- Effective-dated source records are retained rather than overwritten.

- Effective start dates are inclusive.

- Effective end dates are exclusive.

- NULL effective end dates represent open-ended validity.

- Historical business calculations use the relevant business date defined for each rule.

- Overlapping equally applicable rules must result in a data-quality exception.

- The pipeline must not automatically select the nearest or latest rule when no valid rule exists.

- The curated dim_channel_partner dimension uses SCD Type 2 to preserve historical partner attribute versions.

- Business effective dates and warehouse dimension history dates represent different concepts.

### 9.5 Data-Quality Assumptions

- Primary keys are expected to be unique and non-null within their respective datasets.

- Exact duplicate source deliveries can be identified using the defined business event identifiers.

- Conflicting records must not be resolved through arbitrary record selection.

- One authoritative AMB measurement is expected per account_id and measurement_month for commission calculation.

- Missing mandatory references must be quarantined.

- Raw source records are preserved in Bronze for traceability.

- Data-quality and referential integrity validations are performed primarily in Silver.

- Quarantined records may be revalidated after the underlying issue is corrected.

- Duplicate deliveries and legitimate repeated business events must be distinguished.

### 9.6 Financial Processing Assumptions

- Only validated and eligible source transactions proceed to commission calculation.

- Commission eligibility and payout release eligibility are separate business checks.

- Adjustments must reference valid original business events.

- Only approved adjustments are eligible for financial posting.

- Financial corrections follow the reversal and replacement approach rather than silently overwriting committed postings.

- Deduplication and idempotency controls prevent duplicate financial effects.

- Historical payout calculations retain references to applicable rule identifiers and versions.

- Financial calculations follow the signed ledger conventions and rounding rules defined in the BRD.

### 9.7 Technical and Implementation Assumptions

- Python and Pandas are used for synthetic data generation and initial validation.

- SQL is used for relational validation, modelling and reporting.

- PySpark and Spark SQL are used for data transformation and business processing.

- Delta Lake is used for Bronze, Silver and Gold storage.

- Databricks Free Edition is the primary cloud learning environment, subject to its supported capabilities and limitations.

- Local Python and SQLite alternatives are maintained where cloud capabilities are unavailable.

- Azure Data Factory and ADLS Gen2 are optional demonstrations and are not mandatory dependencies.

- No paid cloud services are required for the mandatory project implementation.

### 9.8 Scope and Governance Assumptions

- This is a self-learning and portfolio project.

- All business scenarios, partner information, customer references, transaction records and financial rules are hypothetical.

- The project is not affiliated with or representative of any actual bank or financial institution.

- Business rules and source schemas are governed by the BRD and Source Data Dictionary.

- Changes to business requirements, source schemas or design decisions must be documented and version-controlled.

- Implementation decisions must distinguish between actual functionality, simulated integrations and production recommendations.

### 9.9 Design Principles

- Maintain consistency with the BRD and Source Data Dictionary.

- Preserve historical business and financial information.

- Enforce referential integrity before downstream financial processing.

- Never silently discard invalid or conflicting source records.

- Avoid arbitrary rule selection or financial data correction.

- Ensure traceability from source events to downstream financial outputs.

- Design processing to support safe retries and controlled reprocessing.

- Keep the implementation within the project scope and available technology constraints.