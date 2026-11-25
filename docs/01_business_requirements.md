# Banking Partner Commission and Payout Data Engineering Solution

## Business Requirements Document (BRD) — Version 2.2 (Educational / Portfolio Project)

| Document Attribute | Details | 
| ----- | ----- | 
| Document Status | Self-Learning Data Engineering Specification (Scope Frozen Baseline) | 
| Version | 2.2 | 
| Last Updated | 24 November 2026 | 
| Project Type | Educational Data Engineering Project (Solo Implementation) | 
| Author & Developer | Kota Vikramdev (Independent Data Engineering Learner) | 
| Target Audience | Personal Portfolio, Technical Reviewers, Data Engineering Evaluators | 

> ### ⚠️ DISCLAIMER & NON-AFFILIATION NOTICE
>
> **Educational & Self-Learning Purpose Only:** This document and the associated data engineering project are strictly created for self-learning, skill development, and personal portfolio demonstration purposes.
>
> **No Real Bank Affiliation:** This project **does not represent, refer to, or use proprietary information from any real banking institution, financial service provider, or commercial entity**. All company names, banking workflows, commission structures, tax rules, loan schemas, and transaction datasets described in this document are **100% synthetic, hypothetical, and designed for learning data pipeline engineering concepts**.

---

## 1. Project Objective and Portfolio Goals

### 1.1 Project Objective

The objective of this project is to design, build, and test an end-to-end **Banking Partner Commission and Payout Data Engineering Solution**.

The pipeline ingests multi-source banking datasets (partner master data, loan disbursements, CASA account openings, rate cards, incentive slabs, partner KYC, invoices, and loan adjustment records), validates incoming data quality, calculates multi-tiered commission structures, processes contractual clawbacks/reversals, applies tax logic (TDS & GST), and outputs reconciled financial datasets ready for downstream reporting.

### 1.2 Learning & Skill Development Objectives

As a single-handed self-learning project, this BRD serves as the functional design reference to demonstrate proficiency in:

* **Data Engineering Design:** Translating complex, domain-specific financial rules into scalable data transformation pipelines.
* **SCD Type 2 Implementation:** Building historical tracking dimensions for changing partner profiles (`dim_channel_partner`) while referencing effective-dated source agreements.
* **Data Quality & Quarantine Pipelines:** Implementing robust quarantine processes for invalid, incomplete, or duplicate input records.
* **Financial Reconciliation & Idempotency:** Designing deterministic pipeline executions so retries yield identical results without duplicate ledger postings, ensuring every ledger output is fully auditable.
* **Modular Pipeline Architecture:** Structuring batch processing workflows using standard data engineering toolchains (PySpark, SQL, Orchestration, Delta Lake / Parquet).

---

## 2. Business Background and Problem Simulation

In retail banking ecosystems, financial institutions work with external sourcing partners such as Direct Selling Agents (DSAs), Auto Dealers, Tractor Dealers, and Connectors to acquire credit customers and deposit accounts. Partners earn financial commissions based on agreed performance structures.

Calculating payouts accurately is complex due to distributed source systems, changing commission rates, late-arriving cancellation events (clawbacks), invoice mismatches, and compliance/tax controls.

This project simulates these real-world enterprise data challenges within a controlled sandbox environment to practice handling production-grade data engineering scenarios.

### 2.1 Simulated Business Challenges Addressed

* **Multi-Source Ingestion:** Handling heterogeneous formats and schema variances across raw CSV/Parquet files.
* **Granular Deduplication:** Handling multiple partial loan disbursements without treating legitimate events as duplicates.
* **Late-Arriving Adjustment Events:** Handling foreclosures or loan cancellations that arrive weeks or months after a commission has been calculated or paid.
* **Complex Financial Logic:** Implementing volume-based incentive slabs under both retroactive and marginal calculation modes.
* **Data Governance & Auditability:** Retaining full financial traceability using immutable ledger mechanics without silently deleting or modifying historical records.

---

## 3. Project Roles & Implementation Context

Since this is a solo learning project, all traditional project roles are executed by Kota Vikramdev as the lead developer to simulate an end-to-end data engineering lifecycle:

| Role | Simulated Responsibility in Learning Context | 
| ----- | ----- | 
| **Data Engineer (Author)** | Designs schema, builds data pipelines, implements transformations, and writes unit/integration tests (Kota Vikramdev). | 
| **Business Analyst (Simulated)** | Defines business rules, edge cases, and functional specs (captured in this BRD). | 
| **Finance / Compliance (Simulated)** | Establishes synthetic validation gates for tax (TDS/GST), invoice matching, and ledger reconciliation outputs. | 
| **Code Reviewer / Portfolio Assessor** | Evaluates pipeline cleanliness, data modeling quality, documentation, and error handling. | 

---

## 4. Products and Partner Channels in Scope

### 4.1 Products in Scope (6 Products)

The business scope focuses on the following six specific financial products:

1. **New Car Loans** — Vehicle financing for brand-new automobiles.
2. **Used Car Loans** — Pre-owned vehicle financing.
3. **Tractor Loans** — Agricultural and commercial tractor financing.
4. **Personal Loans** — Unsecured personal credit facilities.
5. **Small Business Banking** — Commercial loans and credit lines for small enterprises.
6. **CASA (Current Account / Savings Account)** — Deposit account acquisitions evaluated on average monthly balance (AMB) thresholds.

### 4.2 Partner Sourcing Channels (4 Channels)

The pipeline supports configurable rate rules across four partner categories:

1. **DSA** — Direct Selling Agents
2. **Auto Dealers** — Authorized retail sales dealers for new and used cars
3. **Tractor Dealers** — Authorized agricultural equipment dealers
4. **Connectors** — Individual business referral partners

---

## 5. Scope Boundaries (Learning Phase 1)

### 5.1 Included In Data Engineering Build

* Automated ingestion and schema validation of CSV/Parquet synthetic datasets.
* Duplicate detection across transaction, account booking, and partner master records.
* Effective-dated commission rate card lookup matching (SCD Type 2 logic for partners).
* Dual-gate eligibility verification (Empanelment, KYC validation, Invoice approval, Payout hold flags).
* Monthly volume-based incentive slab aggregation (Retroactive & Marginal logic).
* Contractual clawback and cancellation adjustment processing (Partial & Full clawbacks).
* Tax calculation (TDS deduction and GST verification on configurable tax bases and date bases).
* Creation of an Exception/Quarantine dataset for bad records (`fact_payout_exceptions`).
* Data processing execution tracking (`payout_batch_control`).
* Generation of standardized downstream financial dimensional models.

### 5.2 Excluded from Pipeline Build (Out of Scope)

* Real banking payment gateway integrations (no real money is processed).
* Core banking mainframes or general ledger live sync.
* Real-time streaming/fraud processing (focused on batch/micro-batch processing).
* Legal tax filings or compliance reporting to authorities.

---

## 6. Source Systems, Logical Datasets, and Data Model

To establish clear data contracts, the pipeline ingests raw source datasets and outputs modeled dimensional tables. Every target table has a strictly defined grain.

### 6.1 Raw Ingestion Datasets

| Dataset | Logical Purpose | Primary / Raw Key | 
| ----- | ----- | ----- | 
| **`src_partner_master`** | Partner profile and empanelment details | `partner_id` | 
| **`src_partner_kyc`** | Historical partner tax registrations (PAN, GSTIN) and KYC status | `kyc_record_id ` | 
| **`src_partner_agreements`** | Partner agreement terms, validity dates, and contractual conditions | `agreement_id` | 
| **`src_disbursements`** | Actual disbursed loan events (including partial disbursements) | `disbursement_id` | 
| **`src_casa_acquisitions`** | Opened savings/current account records with AMB details | `account_id` | 
| **`src_product_master`** | Product identification, eligibility, calculation configuration, and CASA calculation modes | `product_code` | 
| **`src_rate_cards`** | Commission rate configurations and effective dates | `rate_card_id` | 
| **`src_incentive_slabs`** | Volume tier definitions and calculation rules | `slab_id` | 
| **`src_tax_rules`** | Configurable TDS/GST rates, calculation bases, effective dates, and effective-date basis | `tax_rule_id` | 
| **`src_adjustments`** | Foreclosure, early closure, and cancellation events | `adjustment_event_id` | 
| **`src_partner_invoices`** | Submitted invoices for payout release | `invoice_id` | 

#### Historical KYC Record Management

The src_partner_kyc dataset is maintained as an effective-dated historical dataset to support auditability and point-in-time eligibility validation.

A partner may experience multiple status transitions over time, including:

- Pending → Verified
- Verified → Expired
- Expired → Renewed

partner_id acts as the business key.

kyc_record_id uniquely identifies each historical KYC record version.

Recommended source attributes include:

- kyc_record_id
- partner_id
- kyc_status
- pan_verification_status
- gstin_verification_status
- effective_start_date
- effective_end_date
- updated_at

### 6.2 Downstream Data Engineering Targets & Table Grains

| Target Table Name | Entity Type | Defined Table Grain (1 Row Represents) | Target Schema Fields | 
| ----- | ----- | ----- | ----- | 
| **`dim_channel_partner`** | Dimension (SCD Type 2) | **One partner profile version** across effective date ranges. | `partner_sk`, `partner_id`, `partner_name`, `channel_type`, `empanelment_status`, `kyc_status`, `pan_number`, `gstin`, `effective_start_date`, `effective_end_date`, `is_current` | 
| **`fact_disbursements`** | Fact Table | **One loan disbursement event** (including partial disbursements). | `disbursement_sk`, `disbursement_id`, `source_event_id`, `source_event_type`, `partner_id`, `agreement_id`, `customer_id`, `product_code`, `channel_type`, `disbursed_amount`, `disbursement_date`, `batch_id` | 
| **`fact_casa_acquisitions`** | Fact Table | **One deposit account acquisition event**. | `casa_acquisition_sk`, `account_id`, `source_event_id`, `partner_id`, `agreement_id`, `product_code`, `channel_type`, `account_type`, `account_opening_date`, `qualifying_amb`, `amb_measurement_start_date`, `amb_measurement_end_date`, `amb_measurement_month`, `eligibility_status`, `payout_cycle`, `batch_id` | 
| **`fact_payout_ledger`** | Financial Ledger Fact | **One financial posting line item** (Base commission, incentive, clawback, adjustment, TDS, or GST). | `ledger_id`, `idempotency_key`, `source_event_id`, `posting_component`, `calculation_group_id`, `rule_id`, `rule_version`, `original_ledger_id`, `disbursement_id`, `account_id`, `partner_id`, `posting_date`, `transaction_type`, `amount`, `tds_amount`, `gst_amount`, `payout_cycle`, `batch_id` | 
| **`fact_payout_summary`** | Monthly Aggregate Fact | **One partner per payout cycle summary** containing net payable and carried-forward amounts. | `summary_id`, `payout_cycle`, `partner_id`, `gross_commission`, `total_incentives`, `total_clawbacks`, `manual_adjustments`, `total_tds`, `total_gst`, `net_payable_before_carry_forward`, `opening_carry_forward`, `net_payable_after_carry_forward`, `amount_carried_forward`, `payout_status` | 
| **`fact_payout_exceptions`** | Quarantine Fact | **One data quality or validation exception occurrence.** | `exception_id`, `source_file`, `source_record_id`, `error_code`, `error_description`, `resolution_status`, `quarantine_timestamp`, `batch_id` | 
| **`payout_batch_control`** | Operational Metadata | **One ingestion or pipeline execution batch.** | `batch_id`, `pipeline_name`, `execution_start_time`, `execution_end_time`, `records_ingested`, `records_quarantined`, `batch_status` | 

##### CASA Acquisition Grain Note

The defined grain of fact_casa_acquisitions is one deposit account acquisition event.

If future source systems allow multiple acquisition or booking events for the same account, an acquisition_event_id may be introduced as the event-level identifier while retaining account_id as the business key.

For the current learning-project scope, account_id remains the primary raw identifier.

---

## 7. Business Logic & Calculation Rules

### 7.1 Financial Calculation Formulas

#### 7.1.1 Loan Products — Gross Base Commission

Base commission is calculated strictly at the eligible source-event level (per loan disbursement):

$$
\text{Gross Base Commission}_{\text{loan}} = (\text{Eligible Disbursed Amount} \times \text{Applicable Rate (\%)}) + \text{Flat Fee}
$$

#### 7.1.2 CASA Products — Deposit Incentives

Qualifying AMB represents the average monthly balance calculated over a defined measurement period (`amb_measurement_start_date` to `amb_measurement_end_date`). The applicable calculation mode is selected from `src_product_master` or the associated rate card:

| Calculation Mode | Description & Formula | 
| ----- | ----- | 
| **`AMB_RATE`** | Incentive calculated as a percentage of qualifying AMB:<br>$$\text{Incentive} = \text{Qualifying AMB} \times \text{Applicable Rate (\%)} $$ | 
| **`FIXED_PER_ACCOUNT`** | Fixed incentive fee per eligible opened account:<br>$$\text{Incentive} = \text{Fixed Account Fee}$$ | 
| **`AMB_TIERED`** | Tier-based incentive assigned based on the qualifying AMB range bracket. | 

If the account does not satisfy the minimum AMB eligibility threshold, no incentive is generated, `eligibility_status` is updated, and `ERR_AMB_BELOW_THRESHOLD` is logged.

#### 7.1.3 Configurable Tax Calculation (TDS & GST)

Each tax rule in `src_tax_rules` defines an effective start date, effective end date, applicable tax rate, calculation base, and an **effective-date basis**.

* **Effective-Date Basis:** Determines whether tax rules match against `disbursement_date` / `account_opening_date` (transaction date), `invoice_date`, or `payout_date`.
* **Configured Tax Base:** May include base commission, incentives, or combined eligible financial amounts as defined by the active rule configuration.

```math
\text{TDS Amount} = \text{Configured TDS Tax Base} \times \text{TDS Rate (\%)}
```

```math
\text{GST Amount} = \begin{cases} \text{Configured GST Tax Base} \times \text{GST Rate (\%)} & \text{if Partner is GST Registered and Invoiced} \\ 0 & \text{otherwise} \end{cases}
```

#### 7.1.4 Carry-Forward Balance Mechanics & Formulas

To ensure transparent accounting across monthly payout cycles, negative balances resulting from clawbacks or adjustments are explicitly carried forward into subsequent cycles using four auditable metrics:

* **`opening_carry_forward`:** Outstanding negative balance brought forward from the previous payout cycle.
* **`net_payable_before_carry_forward`:** Current cycle's signed ledger total.
* **`net_payable_after_carry_forward`:** Final amount payable after applying the opening carry-forward balance.
* **`amount_carried_forward`:** Closing carry-forward balance to be carried into the next payout cycle.

$$
\text{Net Payable Before Carry Forward} = \text{Gross Base Commission} + \text{Incentive Amount} - \text{Clawback Amount} \pm \text{Manual Adjustments} - \text{TDS} + \text{GST}
$$

$$
\text{Net Payable After Carry Forward} = \max\left(0, \text{Net Payable Before Carry Forward} - \text{Opening Carry Forward}\right)
$$

$$
\text{Closing Carry Forward} = \max\left(0, \text{Opening Carry Forward} - \max\left(0, \text{Net Payable Before Carry Forward}\right)\right) + \max\left(0, -\text{Net Payable Before Carry Forward}\right)
$$

Where `amount_carried_forward` in `fact_payout_summary` stores the computed Closing Carry Forward value.

##### Multi-Cycle Carry-Forward Demonstration

| Financial Metric | Cycle 1 (Clawback Exceeds Earned) | Cycle 2 (Recovery in Subsequent Cycle) | 
| ----- | ----- | ----- | 
| **Current Cycle Net (`net_payable_before_carry_forward`)** | $-\text{Rs. } 2,000$ | $+\text{Rs. } 5,000$ | 
| **Opening Carry-Forward (`opening_carry_forward`)** | $\text{Rs. } 0$ | $\text{Rs. } 2,000$ | 
| **Payable After Carry-Forward (`net_payable_after_carry_forward`)** | $\text{Rs. } 0$ | $\text{Rs. } 3,000$ | 
| **Closing Carry-Forward (`amount_carried_forward`)** | $\text{Rs. } 2,000$ | $\text{Rs. } 0$ | 

### 7.2 Effective-Dated Rate Card Matching

The pipeline selects the applicable commission rate matching partner, channel, and product where dates satisfy:

$$
\text{Rate Effective Start Date} \le \text{Transaction Date} < \text{Rate Effective End Date}
$$

> **Rule Overlap Exception:** Overlapping active rate-card records for the same applicable configuration are treated as a data-quality exception (`ERR_RATE_OVERLAP`) rather than resolved arbitrarily.

### 7.3 Incentive Slab Calculation Methodologies & Base Interaction

Monthly total eligible volume is aggregated per partner, product, channel, and payout cycle (with grouping driven by configuration).

* **Interaction Rule:** Base commission is calculated at the eligible source-event level. Volume-based slab incentives are calculated separately using the aggregated group volume. The resulting incentive is posted as a distinct financial ledger component (`posting_component = INCENTIVE`) and is **never double-counted inside base commission**.

The engine supports two distinct calculation modes:

1. **Retroactive (Tiered Full-Volume) Slabs:** Reaching a higher volume tier applies the higher rate retroactively to 100% of the total monthly volume.
2. **Marginal (Tiered Graduated) Slabs:** The higher rate applies exclusively to the incremental volume within that specific slab bracket.

#### Slab Boundary Assignment Rules

To prevent overlapping slab assignments, all volume slabs use lower-inclusive and upper-exclusive boundaries except for the highest slab.

Example:

| Slab | Monthly Eligible Volume |
|--------|----------------------|
| Slab 1 | ₹0 ≤ Volume < ₹10,00,000 |
| Slab 2 | ₹10,00,000 ≤ Volume < ₹25,00,000 |
| Slab 3 | Volume ≥ ₹25,00,000 |

Volumes that exactly equal a slab boundary are assigned to the higher slab whose lower boundary they satisfy.

Slab definitions must not overlap.

---

## 8. Dual-Gate Eligibility & Financial Controls

### 8.1 Dual-Gate Eligibility Architecture

The pipeline enforces two independent validation gates:

```
[Raw Event] ──► [Gate 1: Calculation Eligibility] ──► Calculates Commission ──► [Gate 2: Payout Release Eligibility] ──► Released for Payout
                       │                                                              │
                       ▼ (Failed)                                                     ▼ (Failed)
               [Quarantine / Hold]                                            [Payout On-Hold Ledger]
```

* **Gate 1: Commission Calculation Eligibility**
  * Active partner empanelment status on disbursement/acquisition date.
  * Valid partner agreement matching transaction date.
  * Non-duplicate disbursement ID / account booking ID.
  * Valid, non-overlapping rate card mapping available.

* **Gate 2: Payout Release Eligibility**
  * Verified partner KYC and valid PAN (or synthetic equivalent).
  * Invoice taxable value and GST matching expected calculated values (where required by channel).
  * No explicit administrative/compliance hold flags.

### 8.2 Clawbacks, Adjustments, and Reversal Policy

When a loan foreclosure or cancellation event is ingested:

* **Clawback Window Check:** System verifies if the cancellation occurred within the contractual recovery period (e.g., within 90 days of disbursement).
* **Recovery Percentage:** Applies full (100%) or partial (e.g., 50%) recovery based on the product clawback rule.
* **Immutable Adjustment Record:** Generates a new adjustment entry in `fact_payout_ledger` linked to `source_event_id` and referencing `original_ledger_id`. Historical rows are **never deleted or modified**.
* **Superseded Calculation & Rule Change Policy:** When an existing financial calculation is superseded by a revised calculation rule or corrected source data, the pipeline preserves the original ledger posting and posts an explicit reversal/adjustment before posting the revised financial result. A new rule version must never silently create duplicate payable amounts.

### 8.3 Signed Ledger Posting Conventions

To prevent double-counting during reconciliation, `fact_payout_ledger.amount` uses an explicit signed amount convention:

| Posting Component (`posting_component`) | Financial Impact | Illustrative Ledger Amount | 
| ----- | ----- | ----- | 
| **`BASE_COMMISSION`** | Credit (Increase Payout) | Positive (`+`) | 
| **`INCENTIVE`** | Credit (Increase Payout) | Positive (`+`) | 
| **`CLAWBACK`** | Debit (Decrease Payout) | Negative (`-`) | 
| **`MANUAL_ADJUSTMENT`** | Credit or Debit | Positive (`+`) or Negative (`-`) | 
| **`TDS_DEDUCTION`** | Tax Deduction (Decrease Payout) | Negative (`-`) | 
| **`GST_PAYABLE`** | Tax Addition (Increase Payout) | Positive (`+`) | 

`tds_amount` and `gst_amount` in the ledger are provided as supporting attribute columns for reporting and must **not** be added again to the signed `amount` column during ledger summation.

#### Summary Aggregation Convention

In fact_payout_summary, component-level aggregate fields such as total_clawbacks and total_tds represent positive absolute amounts for reporting and presentation purposes.

The net payable formula in Section 7.1.4 applies the appropriate financial signs to these values.

In contrast, fact_payout_ledger.amount stores signed financial postings using the conventions defined above.

Reconciliation is performed by summing signed ledger amounts directly without applying additional sign transformations.

### 8.4 Deterministic Idempotency Key Design

To guarantee idempotent pipeline executions, every financial posting in `fact_payout_ledger` is assigned a deterministic key incorporating calculation component and group identifiers:

```math
\text{Idempotency Key} = \text{source\_event\_id} + \text{"\_"} + \text{posting\_component} + \text{"\_"} + \text{calculation\_group\_id} + \text{"\_"} + \text{payout\_cycle} + \text{"\_"} + \text{rule\_id} + \text{"\_"} + \text{rule\_version}
```

* **`source_event_id`:** Identifies the original business event (disbursement, acquisition, adjustment).
* **`posting_component`:** Distinguishes base commission, incentive, TDS, GST, clawback, etc.
* **`calculation_group_id`:** Deterministic group key (e.g., `partner_product_cycle_slab`) distinguishing aggregated volume postings or multiple incentive components.
* **`payout_cycle`:** Identifies the target processing period.
* **`rule_id and rule_version`:** Together identify the exact calculation rule version applied.

Retrying a batch process with identical source data uses deterministic idempotency keys and Delta Lake `MERGE` operations to prevent duplicate financial postings. Existing matching ledger entries remain unchanged for identical reprocessing.

If corrected source data or revised business rules produce a different financial result, the pipeline must preserve the original posting and create explicit reversal and replacement entries.

Financial amounts in previously committed ledger records must never be silently overwritten.

---

## 9. Exception Handling & Quarantine Strategy

Data rows failing validation are isolated in `fact_payout_exceptions` for investigation without stopping the overall pipeline execution.

> **Technical vs. Row-Level Failures:** All identifiable row-level validation failures are quarantined in `fact_payout_exceptions`. A batch is marked failed in `payout_batch_control` (`batch_status = FAILED`) only when a critical technical or operational error (e.g., storage failure, broken schema) prevents pipeline execution.

| Error Code | Trigger Condition | System Action | 
| ----- | ----- | ----- | 
| **`ERR_NO_PARTNER`** | Partner ID not found in partner master | Quarantined in `fact_payout_exceptions` | 
| **`ERR_RATE_NOT_FOUND`** | No rate card matches transaction date | Quarantined in `fact_payout_exceptions` | 
| **`ERR_RATE_OVERLAP`** | Multiple overlapping active rate cards found | Quarantined in `fact_payout_exceptions` | 
| **`ERR_DUPLICATE_TXN`** | Duplicate disbursement or account ID detected | Retains original; flags duplicate in `fact_payout_exceptions` | 
| **`ERR_CONTRACT_EXPIRED`** | Disbursement date outside agreement validity | Quarantined in `fact_payout_exceptions` | 
| **`ERR_KYC_PENDING`** | Partner KYC incomplete at payout gate | Commission calculated; Payout status set to `ON_HOLD` | 
| **`ERR_INVOICE_MISMATCH`** | Invoice taxable value / GST does not match calculated values | Payout status set to `INVOICE_HOLD` | 
| **`ERR_AMB_BELOW_THRESHOLD`** | CASA AMB does not reach minimum incentive threshold | Account logged; zero incentive posted (`eligibility_status` updated) | 

---

## 10. Final Target Schemas

(Detailed schema structures for `dim_channel_partner`, `fact_disbursements`, `fact_casa_acquisitions`, `fact_payout_ledger`, `fact_payout_summary`, `fact_payout_exceptions`, and `payout_batch_control` are defined in Section 6.2 with exact field names and grains.)

---

## 11. Project Verification and Test Suite

The data engineering implementation will be evaluated against the following mandatory verification criteria:

### 11.1 Core Verification Criteria

1. **Idempotency:** Re-running the pipeline on identical source files generates identical target outputs without creating duplicate rows in `fact_payout_ledger`.
2. **SCD Type 2 Integrity:** Changes in partner master attributes expire previous dimension rows (`is_current = False`) and insert new current records.
3. **Unambiguous Financial Reconciliation:**

```math
\sum_{i} \text{fact\_payout\_ledger.amount}_{\text{partner, cycle, } i} == \text{fact\_payout\_summary.net\_payable\_before\_carry\_forward}_{\text{partner, cycle}}
```

4. **100% Row-Level Exception Capture:** All identifiable row-level validation failures must be captured in `fact_payout_exceptions`. Critical technical failures must be recorded in `payout_batch_control` with `batch_status = FAILED`. Row-level errors must not unnecessarily stop processing of otherwise valid records.

### 11.2 Required Test Scenarios Matrix

The pipeline implementation will be validated against the following test cases:

| Test Scenario ID | Scenario Description | Expected Test Outcome | 
| ----- | ----- | ----- | 
| **`TC_01`** | Two partial disbursements for the same loan ID | Both valid events have distinct `source_event_id`s and are processed independently. | 
| **`TC_02`** | Overlapping effective dates in rate cards | Calculation halted for affected record; `ERR_RATE_OVERLAP` logged in exceptions. | 
| **`TC_03`** | Partner KYC status is `PENDING` | Gate 1 succeeds (commission calculated); Gate 2 holds payout (`payout_status = ON_HOLD`). | 
| **`TC_04`** | Invoice taxable value mismatch | Gate 1 succeeds; Gate 2 flags invoice mismatch (`payout_status = INVOICE_HOLD`). | 
| **`TC_05`** | CASA AMB below qualifying threshold | Account processed successfully; zero incentive posted (`ERR_AMB_BELOW_THRESHOLD`). | 
| **`TC_06`** | Same pipeline batch executed twice | Zero duplicate rows created in `fact_payout_ledger` due to `idempotency_key` deduplication. | 
| **`TC_07`** | Late-arriving clawback event | New negative adjustment posted with link to `original_ledger_id`; original ledger entry remains unchanged. | 
| **`TC_08`** | Negative net payout balance in cycle | `net_payable_after_carry_forward` set to $0$; negative balance populated in `amount_carried_forward`. | 
| **`TC_09`** | Tax rule effective-date modification | Pipeline selects the tax rule applicable to the configured effective-date basis and date. | 
| **`TC_10`** | Current cycle payout positive but less than opening carry-forward | Net payable after carry-forward remains $0$; remaining balance is correctly calculated in `amount_carried_forward`. | 
| **`TC_11`** | Calculation rule changes after original ledger posting | Original ledger posting is preserved; explicit reversal and replacement entries are posted with full audit trail. | 
| **`TC_12`** | Multiple incentive components for one partner and cycle | Distinct `calculation_group_id` values generate distinct, collision-free ledger postings. | 

---

## 12. Version History

| Version | Date | Summary of Changes | 
| ----- | ----- | ----- | 
| 1.0 | Initial Draft | Early business requirements draft. | 
| 2.0 | 24 Nov 2026 | Enterprise business requirements refinement. | 
| 2.1 | 24 Nov 2026 | Solo self-learning portfolio framing and non-affiliation disclaimer added. | 
| 2.2 | 24 Nov 2026 | **Scope Frozen Baseline:** Updated author metadata to Kota Vikramdev; aligned 6 products and 4 channels; defined table names and grains; added configurable tax bases and effective-date basis; explicit CASA calculation modes; carry-forward formulas; signed ledger conventions; immutable reversal/replacement policy; deterministic idempotency key design including rule_version; historical KYC guidance; slab-boundary definitions; summary-versus-ledger reconciliation rules; and enterprise-grade auditability controls. | 