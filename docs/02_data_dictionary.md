# Synthetic Source Data Dictionary

## 1. Document Information

| Attribute | Value |
|---|---|
| Project | Banking Partner Commission and Payout Data Engineering Solution |
| Document | Synthetic Source Data Dictionary |
| Version | 1.0 |
| Status | Synthetic Data Design Baseline |
| Purpose | Define source datasets, their grain, keys, data types and validation rules |

## 2. Source Dataset Inventory

| Dataset Name | Business Purpose | Dataset Grain | Primary Key |
|---|---|---|---|
| src_partner_master | Partner identity and profile | One row per partner | partner_id |
| src_partner_agreements | Contractual and empanelment history | One row per agreement/version | agreement_id |
| src_partner_kyc | Historical KYC status | One row per KYC status record | kyc_record_id |
| src_product_master | Product definitions | One row per product | product_id |
| src_disbursements | Loan disbursement events | One row per disbursement event | disbursement_event_id |
| src_casa_acquisitions | CASA acquisition events and monthly AMB measurements | One row per acquisition/measurement event | acquisition_event_id |
| src_rate_cards | Effective-dated commission rules | One row per rate rule | rate_card_id |
| src_incentive_slabs | Incentive slab configuration | One row per slab configuration | slab_id |
| src_tax_rules | Effective-dated tax rules | One row per tax rule | tax_rule_id |
| src_adjustments | Financial adjustment events | One row per adjustment event | adjustment_id |
| src_partner_invoices | Partner invoice records | One row per invoice | invoice_id |

## 3. Common Data Standards

- Identifiers will use STRING data types.

- Monetary values will use DECIMAL(18,2).

- Commission and tax rates will use DECIMAL(9,6).

- Dates will use YYYY-MM-DD.

- Timestamps will use ISO 8601 with timezone.

- Status values will use controlled uppercase values.

- Financial calculations will use decimal arithmetic.

## 4. Modelling Principles

1\. Every dataset must have a clearly defined grain.

2\. Primary keys must be unique and non-null.

3\. Foreign-key relationships must be validated.

4\. Historical records must be retained where business rules require history.

5\. Source records must not be silently overwritten.

6\. Invalid records must be identifiable and traceable.

7\. Synthetic data must not represent any real bank or customer.

## 5. Detailed Source Dataset Schemas

### 5.1 src_partner_master

**Business Purpose:** Stores hypothetical channel partner identity and profile information.

**Grain:** One row per partner.

**Primary Key:** partner_id

| Column | Data Type | Nullable | Validation / Description |
|---|---|---|---|
| partner_id | STRING | No | Unique partner ID |
| partner_name | STRING | No | Synthetic partner name |
| partner_type | STRING | No | DSA, AUTO_DEALER, TRACTOR_DEALER, CONNECTOR |
| city | STRING | No | Operating city |
| state | STRING | No | Operating state |
| onboarding_date | DATE | No | Must not be after project reference date |
| partner_status | STRING | No | ACTIVE, INACTIVE, SUSPENDED |
| created_at | TIMESTAMP | No | Source creation timestamp |
| updated_at | TIMESTAMP | Yes | Last source update timestamp |

### 5.2 src_partner_agreements

**Business Purpose:** Stores partner agreement and empanelment history.

**Grain:** One row per agreement/version.

**Primary Key:** agreement_id

**Foreign Key:** partner_id references src_partner_master.partner_id.

| Column | Data Type | Nullable | Validation / Description |
|---|---|---|---|
| agreement_id | STRING | No | Unique agreement ID |
| partner_id | STRING | No | Existing partner ID |
| agreement_status | STRING | No | ACTIVE, EXPIRED, TERMINATED, SUSPENDED |
| effective_from | DATE | No | Inclusive start date |
| effective_to | DATE | Yes | Exclusive end date |
| commission_eligible | BOOLEAN | No | Whether agreement permits commission calculation |
| agreement_document_ref | STRING | Yes | Synthetic document reference |
| created_at | TIMESTAMP | No | Source creation timestamp |
| updated_at | TIMESTAMP | Yes | Last source update timestamp |

- effective_to must be greater than effective_from when populated.

### 5.3 src_partner_kyc

**Business Purpose:** Stores historical partner KYC status.

**Grain:** One row per KYC status record/transition.

**Primary Key:** kyc_record_id

**Foreign Key:** partner_id references src_partner_master.partner_id.

| Column | Data Type | Nullable | Validation / Description |
|---|---|---|---|
| kyc_record_id | STRING | No | Unique KYC record ID |
| partner_id | STRING | No | Existing partner ID |
| kyc_status | STRING | No | PENDING, VERIFIED, REJECTED, EXPIRED |
| effective_from | DATE | No | Inclusive start date |
| effective_to | DATE | Yes | Exclusive end date |
| verification_date | DATE | Yes | Required for VERIFIED status |
| rejection_reason | STRING | Yes | Required for REJECTED status |
| created_at | TIMESTAMP | No | Source creation timestamp |
| updated_at | TIMESTAMP | Yes | Last source update timestamp |

**Validation and Modelling Notes**

- All primary keys must be unique and non-null.

- All foreign keys must reference existing parent records.

- Agreement and KYC effective periods use inclusive start and exclusive end dates.

- Overlapping agreement or KYC periods for the same partner are invalid unless explicitly allowed by a future business rule.

- Historical agreement and KYC records must be retained.

- Partner profile status, agreement status and KYC status are independent attributes.

- Monetary values in future datasets must use DECIMAL(18,2).

**KYC and Eligibility Evaluation Rules**

For this educational project, the following evaluation dates apply:

1\. Partner empanelment and agreement validity are evaluated as of the disbursement date.

2\. KYC status for payout release is evaluated as of the payout release date.

3\. A commission may be calculated and posted to the ledger while payout release is held due to pending KYC.

4\. Once KYC is verified, the held payout may be released in a subsequent payout cycle, provided all other release conditions are satisfied.

5\. KYC history must be retained to support historical, point-in-time eligibility checks.

These are illustrative project assumptions and do not represent a universal banking policy.

### 5.4 src_product_master

**Business Purpose:** Stores the hypothetical financial product definitions.

**Grain:** One row per product.

**Primary Key:** product_id

| Column | Data Type | Nullable | Validation / Description |
|---|---|---|---|
| product_id | STRING | No | Unique product ID |
| product_name | STRING | No | Product display name |
| product_category | STRING | No | LOAN or CASA |
| commission_basis | STRING | No | DISBURSED_AMOUNT or CASA_AMB |
| product_status | STRING | No | ACTIVE or INACTIVE |
| created_at | TIMESTAMP | No | Source creation timestamp |
| updated_at | TIMESTAMP | Yes | Last source update timestamp |

**Initial Reference Values:**

| product_id | product_name | product_category | commission_basis |
|---|---|---|---|
| PROD001 | New Car Loan | LOAN | DISBURSED_AMOUNT |
| PROD002 | Used Car Loan | LOAN | DISBURSED_AMOUNT |
| PROD003 | Tractor Loan | LOAN | DISBURSED_AMOUNT |
| PROD004 | Personal Loan | LOAN | DISBURSED_AMOUNT |
| PROD005 | Small Business Banking | LOAN | DISBURSED_AMOUNT |
| PROD006 | CASA | CASA | CASA_AMB |

**Validation Rules:**

- product_id must be unique and non-null.

- product_category must be LOAN or CASA.

- commission_basis must be DISBURSED_AMOUNT or CASA_AMB.

- LOAN products must use DISBURSED_AMOUNT.

- CASA products must use CASA_AMB.

### 5.5 src_disbursements

**Business Purpose:** Stores individual loan disbursement events.

**Grain:** One row per disbursement event.

**Primary Key:** disbursement_event_id

**Foreign Keys:**

- partner_id references src_partner_master.partner_id.

- product_id references src_product_master.product_id.

| Column | Data Type | Nullable | Validation / Description |
|---|---|---|---|
| disbursement_event_id | STRING | No | Unique source event ID |
| loan_id | STRING | No | Loan identifier; may repeat |
| disbursement_sequence | INTEGER | No | Positive sequence within loan |
| partner_id | STRING | No | Existing partner ID |
| product_id | STRING | No | Existing LOAN product ID |
| customer_ref | STRING | No | Synthetic customer reference; no real PII |
| disbursement_date | DATE | No | Actual disbursement date |
| disbursed_amount | DECIMAL(18,2) | No | Must be greater than zero |
| currency_code | STRING | No | INR |
| disbursement_status | STRING | No | SUCCESSFUL, FAILED, CANCELLED |
| source_system | STRING | No | Synthetic originating system |
| source_event_timestamp | TIMESTAMP | No | Source event timestamp |
| created_at | TIMESTAMP | No | Source record creation timestamp |
| updated_at | TIMESTAMP | Yes | Last source update timestamp |

**Validation Rules:**

- disbursement_event_id must be unique and non-null.

- loan_id, partner_id and product_id must be populated.

- partner_id and product_id must reference existing records.

- product_category must be LOAN.

- disbursement_sequence must be a positive integer.

- loan_id + disbursement_sequence must be unique.

- disbursed_amount must be greater than zero.

- currency_code must be INR.

- disbursement_status must be SUCCESSFUL, FAILED or CANCELLED.

- Only SUCCESSFUL events are candidates for commission calculation.

- Multiple successful disbursement events for the same loan are permitted.

- Failed or cancelled events must not generate commission.

**Modelling Notes:**

- loan_id is not unique because partial disbursements are supported.

- Each disbursement event has its own unique event identifier.

- Later financial reversals and clawbacks will be represented through src_adjustments.

- Source event timestamps and source record creation timestamps are retained separately for traceability.

### 5.6 src_casa_acquisitions

**Business Purpose:** Stores synthetic CASA acquisition events and monthly AMB measurement information.

**Grain:** One row per CASA acquisition/measurement event per measurement cycle.

**Primary Key:** acquisition_event_id

**Foreign Keys:**

- partner_id references src_partner_master.partner_id.

- product_id references src_product_master.product_id.

| Column | Data Type | Nullable | Validation / Description |
|---|---|---|---|
| acquisition_event_id | STRING | No | Unique acquisition/measurement event ID |
| account_id | STRING | No | Synthetic account reference |
| partner_id | STRING | No | Existing partner ID |
| product_id | STRING | No | Must reference CASA product |
| account_type | STRING | No | SAVINGS or CURRENT |
| acquisition_date | DATE | No | Account acquisition/opening date |
| measurement_month | DATE | No | First day of measurement month |
| average_monthly_balance | DECIMAL(18,2) | Yes | Monthly average balance |
| currency_code | STRING | No | INR |
| account_status | STRING | No | ACTIVE, CLOSED, DORMANT |
| eligibility_status | STRING | No | ELIGIBLE, INELIGIBLE, PENDING |
| source_system | STRING | No | Synthetic originating system |
| source_event_timestamp | TIMESTAMP | No | Source event timestamp |
| created_at | TIMESTAMP | No | Source creation timestamp |
| updated_at | TIMESTAMP | Yes | Last source update timestamp |

**Validation Rules:**

- acquisition_event_id must be unique and non-null.

- account_id, partner_id and product_id must be populated.

- partner_id and product_id must reference existing records.

- product_category must be CASA.

- measurement_month must be the first day of a calendar month.

- average_monthly_balance must be zero or greater when populated.

- account_type must be SAVINGS or CURRENT.

- account_status must be ACTIVE, CLOSED or DORMANT.

- eligibility_status must be ELIGIBLE, INELIGIBLE or PENDING.

- acquisition_date must not be after the end of measurement_month.

- Only one authoritative AMB measurement per account and measurement month may be used for commission calculation.

- PENDING and INELIGIBLE records must not generate commission until eligibility conditions are satisfied.

**Modelling Notes:**

- account_id is not the primary key because an account can have multiple monthly measurement events.

- acquisition_event_id uniquely identifies each measurement event.

- AMB is assumed to be supplied by the synthetic source system in the initial version.

- Daily account balance snapshots and AMB derivation are optional future enhancements.

- CASA commission calculation supports AMB_RATE, FIXED_PER_ACCOUNT and AMB_TIERED modes.

### 5.7 src_rate_cards

**Business Purpose:** Stores effective-dated commission rate rules.

**Grain:** One row per effective-dated commission rate rule.

**Primary Key:** rate_card_id

**Foreign Key:** product_id references src_product_master.product_id.

**Conditional Foreign Key:** partner_id references src_partner_master.partner_id when populated.

| Column | Data Type | Nullable | Validation / Description |
|---|---|---|---|
| rate_card_id | STRING | No | Unique rate rule ID |
| partner_id | STRING | Yes | Optional partner-specific rule |
| partner_type | STRING | Yes | Optional partner category rule |
| product_id | STRING | No | Existing product ID |
| commission_mode | STRING | No | LOAN_RATE, AMB_RATE, FIXED_PER_ACCOUNT, AMB_TIERED |
| commission_rate | DECIMAL(9,6) | Yes | Percentage rate |
| fixed_amount | DECIMAL(18,2) | Yes | Fixed commission amount |
| tier_group_id | STRING | Yes | Identifies all tiers belonging to one CASA AMB tier configuration |
| tier_lower_bound | DECIMAL(18,2) | Yes | Inclusive lower AMB boundary |
| tier_upper_bound | DECIMAL(18,2) | Yes | Exclusive upper AMB boundary; NULL for the final tier |
| effective_from | DATE | No | Inclusive start date |
| effective_to | DATE | Yes | Exclusive end date |
| rule_status | STRING | No | ACTIVE, INACTIVE |
| rule_version | STRING | No | Rule version |
| created_at | TIMESTAMP | No | Source creation timestamp |
| updated_at | TIMESTAMP | Yes | Last source update timestamp |

**Validation Rules:**

- rate_card_id must be unique and non-null.

- product_id must reference an existing product.

- Exactly one of partner_id and partner_type must be populated.

- A populated partner_id must reference an existing partner.

- Effective dates must be valid.

- Commission mode must be compatible with product category.

- Required rate or fixed amount must be populated according to commission mode.

- Overlapping rules for the same applicability dimensions must be identified and rejected unless explicitly resolved by precedence.

- Rule changes must be versioned and traceable.

**Modelling Notes:**

- Partner-specific rules take precedence over partner-type rules.

- Rate selection uses the transaction's applicable effective date.

- Effective start is inclusive and effective end is exclusive.

- For AMB_TIERED commission mode, multiple rows may share the same tier_group_id.

- Each AMB_TIERED rate rule must have a populated tier_group_id and tier_lower_bound; tier_upper_bound is required except for the final tier, where it is NULL.
- Non-AMB_TIERED rules must leave tier_group_id, tier_lower_bound and tier_upper_bound NULL.
- Each tier must have a valid lower and upper boundary.

- Tiers within the same tier_group_id must not overlap.

- Tier boundaries must provide complete coverage of the intended AMB range.

- The applicable tier rate is selected using the account's average monthly balance.

- The selected tier's rate is applied to the entire eligible AMB in this project.

- AMB_TIERED is a base commission calculation and is separate from partner volume incentive slabs.

### 5.8 src_incentive_slabs

**Business Purpose:** Stores partner-level volume-based incentive slab rules.

**Grain:** One row per incentive slab configuration.

**Primary Key:** slab_id

**Foreign Keys:**

- product_id references src_product_master.product_id.

- partner_id references src_partner_master.partner_id when populated.

| Column | Data Type | Nullable | Validation / Description |
|---|---|---|---|
| slab_id | STRING | No | Unique slab ID |
| calculation_group_id | STRING | No | Identifies slabs in the same configuration |
| partner_type | STRING | Yes | Optional partner category applicability |
| partner_id | STRING | Yes | Optional partner-specific applicability |
| product_id | STRING | No | Existing product ID |
| payout_cycle | STRING | No | MONTHLY or QUARTERLY |
| slab_calculation_type | STRING | No | RETROACTIVE or MARGINAL |
| lower_bound | DECIMAL(18,2) | No | Inclusive volume boundary |
| upper_bound | DECIMAL(18,2) | Yes | Exclusive volume boundary |
| incentive_rate | DECIMAL(9,6) | No | Incentive percentage |
| effective_from | DATE | No | Inclusive start date |
| effective_to | DATE | Yes | Exclusive end date |
| rule_status | STRING | No | ACTIVE, INACTIVE |
| rule_version | STRING | No | Configuration version |
| created_at | TIMESTAMP | No | Source creation timestamp |
| updated_at | TIMESTAMP | Yes | Last update timestamp |

**Validation Rules:**

- slab_id must be unique and non-null.

- calculation_group_id must be populated.

- Exactly one of partner_id and partner_type must be populated.

- Product and partner references must be valid.

- lower_bound must be zero or greater.

- upper_bound must be greater than lower_bound when populated.

- Slabs within the same calculation group must not overlap.

- Slab boundaries must be continuous where the configuration requires complete coverage.

- Incentive rates must be valid non-negative decimal values.

- Slab calculation type must be RETROACTIVE or MARGINAL.

- Effective dates must be valid.

**Modelling Notes:**

- Base commission and volume-based incentives are separate financial components.

- Slabs are grouped using calculation_group_id.

- Boundaries are lower-inclusive and upper-exclusive.

- RETROACTIVE applies the selected slab rate to the entire eligible volume.

- MARGINAL applies the corresponding rate to each volume portion.

- CASA AMB tiered base commission is separate from partner volume-based incentive slabs.

### 5.9 src_tax_rules

**Business Purpose:** Stores configurable, effective-dated tax deduction rules used during commission and payout calculations. All tax rates and tax calculation bases in this project are illustrative and intended only for educational purposes.

**Grain:** One row per effective-dated tax rule.

| Column Name | Data Type | Nullable | Constraints / Description |
|---|---|---|---|
| tax_rule_id | STRING | No | Primary key; unique tax rule identifier |
| tax_rule_name | STRING | No | Descriptive name of the tax rule |
| partner_type | STRING | Yes | DSA, AUTO_DEALER, TRACTOR_DEALER, CONNECTOR; NULL indicates a general rule applicable to all supported partner types |
| tax_type | STRING | No | Tax category; initially TDS |
| tax_rate | DECIMAL(9,6) | No | Non-negative tax rate; stored as a decimal fraction |
| tax_calculation_basis | STRING | No | GROSS_COMMISSION or COMMISSION_PLUS_INCENTIVE |
| tax_date_basis | STRING | No | TRANSACTION_DATE, INVOICE_DATE or PAYOUT_DATE |
| effective_from | DATE | No | Inclusive start date of rule validity |
| effective_to | DATE | Yes | Exclusive end date; NULL means no scheduled end |
| rule_status | STRING | No | ACTIVE or INACTIVE |
| rule_version | STRING | No | Version of the tax rule |
| created_at | TIMESTAMP | No | Record creation timestamp |
| updated_at | TIMESTAMP | No | Last update timestamp |

**Sample Records**

| tax_rule_id | tax_rule_name | partner_type | tax_type | tax_rate | tax_calculation_basis | tax_date_basis | effective_from | effective_to | rule_status | rule_version |
|---|---|---|---|---:|---|---|---|---|---|---|
| TAX001 | DSA TDS Rule | DSA | TDS | 0.020000 | GROSS_COMMISSION | PAYOUT_DATE | 2026-01-01 | NULL | ACTIVE | V1 |
| TAX002 | Auto Dealer TDS Rule | AUTO_DEALER | TDS | 0.020000 | GROSS_COMMISSION | PAYOUT_DATE | 2026-01-01 | NULL | ACTIVE | V1 |
| TAX003 | Connector TDS Rule | CONNECTOR | TDS | 0.010000 | COMMISSION_PLUS_INCENTIVE | INVOICE_DATE | 2026-01-01 | NULL | ACTIVE | V1 |

**Business Rules and Validations**

1\. Tax rates must be configurable and must not be hardcoded into the payout calculation logic.

2\. Tax rule selection must consider the configured tax date basis.

3\. Effective-date matching follows:

   - `effective_from <= applicable_date`

   - `effective_to > applicable_date`, or `effective_to IS NULL`

4\. Overlapping active tax rules for the same applicability dimensions must raise a data-quality exception.

5\. If no applicable tax rule is found, the transaction must be recorded as an exception rather than silently assuming a zero tax rate.

6\. Tax calculation must use the configured calculation basis.

7\. Tax amounts must be rounded according to the project's defined financial rounding convention.

8\. Tax rule changes must be version-controlled and must not silently modify previously committed payout ledger entries.

9\. This initial version supports partner-type-specific and general tax rules; partner-specific tax rules are out of scope.

10\. All tax calculations are illustrative and do not represent actual statutory tax advice or rates.

11\. A populated partner_type identifies a partner-category-specific tax rule.

12\. A NULL partner_type represents a general tax rule applicable to all supported partner types.

13\. For the same tax type and effective date, a partner-type-specific rule takes precedence over a general rule.

14\. Multiple applicable rules at the same precedence level must raise a data-quality exception.

GROSS_COMMISSION = eligible base commission before TDS.

COMMISSION_PLUS_INCENTIVE = eligible base commission plus eligible incentive before TDS.

### 5.10 src_adjustments

**Business Purpose:** Stores financial adjustment events that modify previously calculated commissions or payouts.

Examples include:

- Loan cancellation reversals.

- Foreclosure-related clawbacks.

- Commission clawbacks.

- Approved manual adjustments.

- Corrections to previously processed financial events.

**Grain:** One row per adjustment event.

| Column Name | Data Type | Nullable | Constraints / Description |
|---|---|---|---|
| adjustment_id | STRING | No | Primary key; unique adjustment event identifier |
| original_source_event_type | STRING | No | DISBURSEMENT or CASA_ACQUISITION; identifies the source dataset of the original event |
| original_source_event_id | STRING | No | Reference to the original event in the dataset identified by original_source_event_type |
| partner_id | STRING | No | Foreign key referencing `src_partner_master.partner_id` |
| product_id | STRING | No | Foreign key referencing `src_product_master.product_id` |
| adjustment_type | STRING | No | CLAWBACK, CANCELLATION_REVERSAL, FORECLOSURE_REVERSAL or MANUAL_ADJUSTMENT |
| adjustment_amount | DECIMAL(18,2) | No | Positive source adjustment amount; posting sign is determined by business logic |
| adjustment_direction | STRING | No | DEBIT or CREDIT; determines the financial posting direction |
| adjustment_reason | STRING | No | Business explanation for the adjustment |
| adjustment_date | DATE | No | Date the adjustment was initiated |
| effective_date | DATE | No | Date the adjustment becomes applicable |
| approval_status | STRING | No | PENDING, APPROVED or REJECTED |
| approved_by | STRING | Yes | Approver reference; required when approval_status is APPROVED |
| source_system | STRING | No | Source system identifier |
| source_event_timestamp | TIMESTAMP | No | Timestamp of the source adjustment event |
| created_at | TIMESTAMP | No | Record creation timestamp |
| updated_at | TIMESTAMP | No | Last update timestamp |

**Sample Records**

| adjustment_id | original_source_event_type | original_source_event_id | partner_id | product_id | adjustment_type | adjustment_amount | adjustment_direction | adjustment_reason | adjustment_date | effective_date | approval_status | approved_by |
|---|---|---|---|---|---|---:|---|---|---|---|---|---|
| ADJ001 | DISBURSEMENT | DISB001 | P001 | PROD001 | CANCELLATION_REVERSAL | 10000.00 | DEBIT | Loan cancelled within illustrative clawback window | 2026-06-15 | 2026-06-15 | APPROVED | PORTFOLIO_APPROVER_01 |
| ADJ002 | DISBURSEMENT | DISB002 | P002 | PROD002 | FORECLOSURE_REVERSAL | 5000.00 | DEBIT | Early foreclosure within illustrative clawback window | 2026-06-20 | 2026-06-20 | PENDING | |
| ADJ003 | DISBURSEMENT | DISB003 | P003 | PROD003 | MANUAL_ADJUSTMENT | 1500.00 | CREDIT | Approved commission correction | 2026-06-25 | 2026-06-25 | APPROVED | PORTFOLIO_APPROVER_02 |

**Business Rules and Validations**

1\. Every adjustment must have a unique `adjustment_id`.

2\. The original source event must be identifiable and traceable through `original_source_event_type` and `original_source_event_id`.

3\. `partner_id` and `product_id` must reference valid master records.

4\. Only APPROVED adjustments are eligible for financial posting.

5\. PENDING and REJECTED adjustments must not affect payout calculations.

6\. An adjustment must not overwrite or delete an existing payout ledger entry.

7\. Approved clawbacks and reversals must create separate negative ledger postings.

8\. The source `adjustment_amount` is stored as a positive value; the ledger posting logic determines whether the financial impact is positive or negative.

9\. Reprocessing the same adjustment must not create a duplicate financial effect.

10\. If an adjustment references an unknown source event, the record must be quarantined or recorded as an exception.

11\. Any change to an already-posted adjustment must be represented through a new corrective adjustment or an explicit reversal-and-replacement process.

12\. Approval history and source references must be retained for auditability.

13\. adjustment_amount must always be a positive value.

14\. adjustment_direction determines whether the ledger posting is negative or positive.

15\. CLAWBACK, CANCELLATION_REVERSAL and FORECLOSURE_REVERSAL must use DEBIT.

16\. MANUAL_ADJUSTMENT may use DEBIT or CREDIT, depending on the approved correction.

17\. Only APPROVED adjustments are eligible for financial posting.

18\. `original_source_event_type` and `original_source_event_id` together must identify exactly one existing source event.

19\. DISBURSEMENT event IDs must exist in `src_disbursements`; CASA_ACQUISITION event IDs must exist in `src_casa_acquisitions`.

**Illustrative Ledger Example**

Assume an original commission of INR 10,000 was posted and a subsequent cancellation requires a full reversal.

| Posting Component | Amount | Description |
|---|---:|---|
| BASE_COMMISSION | +10000.00 | Original commission posting |
| CANCELLATION_REVERSAL | -10000.00 | Separate reversal posting |
| NET FINANCIAL IMPACT | 0.00 | Combined ledger impact |

The original commission record must remain unchanged.

### 5.11 src_partner_invoices

**Business Purpose:** Stores partner-submitted invoices and their validation information before payout release.

Invoice validation is a separate business control from commission calculation and tax deduction.

**Grain:** One row per partner invoice.

| Column Name | Data Type | Nullable | Constraints / Description |
|---|---|---|---|
| invoice_id | STRING | No | Primary key; unique invoice record identifier |
| partner_id | STRING | No | Foreign key referencing `src_partner_master.partner_id` |
| invoice_number | STRING | No | Partner-provided invoice number |
| invoice_date | DATE | No | Date on which invoice was issued |
| invoice_period_start | DATE | No | Start of the invoiced period |
| invoice_period_end | DATE | No | End of the invoiced period |
| taxable_amount | DECIMAL(18,2) | No | Invoice taxable amount; non-negative |
| gst_amount | DECIMAL(18,2) | No | GST amount; non-negative |
| total_invoice_amount | DECIMAL(18,2) | No | Total invoice amount |
| currency_code | STRING | No | Currency code; initially INR |
| invoice_status | STRING | No | SUBMITTED, VALIDATED or REJECTED |
| validation_reason | STRING | Yes | Explanation for invoice validation failure or other validation information |
| source_system | STRING | No | Source system identifier |
| payout_cycle | STRING | No | Payout cycle covered by the invoice; initially MONTHLY |
| created_at | TIMESTAMP | No | Record creation timestamp |
| updated_at | TIMESTAMP | No | Last update timestamp |

**Sample Records**

| invoice_id | partner_id | invoice_number | invoice_date | invoice_period_start | invoice_period_end | taxable_amount | gst_amount | total_invoice_amount | currency_code | invoice_status | validation_reason | payout_cycle |
|---|---|---|---|---|---|---:|---:|---:|---|---|---|---|
| INV001 | P001 | INV-P001-001 | 2026-06-30 | 2026-06-01 | 2026-06-30 | 10000.00 | 1800.00 | 11800.00 | INR | VALIDATED | | MONTHLY |
| INV002 | P002 | INV-P002-001 | 2026-06-30 | 2026-06-01 | 2026-06-30 | 15000.00 | 2700.00 | 17700.00 | INR | SUBMITTED | AWAITING_VALIDATION | MONTHLY |
| INV003 | P003 | INV-P003-001 | 2026-06-30 | 2026-06-01 | 2026-06-30 | 8000.00 | 0.00 | 8000.00 | INR | REJECTED | PARTNER_TAX_PROFILE_MISMATCH | MONTHLY |

**Business Rules and Validations**

1\. Every invoice must have a unique `invoice_id`.

2\. The combination of `partner_id` and `invoice_number` must be unique for the initial project scope.

3\. Partner references must exist in `src_partner_master`.

4\. Invoice period start date must be earlier than or equal to invoice period end date.

5\. Taxable amount and GST amount must be non-negative.

6\. Invoice total must reconcile:

   `total_invoice_amount = taxable_amount + gst_amount`

7\. Reconciliation must follow the project's defined rounding convention.

8\. An invoice in SUBMITTED status must not be treated as validated.

9\. An invoice in REJECTED status must place the corresponding payout release on hold.

10\. A VALIDATED invoice can satisfy the invoice validation gate, subject to all other payout release conditions.

11\. Invoice validation must remain separate from commission calculation eligibility.

12\. Invoice validation must remain separate from TDS calculation.

13\. GST must not be automatically added to net commission payable without an explicitly defined payout and invoice treatment.

14\. Invoice corrections or resubmissions must be traceable and must not silently overwrite previously processed financial records.

15\. Missing or invalid invoice references must be recorded in `fact_payout_exceptions`.

16\. `payout_cycle` must be MONTHLY in the initial project scope.

17\. A REJECTED invoice must contain a non-null `validation_reason`.

18\. The invoice payout cycle and invoice period must correspond to the payout period being validated.

**Important Financial Distinction**

| Component | Treatment |
|---|---|
| Gross Commission | Calculated using applicable commission rules |
| Incentive | Calculated using the applicable payout-cycle incentive rules |
| Clawback | Posted as a separate negative ledger component |
| TDS | Deducted using the configured tax rule |
| GST | Validated and reconciled against the submitted invoice |
| Net Payable | Calculated using the project's defined payout formula and carry-forward rules |

Invoice validation does not automatically establish that a partner is eligible for payout. All other payout release conditions, including KYC and compliance checks, must also pass.