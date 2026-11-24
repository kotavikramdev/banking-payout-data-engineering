# Banking Partner Commission and Payout Data Engineering Solution
## Business Requirements Document (BRD) — Version 2.0

| Document attribute | Details |
|---|---|
| Document status | Draft for business review |
| Version | 2.0 |
| Last updated | 24 November 2026 |
| Project type | Banking partner commission and payout data engineering |
| Primary audience | Business stakeholders, Business Analysts, Data Engineers, Finance, Operations and reviewers |

> **Document purpose:** This BRD defines the business context, requirements, process expectations, controls, assumptions and open questions for a learning-oriented data engineering implementation. It is a working draft, not an approved bank policy or production specification. All commercial, tax, compliance and operational rules must be confirmed with the relevant business owners.

---

## 1. Project Objective

The objective of this project is to develop an end-to-end banking partner commission and payout data engineering solution.

The solution will ingest partner master data, loan disbursement transactions, commission rate structures, incentive slabs, partner KYC information, invoice details and loan adjustment records from multiple source systems.

The pipeline will validate and process incoming data, determine commission and payout eligibility, calculate partner-wise and product-wise commissions, apply incentive structures, process clawbacks and reversals, and derive the payable amount after applicable tax deductions.

The solution will maintain financial transaction traceability, support payout reconciliation, and generate partner-wise and payout-cycle-wise reports. The resulting data will provide a foundation for financial reporting and business analysis, helping the bank monitor partner performance, commission expenses and payout operations.

## 2. Business Background and Problem Statement

Banks work with external sourcing partners such as Direct Selling Agents (DSAs), dealers, connectors and Business Correspondents (BCs) to source customers for banking products. A partner may earn commission or incentives according to the commercial agreement between the bank and that partner.

The bank must calculate commissions accurately, validate partner and transaction eligibility, account for subsequent adjustments, and ensure that payout amounts are supported by appropriate documentation and financial controls.

The process may involve data distributed across multiple source systems. Incomplete or inconsistent records, duplicate transactions, changing commission rates, late-arriving foreclosure or cancellation events, invoice mismatches and payout failures can create incorrect financial outcomes.

The proposed data engineering solution will bring the relevant data together, apply approved business rules, retain calculation history, identify exceptions and produce traceable outputs for downstream payout operations, reconciliation and reporting.

### 2.1 Key Business Challenges

- Data may be distributed across multiple source systems and file formats.
- Inconsistent or incomplete records may affect commission calculations.
- Duplicate loan or disbursement transactions may result in duplicate commission.
- Commission rates and partner agreements may change over time and require historical tracking.
- Late-arriving foreclosure and cancellation records may require adjustments to previously calculated commissions.
- Commission eligibility and payout release eligibility may differ.
- Invoice, tax and partner-documentation mismatches may delay payout.
- Payout records must be reconciled against financial and accounting records.
- Business users need visibility into rejected records, unresolved exceptions and payout status.

## 3. Stakeholders and Responsibilities

| Stakeholder | Primary responsibility / interest |
|---|---|
| Bank / Business team | Owns banking products, partner commercial arrangements and business policies. |
| Partner | Sources business for the bank and receives commission according to the applicable agreement. |
| Customer | Avails the bank's product or service. |
| Finance team | Reviews commission and payout amounts, accounting treatment and reconciliation. |
| Partner onboarding team | Manages partner empanelment, agreements and onboarding documentation. |
| Compliance team | Oversees applicable regulatory, tax and internal policy requirements. |
| Operations team | Manages operational exceptions, approvals and payout coordination. |
| Data / IT team | Maintains source integrations, data pipelines, data quality processes and reporting systems. |

## 4. Products and Channels in Scope

### 4.1 Products

The initial business scope focuses on the following loan products:

1. Personal Loans
2. Vehicle Loans
3. Home Loans

Other banking products, including CASA and Average Monthly Balance (AMB)-based arrangements, are not included in the initial loan-commission scope. They may be considered in a later phase if suitable source data and business rules are provided.

### 4.2 Partner Channels

The partner channels identified for this project are:

1. DSA — Direct Selling Agents
2. Dealers — tractor and other vehicle dealers
3. Connectors — other business-sourcing partners
4. BC — Business Correspondents

Commission structures and eligibility conditions may vary by partner, channel and financial product. The solution should therefore support configurable business rules rather than assume one calculation model for all partners.

## 5. Scope Boundaries

### 5.1 Proposed Initial Scope

The proposed initial implementation will prioritize:

- Ingestion of partner, agreement, product, loan disbursement and commission-rate data.
- Basic source-data validation and duplicate detection.
- Partner, agreement, product and transaction eligibility checks.
- Partner-wise and product-wise base commission calculation.
- Monthly volume-based incentive calculation, subject to confirmed slab rules.
- Identification and calculation of contractual clawback or adjustment events.
- Preservation of original commission and subsequent adjustment records.
- Commission summaries, exception outputs and reconciliation-oriented datasets.
- Business reports that can be generated from the processed data.

### 5.2 Capabilities Requiring Business/Data Confirmation

The following are included in the broader business vision but depend on the availability of source data, confirmed rules and implementation feasibility:

- Partner KYC and tax-document validation.
- Invoice validation and invoice-to-commission matching.
- TDS and other applicable tax calculations.
- Payout approval and status tracking.
- Ledger integration and accounting reconciliation.
- Partner statements and operational dashboards.

### 5.3 Proposed Exclusions for the Initial Data Engineering Build

Unless explicitly confirmed and supported by the available environment and source data, the initial implementation will not:

- Initiate or execute real bank payments.
- Replace the bank's payment processing platform.
- Replace a core banking system or general ledger.
- Provide real-time fraud detection.
- Determine or interpret tax law independently.
- Implement CASA/AMB commission arrangements.
- Claim production-grade regulatory compliance.

These boundaries are proposed to keep the first implementation achievable. They should be reviewed with the project owner before the scope is baselined.

## 6. Source Systems and Logical Datasets

The source data may be provided as CSV, Parquet or JSON files, or through other approved interfaces. The datasets below represent the logical information required by the business process; they are not confirmation that every source file currently exists.

| Logical dataset | Business purpose | Initial priority |
|---|---|---|
| Partner Master | Partner identity, type, channel and status | Must have |
| Customer Master | Customer reference information, where required | Supporting |
| Loan Application | Application and sanction details | Supporting |
| Loan Disbursement | Actual disbursed loan transactions | Must have |
| Product Master | Product identification and classification | Must have |
| Commission Rate Master | Partner/product/channel-wise commission rates | Must have |
| Incentive Slab Master | Volume-based incentive configuration | Must have if incentives are implemented |
| Partner Agreement | Contract validity, terms and commercial conditions | Must have |
| Partner KYC | KYC and tax-registration information | Required for payout validation, if available |
| Foreclosure / Cancellation | Events that may trigger contractual adjustments | Must have for clawback scope |
| Commission Transactions | Calculated commission and adjustment history | Pipeline output / downstream dataset |
| Partner Invoice | Invoice details for validation | Required for invoice scope |
| Payout Transactions | Payment instruction/status and outcome records | Required for payout tracking scope |
| TDS Transactions | Tax deduction details | Required for tax scope |
| Ledger Entries | Accounting records | Supporting / integration-dependent |
| Reconciliation Records | Financial matching results and exceptions | Supporting / output dataset |

**Source discovery requirement:** Before technical design is finalized, the actual files must be inspected to confirm their names, formats, schemas, grain, primary identifiers, date fields, data volumes, refresh frequency and data-quality characteristics. Dataset names in this BRD are logical names and may differ from actual file names.

## 7. Business Requirements — Commission Calculation

The commission calculation process shall determine commission based on approved commercial agreements between the bank and its partners.

### 7.1 Supported Calculation Capabilities

The solution should support, where applicable:

1. Partner-wise and product-wise commission rates.
2. Flat-rate and percentage-based commission structures.
3. Effective-dated commission rate selection.
4. Commission calculation using the contractually defined eligible amount.
5. Monthly partner-volume-based incentive calculations.
6. Retroactive and progressive incentive slab methodologies.
7. Commission adjustments arising from cancellations, foreclosures and other approved events.
8. Configurable rounding and precision rules.

### 7.2 Calculation Traceability

For each calculated commission, the solution should retain enough information to reproduce and explain the result, including:

- Source transaction identifier.
- Partner and product identifiers.
- Applicable agreement and rate references.
- Rate effective date or applicable rate period.
- Calculation basis and eligible amount.
- Calculation method and relevant slab, where applicable.
- Gross commission, adjustment and net commission amounts.
- Calculation timestamp and processing/run identifier.

### 7.3 Configuration and Exception Rules

- Missing, expired or overlapping commission-rate configurations must be identified.
- The pipeline must not silently assign an arbitrary rate when configuration is missing or conflicting.
- Commission calculation methods and eligibility conditions must be driven by approved business rules and partner agreements.
- Historical calculations must remain explainable when a rate or agreement changes.

## 8. Partner and Transaction Eligibility

The solution shall determine whether a loan transaction qualifies for commission and whether the resulting commission can be released for payout.

These are separate decisions:

### 8.1 Commission Eligibility

Commission eligibility may depend on:

- Partner identity and status.
- Partner agreement validity on the relevant business date.
- Product and sourcing-channel eligibility.
- Valid loan and disbursement references.
- Applicable commission-rate configuration.
- Transaction attribution to the partner.
- Other conditions defined in the partner agreement.

### 8.2 Payout Release Eligibility

Payout release may additionally depend on:

- Required partner KYC documentation being valid.
- PAN/GST details and their applicability being verified, as required.
- Invoice submission and approval, where required.
- Required business and finance approvals.
- Valid payout instructions and other bank-defined controls.

A transaction that qualifies for commission may remain pending payout until all required documentation and approval conditions are satisfied. GST registration should be treated as applicable only where required by the relevant business and tax rules.

## 9. Clawback, Cancellation and Reversal Requirements

The solution shall identify loan foreclosure, cancellation and other contractually defined events that may trigger commission recovery or adjustment.

Clawback eligibility must be determined using approved business rules, which may include:

1. Original loan disbursement date.
2. Relevant foreclosure or cancellation event date.
3. Partner-specific or product-specific clawback rules.
4. Applicable recovery window.
5. Full or partial recovery percentage.
6. Original commission amount and payment status.
7. Whether the original commission or related incentive is recoverable.

### 9.1 Transaction History

- Original commission transactions must be maintained separately from reversal and clawback transactions.
- For already-paid commissions, recovery should be recorded as a subsequent financial adjustment or recovery transaction.
- For unpaid commissions, the adjustment should be reflected in the outstanding payable balance.
- Original commission records must not be silently deleted or overwritten.
- Each adjustment must reference the original commission and the triggering business event.

A foreclosure or cancellation must not automatically be assumed to trigger a full clawback. The applicable partner agreement and approved business rules determine whether recovery applies and how it is calculated.

## 10. Invoice and Tax Requirements

Invoice and tax validation shall be performed where these capabilities are included in the agreed implementation scope and where the required source data and approved rules are available.

| Validation area | Business purpose |
|---|---|
| Invoice Number | Identify the submitted invoice |
| Partner ID | Confirm invoice ownership |
| Duplicate Invoice | Prevent duplicate invoice processing |
| Invoice Amount | Compare invoice amount with approved commission |
| Invoice Period | Verify the relevant payout cycle |
| PAN | Validate required tax identity details |
| GSTIN | Validate GST details and applicability, where relevant |
| Tax Calculation | Apply approved, effective-dated tax rules |
| Invoice Status | Track submitted, approved, rejected or other defined statuses |

TDS and GST are distinct tax concepts and must not be treated as interchangeable. Tax rates, thresholds, applicability and effective dates must be supplied or approved by the relevant business/tax owner. This project must not hardcode unverified tax assumptions.

## 11. Payout Processing and Status Tracking

After commission, documentation, invoice, tax and approval validations are completed, the resulting payable amount may be passed to the bank's designated payment processing process or system.

For the initial data engineering build, payout processing may be represented through payout records and status tracking. Actual payment execution is outside the initial scope unless a supported integration is explicitly approved.

The solution should capture, where available:

- Payout reference number.
- Partner reference.
- Payout cycle or period.
- Approved payable amount.
- Payment date.
- Partner bank-account reference (avoid exposing full account details in analytical outputs).
- Payment status.
- Payment failure reason.
- Retry or reprocessing history.
- Source commission references.

### 11.1 Proposed Payout Statuses

| Status | Meaning |
|---|---|
| Calculated | Commission has been calculated |
| Pending Approval | Awaiting required approval |
| Approved | Approved for payout processing |
| Processing | Payment has been initiated by the designated process |
| Paid | Payment has been confirmed as successful |
| Failed | Payment attempt failed |
| On Hold | Temporarily blocked from proceeding |
| Rejected | Not approved for payout |

Status definitions and permitted transitions must be confirmed with the business owner. Retries must be controlled to prevent duplicate financial impact.

## 12. Reporting and Dashboard Requirements

The solution should provide reporting datasets or outputs that support business monitoring and operational review.

### 12.1 Required Reports

| Report | Business purpose |
|---|---|
| Partner-wise Commission Report | Understand commission earned by each partner |
| Product-wise Commission Report | Compare commission by loan product |
| Monthly Payout Report | Monitor payout cycles |
| Clawback Report | Monitor commission recovery and adjustments |
| Pending Payout Report | Identify amounts awaiting payout |
| Failed Payout Report | Identify payment failures |
| Partner Performance Report | Measure sourcing and disbursement performance |
| Reconciliation Report | Identify financial mismatches |
| TDS Report | Track applicable tax deductions |
| Exception Report | Identify invalid, incomplete or conflicting records |

### 12.2 Proposed Dashboard KPIs

- **Total Eligible Disbursement Volume:** Sum of disbursements eligible for commission calculation.
- **Total Base Commission:** Commission calculated using standard rates.
- **Total Incentive Commission:** Additional commission earned through approved incentive slabs.
- **Total Clawback:** Commission recovered or adjusted under approved rules.
- **Net Commission Payable:** Commission after applicable commission adjustments.
- **Total TDS:** Applicable tax deducted at source, where in scope.
- **Total Payout Amount:** Amount paid or scheduled for payment, with the status clearly identified.
- **Number of Active Partners:** Count of partners meeting the agreed active-partner definition.
- **Number of Failed Payouts:** Count of payout transactions with failed status.
- **Number of Rejected Transactions:** Count of records rejected during validation.

Metric definitions, aggregation grain and reporting period must be agreed before dashboards are treated as authoritative. In particular, commission payable, net payable after tax and amount actually paid should be reported as distinct measures.

## 13. Financial, Data Quality and Audit Controls

The solution must implement financial and operational controls to support commission accuracy, prevent duplicate financial processing and provide auditability.

### 13.1 Financial Controls

| Control | Expected behaviour |
|---|---|
| Duplicate Transaction Detection | Prevent duplicate commission calculation and duplicate financial impact. |
| Partner Validation | Reject or hold transactions associated with invalid or inactive partners, according to the approved rule. |
| Contract Validation | Prevent commission calculation where the required agreement is invalid for the relevant date. |
| Rate Validation | Identify missing, incorrect or conflicting commission-rate configurations. |
| Amount Validation | Detect missing, invalid, negative, zero or unreasonable transaction amounts according to approved rules. |
| Invoice Validation | Identify duplicate invoices and mismatches against approved commission. |
| Clawback Validation | Prevent recovery beyond applicable contractual limits. |
| Payout Validation | Prevent duplicate payout processing and unauthorized payment activity. |
| Reconciliation Control | Compare commission, invoice, payout and ledger records where those records are available. |
| Audit Trail | Maintain history of calculations, approvals, modifications and payment-related transactions. |

### 13.2 Data Quality Controls

Invalid, incomplete or inconsistent records must not be silently discarded. They must be captured in an Exception or Rejected Records dataset for investigation and remediation.

The system should validate, at minimum:

- Missing Partner ID.
- Invalid or missing Loan ID.
- Missing or invalid Disbursement Amount.
- Invalid Transaction Date.
- Duplicate Source Transaction.
- Invalid or missing Product Mapping.
- Missing Commission Rate Mapping.
- Missing Agreement Reference.
- Invalid Customer Reference, where customer reference is required.
- Invalid or missing partner attribution.

The exact validation rules, rejection thresholds and treatment of zero or negative values must be confirmed against the source data and business policy.

### 13.3 Audit and Reprocessing

Records failing validation should:

- Be excluded from downstream commission or payout processing until resolved.
- Be stored with a clear exception category and reason.
- Be available for operational review and reporting.
- Support correction and controlled reprocessing.
- Retain the original source reference and processing history.
- Avoid duplicate commission or payout when reprocessed.

## 14. End-to-End Business Process

The expected high-level lifecycle is described below. The exact sequence may vary based on the bank's operating model and the availability of source data.

### Step 1 — Source Data Acquisition

Acquire the relevant datasets, such as Partner Master, Customer Master, Loan Application, Loan Disbursement, Product Master, Commission Rate Master, Incentive Slab Master, Partner Agreement, Partner KYC and adjustment events. Invoice, payout, tax, ledger and reconciliation datasets are included where those capabilities are in scope.

### Step 2 — Data Validation and Standardization

Validate file structure, required fields, data types, dates, identifiers, duplicates and reference mappings. Preserve source records and route invalid records to the exception process.

### Step 3 — Eligibility Assessment

Validate partner, agreement, product, loan and disbursement details. Determine commission eligibility separately from payout release eligibility.

### Step 4 — Commission Calculation

Calculate base commission using the applicable approved rate and eligible amount. Calculate incentives and adjustments only after the corresponding business rules have been confirmed.

### Step 5 — Adjustment and Clawback Processing

Identify qualifying cancellation, foreclosure or other adjustment events. Create linked adjustment transactions without overwriting original commission history.

### Step 6 — Invoice, Tax and Approval Validation

Where included in scope, validate invoice information, partner tax details, applicable tax rules and required approvals. Derive the approved payable amount.

### Step 7 — Payout Status and Reconciliation

Record payout instructions or outcomes received from the designated payment process. Track statuses and reconcile available commission, payout and ledger information.

### Step 8 — Reporting

Publish partner-wise, product-wise, payout-cycle-wise, exception and reconciliation outputs for business and operational review.

## 15. Exception Management

The solution shall identify, track and manage business and data exceptions to protect financial accuracy and operational control.

### 15.1 Exception Management Principles

- Exceptions must be captured and logged.
- Exceptions must not be silently discarded.
- Financial impact must be prevented until the relevant issue is resolved.
- Exceptions must be available for business review and remediation.
- Resolution and reprocessing history must be retained.

### 15.2 Exception Scenarios

| Scenario | Expected system behaviour |
|---|---|
| Partner ID Missing | Quarantine or reject the record for investigation. |
| Partner Inactive | Mark the transaction ineligible according to the applicable rule. |
| Commission Rate Missing | Raise a configuration exception and suspend calculation for the affected record. |
| Multiple Applicable Rates | Flag conflicting configuration for business review. |
| Loan Cancelled | Apply the approved contractual cancellation adjustment, if applicable. |
| KYC Expired | Hold payout where valid KYC is a payout requirement. |
| Invoice Mismatch | Route for investigation and validation. |
| Payment Failed | Record failure and support controlled reprocessing. |
| Duplicate Source Transaction | Prevent duplicate commission and duplicate financial impact. |
| Missing Agreement | Hold or mark ineligible until agreement validation is completed. |
| Invalid Product Mapping | Route to exception handling for correction. |
| Invalid Disbursement Amount | Reject or quarantine until corrected under the agreed rule. |
| Invalid Transaction Date | Capture as an exception and prevent affected processing. |
| Missing Required Tax Information | Hold payout where the information is required. |

### 15.3 Exception Dataset Fields

The exception dataset should contain, where available:

- Source system and source file reference.
- Source transaction identifier.
- Partner and loan identifiers.
- Exception category and description.
- Detection timestamp.
- Processing run identifier.
- Processing and resolution status.
- Resolution comments and resolved timestamp.
- Reprocessing reference.
- Audit information.

## 16. Non-Functional Requirements

### 16.1 Security and Access Control

- Access to commission and payout information shall be restricted to authorized users.
- Sensitive financial and personal data shall be protected from unauthorized access.
- Data shall be securely stored and transmitted using controls supported by the implementation environment.
- User and system actions shall be authenticated and traceable.
- Analytical outputs should avoid exposing full bank-account details or unnecessary personal information.

### 16.2 Role-Based Access Control

- Users should access information relevant to their assigned role.
- Administrative actions should be restricted to authorized personnel.
- Approval responsibilities should be segregated where supported by the operating model.

### 16.3 Data Accuracy and Integrity

- Commission calculations shall be consistent with approved business rules.
- Duplicate financial processing shall be prevented.
- Validation rules shall support data completeness, consistency and referential integrity.

### 16.4 Auditability and Traceability

- Calculations should be reproducible from retained source data and rule references.
- Financial outputs should be traceable to originating source records.
- Changes to business-rule configurations should be auditable.
- Original transactions and subsequent adjustments should remain distinguishable.

### 16.5 Reliability and Recovery

- Processing should be repeatable and support controlled restart.
- Failures should be logged with actionable details.
- Reprocessing should not create duplicate financial outcomes.
- Historical processing results should remain identifiable by run or batch.

### 16.6 Performance and Timeliness

- Processing should complete within business timelines agreed for the project.
- Reporting data should be available within agreed reporting windows.
- Performance targets must be set after source volume and refresh frequency are understood.

### 16.7 Monitoring

- Data validation failures should be measurable and reportable.
- Pipeline failures should be surfaced for investigation.
- Reconciliation exceptions should be highlighted.
- Processing status and record counts should be available for each run.

### 16.8 Historical Retention

- Historical commission, payout, tax and reconciliation data should be retained according to the approved retention policy.
- Historical records should remain available for reporting and audit needs.
- The actual retention period is an open business/compliance decision.

## 17. Assumptions and Open Questions

This section separates working assumptions from questions that require business confirmation. Assumptions are not approved policy until confirmed.

### 17.1 Working Assumptions

| ID | Working assumption | Validation needed |
|---|---|---|
| A01 | Commission is calculated on the disbursed loan amount. | Confirm whether the basis is gross disbursement, net disbursement or another contract-defined amount. |
| A02 | Commission is calculated periodically using a business-defined payout cycle. | Confirm cycle frequency and cut-off rules. |
| A03 | Partner eligibility depends on partner status, agreement validity and applicable onboarding checks. | Confirm date basis and required checks. |
| A04 | Only eligible and validated transactions proceed to payout consideration. | Confirm exception and approval handling. |
| A05 | Clawbacks may be triggered by foreclosure, cancellation or other defined events. | Confirm event types, windows and recovery percentages. |
| A06 | Applicable tax deductions are considered before final payout. | Confirm tax treatment with the responsible business/tax owner. |

### 17.2 Open Business Questions

| ID | Open question |
|---|---|
| Q01 | Are incentive slabs calculated using progressive or retroactive logic? |
| Q02 | Are slab calculations performed partner-wise, partner-product-wise or at another aggregation level? |
| Q03 | Does a qualifying foreclosure reverse base commission, incentive commission or both? |
| Q04 | Can negative commission balances be carried forward to future payout cycles? |
| Q05 | Can commission be paid before invoice submission or approval? |
| Q06 | How should partial loan disbursements be handled? |
| Q07 | What tax rules apply to each partner category, and who supplies the approved rules? |
| Q08 | Are commission rates effective-dated, and how are historical rate changes handled? |
| Q09 | What approval levels are required before payout? |
| Q10 | Who owns reconciliation exception resolution? |
| Q11 | How should partner mergers, transfers or ownership changes be handled? |
| Q12 | What is the required retention period for commission and payout records? |
| Q13 | What is the source-of-truth system for partner, agreement, loan and payout status? |
| Q14 | What is the expected data refresh frequency and payout-cycle cut-off? |
| Q15 | What unique business keys identify a loan, disbursement, commission and payout transaction? |

### 17.3 Items Requiring Business Sign-Off

The following areas require confirmation before detailed solution design is baselined:

- Commission calculation methodology and calculation basis.
- Incentive slab methodology and aggregation level.
- Clawback and cancellation rules.
- Payout frequency and cut-off.
- Tax treatment and applicable documentation.
- Invoice requirements.
- Reconciliation ownership and matching rules.
- Exception resolution and approval process.
- Record retention policy.
- Regulatory, compliance and security requirements.
- Source systems and authoritative identifiers.

## 18. Business Glossary

| Term | Meaning in this project |
|---|---|
| Partner | External entity that sources business for the bank under an arrangement. |
| DSA | Direct Selling Agent. |
| BC | Business Correspondent. |
| Disbursement | Release of loan funds by the bank; distinct from application or sanction. |
| Commission | Amount earned by a partner under the applicable commercial arrangement. |
| Incentive | Additional amount earned when defined performance or volume conditions are met. |
| Clawback | Recovery or adjustment of previously calculated or paid commission under contractual rules. |
| Commission eligibility | Whether a transaction qualifies for commission under business rules. |
| Payout release eligibility | Whether an otherwise eligible commission can proceed to payment. |
| TDS | Tax deducted at source, where applicable. |
| Reconciliation | Comparison of related records to identify matched and unmatched financial amounts. |
| Effective date | Date from which a rate, agreement or rule is valid. |

## 19. Acceptance Criteria for the Business Requirements

This BRD may be considered ready for detailed solution design when:

1. The business owner confirms the initial products, channels and scope boundaries.
2. Actual source files and their business meaning are identified.
3. Required identifiers and transaction grain are understood.
4. Commission basis, rate selection and effective-date rules are documented.
5. Incentive and clawback rules are either confirmed or explicitly excluded from the first implementation.
6. Commission eligibility and payout release eligibility are clearly distinguished.
7. Required outputs, reports and metric definitions are agreed.
8. Exception handling, reconciliation ownership and audit expectations are documented.
9. Open questions are assigned to owners or recorded as explicit implementation assumptions.
10. The project owner approves the BRD baseline.

## 20. Change History

| Version | Date | Summary |
|---|---|---|
| 1.0 | Initial draft | Initial business requirements prepared by the project author. |
| 2.0 | 24 November 2026 | Refined structure, clarified scope, separated assumptions from confirmed rules, strengthened eligibility, clawback, data quality, exception, audit and acceptance requirements. |

---

**Next project gate:** Review this draft against the actual sample datasets. Confirm which logical datasets are available, map their columns to the business requirements, and update the open questions before finalizing the BRD baseline.