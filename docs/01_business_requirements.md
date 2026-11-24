# Banking Payout System Data Engineering Project - Business Requirement Document

## 1. Objective of the Project
The objective of this project is to develop an end-to-end banking partner commission and payout data engineering solution.

The system will ingest partner master data, loan disbursement transactions, commission rate structures, incentive slabs, partner KYC information, invoice details and loan adjustment records from multiple source systems.

The pipeline will process and validate the incoming data, determine partner eligibility, calculate product-wise and partner-wise commissions, apply incentive structures, handle clawbacks and reversals, and derive the final payable amount after applicable tax deductions.

The solution will also maintain financial transaction traceability, support payout reconciliation, and generate partner-wise and payout-cycle-wise reporting.

The processed data will provide a foundation for financial reporting and business analysis to help the bank monitor partner performance, commission expenses and payout operations.

## 2. Business Problem
The Bank has the products like Business loans for running the business like Personal Loans, Home Loans, Vehicle Loans etc. The bank procures the partners like DSAs, Dealers or Connectors to source their business and sell the loan products to end customers. Upon sourcing the business, partners will get commission according to the contract. Bank needs to ensure proper commission computation while processing each loan transaction grouped by partner and product type, then eventually process the payout both basic and incentive payouts for partners to continue growing business while maintaining auditability and traceability. This requires an end-to-end data engineering solution to assess partners, loan transactions, kyc validation, empanelment, commission computation including clawback and reversals, payout invoicing, processing and auditability.
- Data may be distributed across multiple source systems.
- Inconsistent or incomplete records may affect commission calculations.
- Duplicate loan transactions may result in duplicate commission.
- Changes in commission rates need historical tracking.
- Late-arriving foreclosure and cancellation records may require adjustments to previously calculated commissions.
- Payout records must be reconciled against financial records.

## 3. Stakeholders
This includes primarily the following stakeholders.
1. Bank - owns the loan products, sanctions loans and disburses the amount, commission and calculation, final payout.
2. Partner - sources the bank's products to the end customers, get their commission according to the agreed contractual commission slab.
3. Customer - person who avails the loan from the bank.
4. Finance team - validates the payouts, accounting and reconciliation.
5. Partner onboarding team - manages empanelment and KYC.
6. Compliance team - overseas applicable regulatory and policy requirements.
7. Operations team - Handles exceptions, approvals and payout processing.
8. Data / IT team - maintains data pipelines and reporting systems.

## 4. Products Covered
Loan Products covered in the Bank are as follows:
1. Personal Loans
2. Vehicle Loans
3. Home Loans

The partners may associated with Bank can source business based on the above listed products.

## 5. Channels Covered
Partners can be categorized into multiple channels, some of them are listed below:
1. DSA - Direct Selling Agents
2. Dealers - Tractor and other Vehicle Dealers
3. Connectors - Other Sourcing Business
4. BC - Business Correspondents

Commission structures and eligibility conditions may vary based on partner type, sourcing channel and financial product. The system should support configurable commission structures rather than assuming a single calculation model.

## 6. Source systems and datasets.
The source datasets can be CSV/Parquet/JSON based files which can consists of the following:

| Dataset | Purpose | Priority |
|----------|---------|----------|
| Partner Master | Partner identity and status | Must have |
| Customer Master | Customer information | Supporting |
| Loan Application | Application and sanction details | Must have |
| Loan Disbursement | Actual disbursed transactions | Must have |
| Product Master | Product classification | Must have |
| Commission Rate Master | Partner/product-wise rates | Must have |
| Incentive Slab Master | Volume-based incentives | Must have |
| Partner Agreement | Contract validity and terms | Must have |
| Partner KYC | KYC and tax registration validation | Must have |
| Foreclosure / Cancellation | Clawback triggers | Must have |
| Commission Transactions | Calculated commission history | Must have |
| Partner Invoice | Invoice validation | Must have |
| Payout Transactions | Actual payout records | Must have |
| TDS Transactions | Tax deduction details | Must have |
| Ledger Entries | Accounting records | Supporting |
| Reconciliation Records | Financial matching and exceptions | Supporting |

## 7. Commission calculation rules.
The commission calculation engine should determine commission based on approved commercial agreements between the bank and its partners.
The system should support:
1. Partner-wise and product-wise commission rates.
2. Flat-rate and percentage-based commission structures.
3. Effective-dated commission rate selection.
4. Commission calculation based on the contractually defined eligible amount.
5. Monthly partner volume-based incentive calculations.
6. Retroactive and progressive incentive slab methodologies, where applicable.
7. Commission adjustments due to cancellations, foreclosures and other approved events.
8. Configurable rounding and precision rules.

The system must retain the applicable commission rate, calculation basis, source transaction reference and calculation result for auditability.

Missing, expired or overlapping commission rate configurations must be identified and handled through defined exception processes rather than silently assigned an arbitrary rate.

All commission calculation methods and eligibility conditions must be driven by approved business rules and partner agreements.

## 8. Partner eligibility rules.
Payout must be credited to the partner only if the partner empanelment contract is valid as on the transaction date and the KYC details, GST are verified. Then only, partner is eligible for payouts.

The system should separately determine commission eligibility and payout release eligibility. A transaction that qualifies for commission may remain pending payout until all required partner documentation and approval conditions are satisfied.

## 9. Clawback and cancellation rules.
The system should identify loan foreclosure, cancellation and other contractually defined events that may trigger commission recovery or adjustment.

Clawback eligibility must be determined based on:

1. Original loan disbursement date.
2. Relevant foreclosure or cancellation event date.
3. Partner-specific or product-specific clawback rules.
4. Applicable recovery window.
5. Full or partial recovery percentage.
6. Original commission amount and payment status.

The system must maintain original commission transactions separately from reversal and clawback transactions.

For already-paid commissions, recovery should be reflected as a subsequent financial adjustment or recovery transaction.

For unpaid commissions, the adjustment should be reflected in the outstanding payable balance.

Original commission records must not be silently deleted or overwritten.

## 10. Tax and invoice validation.
The below mentioned details needs to be validated while processing the payout to the partner.

| Validation | Purpose |
|------------|---------|
| Invoice Number | Identify invoice |
| Partner ID | Confirm invoice ownership |
| Duplicate Invoice | Prevent duplicate processing |
| Invoice Amount | Match against approved commission |
| Invoice Period | Verify payout cycle |
| PAN | Tax validation |
| GSTIN | Validate GST applicability and details |
| Tax Calculation | Apply applicable tax rules |
| Invoice Status | Track submitted, approved, or rejected |

## 11. Payout processing.
Once everything is validated, the partner is eligible for the payment, the payout has to be processed throught the payment gateway and it needs to be credited in the partner account. Post that the same has to be accounted for auditability and traceability.

The payout processing status should be as follows along with the payout reference number, payment date, partner bank account reference,payment failure reason, retry handling, duplicate payout prevention.

| Status | Meaning |
|---------|---------|
| Calculated | Commission calculated |
| Pending Approval | Awaiting approval |
| Approved | Ready for payout |
| Processing | Payment initiated |
| Paid | Successfully credited |
| Failed | Payment failed |
| On Hold | Temporarily blocked |
| Rejected | Not approved |

## 12. Reporting requirements.
Following are the reporting requirements.

| Report | Business Purpose |
|---------|------------------|
| Partner-wise Commission Report | Understand commission earned by each partner |
| Product-wise Commission Report | Compare commission by loan product |
| Monthly Payout Report | Monitor payout cycles |
| Clawback Report | Monitor commission recovery |
| Pending Payout Report | Identify unpaid amounts |
| Failed Payout Report | Identify payment failures |
| Partner Performance Report | Measure sourcing and disbursement performance |
| Reconciliation Report | Identify financial mismatches |
| TDS Report | Track applicable tax deductions |
| Exception Report | Identify invalid and incomplete records |

Also the business dashboard with the following KPIs:

### Dashboard KPIs

- **Total Eligible Disbursement Volume** - Sum of all disbursements eligible for commission calculation.
- **Total Base Commission** - Commission calculated using standard rates.
- **Total Incentive Commission** - Additional commission earned through incentive slabs.
- **Total Clawback** - Commission recovered due to foreclosure or cancellation.
- **Net Payable Commission** - Final commission payable after adjustments.
- **Total TDS** - Total tax deducted at source.
- **Total Payout Amount** - Amount disbursed to partners after deductions.
- **Number of Active Partners** - Count of partners eligible for commission.
- **Number of Failed Payouts** - Count of payout transactions that failed.
- **Number of Transactions Rejected During Validation** - Count of records rejected due to validation errors.

## 13. Financial controls.
The solution must implement financial and operational controls to ensure commission accuracy, prevent duplicate payments, and support audit and compliance requirements.

| Control | Expected Behaviour |
|----------|-------------------|
| Duplicate Transaction Detection | Prevent duplicate commission calculation and payment processing. |
| Partner Validation | Reject or hold transactions associated with invalid or inactive partners. |
| Contract Validation | Prevent commission calculation for expired, inactive, or invalid partner agreements. |
| Rate Validation | Identify missing, incorrect, or conflicting commission rate configurations. |
| Amount Validation | Detect negative, zero, or unreasonable transaction amounts. |
| Invoice Validation | Identify duplicate invoices and mismatches between invoice values and approved commission amounts. |
| Clawback Validation | Prevent recovery of commission beyond applicable clawback limits. |
| Payout Validation | Prevent duplicate payout execution and unauthorized payment processing. |
| Reconciliation Control | Reconcile commission, payout, invoice, and ledger records to identify discrepancies. |
| Audit Trail | Maintain complete history of calculations, approvals, modifications, and payment transactions. |

### Data Quality Controls

In addition to financial controls, the solution must implement data quality validations to ensure that only valid and complete transactions are processed for commission calculation and payout.

Invalid, incomplete, or inconsistent records must not be discarded. Such records must be captured in an **Exception Dataset** or **Rejected Records Dataset** for investigation and remediation.

The system should validate the following conditions:

- Missing Partner ID
- Invalid Loan ID
- Null or missing Disbursement Amount
- Invalid Transaction Date
- Duplicate Source Transaction
- Invalid Product Mapping
- Missing Product Identifier
- Missing Commission Rate Mapping
- Missing Agreement Reference
- Invalid Customer Reference

### Exception Management

Records failing validation checks should:

- Be excluded from commission calculation and payout processing.
- Be stored in an Exception or Rejected Records dataset.
- Capture the reason for rejection.
- Support reporting and operational review.
- Allow correction and reprocessing after data issues are resolved.
- Maintain a complete audit trail of validation failures and remediation actions.

## 14. End-to-End Business Process

The commission management process encompasses the complete lifecycle from transaction sourcing through commission calculation, validation, payout, reconciliation, and reporting.

### Process Flow

#### 1. Source Systems and Data Acquisition

Business data is sourced from the following datasets:

- Partner Master
- Customer Master
- Loan Application
- Loan Disbursement
- Product Master
- Commission Rate Master
- Incentive Slab Master
- Partner Agreement
- Partner KYC
- Foreclosure / Cancellation
- Partner Invoice
- Payout Transactions
- TDS Transactions
- Ledger Entries
- Reconciliation Records

#### 2. Data Validation and Eligibility Assessment

The system validates source data and determines eligibility for commission processing.

Key validations include:

- Data quality validation
- Partner eligibility validation
- Agreement validity validation
- KYC validation
- Product validation
- Loan validation
- Disbursement validation
- Duplicate transaction detection

Only eligible transactions proceed to commission calculation.

#### 3. Commission Calculation

Commission is calculated based on approved business rules.

Calculation components include:

- Base commission
- Product-specific commission
- Volume incentives
- Performance incentives
- Clawback adjustments
- Cancellation adjustments

The calculated commission amount becomes the basis for payout processing.

#### 4. Invoice, Tax, and Payout Validation

Before payment execution, financial validations are performed.

Key activities include:

- Invoice validation
- Invoice ownership verification
- Tax applicability determination
- PAN validation
- GST validation
- TDS calculation
- Net payable amount calculation
- Approval workflow validation

Only approved transactions proceed for payment.

#### 5. Payout and Reconciliation

Approved commissions are disbursed to partners.

Key activities include:

- Payment execution
- Payout status tracking
- Ledger posting
- Financial reconciliation
- Exception management
- Audit trail creation

#### 6. Business Reporting

The solution generates operational and financial reports to support business monitoring and decision-making.

Typical reports include:

- Partner-wise commission report
- Product-wise commission report
- Monthly payout report
- Clawback report
- Pending payout report
- Failed payout report
- Partner performance report
- Reconciliation report
- TDS report
- Exception report

## 15. Exception Handling

The solution shall identify, track, and manage business exceptions to ensure financial accuracy and operational control.

### Exception Management Principles

- Exceptions must be captured and logged.
- Exceptions must not be silently discarded.
- Financial impact must be prevented until resolution.
- Exceptions should be available for business review and remediation.
- Complete audit history must be maintained.

### Exception Scenarios

| Scenario | Expected System Behaviour |
|-----------|--------------------------|
| Partner ID Missing | Reject or quarantine the record for investigation. |
| Partner Inactive | Mark the transaction as ineligible for commission. |
| Commission Rate Missing | Raise a configuration exception and suspend processing. |
| Multiple Applicable Rates | Flag a conflicting configuration for business review. |
| Loan Cancelled | Apply contractual cancellation adjustment or clawback rule. |
| KYC Expired | Hold payout until KYC compliance is restored. |
| Invoice Mismatch | Route the transaction for investigation and validation. |
| Payment Failed | Record the failure and support controlled reprocessing. |
| Duplicate Source Transaction | Prevent duplicate commission and duplicate financial impact. |
| Missing Agreement | Mark the transaction ineligible until agreement validation is completed. |
| Invalid Product Mapping | Route the transaction to exception handling for correction. |
| Invalid Disbursement Amount | Reject the transaction until corrected. |
| Invalid Transaction Date | Capture as an exception and prevent processing. |
| Missing Tax Information | Hold payout until required tax details are provided. |

### Exception Dataset Requirements

The solution shall maintain a dedicated exception dataset containing:

- Source transaction identifier
- Exception category
- Exception description
- Detection timestamp
- Processing status
- Resolution status
- Resolution comments
- Audit information

## 16. Non-Functional Requirements

The commission management solution shall satisfy the following non-functional requirements.

### Security

- Access to commission and payout information shall be restricted to authorized users.
- Sensitive financial data shall be protected from unauthorized access.
- All business-critical data shall be securely stored and transmitted.
- User actions shall be authenticated and traceable.

### Role-Based Access Control

- Users shall only access information relevant to their assigned role.
- Administrative actions shall be restricted to authorized personnel.
- Approval actions shall be segregated according to business responsibilities.

### Data Accuracy

- Commission calculations shall be accurate and consistent with approved business rules.
- The solution shall prevent duplicate financial processing.
- Validation rules shall ensure data completeness and integrity.

### Auditability and Traceability

- All calculations shall be reproducible.
- All financial transactions shall be traceable to originating source records.
- All changes to business rules and configurations shall be auditable.
- Complete transaction history shall be maintained.

### Reliability

- The solution shall support reliable and repeatable processing.
- Processing failures shall be logged and recoverable.
- Critical business processes shall support restart and reprocessing capabilities.

### Performance

- The solution shall support timely commission calculation and payout processing.
- Reporting shall be available within agreed business timelines.
- Data validation and reconciliation processes shall complete within operational service windows.

### Monitoring and Alerting

- Validation failures shall be monitored.
- Processing failures shall generate alerts.
- Data quality issues shall be reported for remediation.
- Reconciliation exceptions shall be highlighted for investigation.

### Historical Data Retention

- Historical commission data shall be retained for audit and regulatory purposes.
- Historical payout, tax, and reconciliation records shall remain accessible.
- Archived records shall support reporting and audit requests.

### Recovery and Reprocessing

- Failed transactions shall support controlled reprocessing.
- Exception records shall support correction and resubmission.
- Recovery processes shall preserve auditability and financial integrity.

### Business Requirement Statement

The solution must ensure that commission and payout calculations are reproducible, auditable, and traceable to their originating source transactions and applicable business rules.

## 17. Assumptions and Open Questions

This section captures assumptions currently used in the business requirements and identifies outstanding questions requiring business clarification.

### Assumptions

| Type | Description |
|--------|-------------|
| Assumption | Commission is calculated on disbursed loan amount. |
| Assumption | Commission calculation is performed periodically based on business-defined payout cycles. |
| Assumption | Partner eligibility is determined using partner status, agreement validity, and KYC status. |
| Assumption | Only eligible and validated transactions are considered for payout processing. |
| Assumption | Clawbacks are triggered by foreclosure, cancellation, or other defined business events. |
| Assumption | Tax deductions are applied before final payout execution. |

### Open Questions

| Type | Question |
|--------|----------|
| Open Question | Are incentive slabs calculated using progressive or retroactive logic? |
| Open Question | Are slab calculations performed partner-wise or partner-product-wise? |
| Open Question | Does foreclosure reverse the base commission, incentive commission, or both? |
| Open Question | Can negative commission balances be carried forward to future payout cycles? |
| Open Question | Can commission be paid before invoice submission or approval? |
| Open Question | How should partial loan disbursements be handled during commission calculation? |
| Open Question | What are the applicable tax rules for different partner categories? |
| Open Question | Are commission rates effective-dated, and how should historical rate changes be handled? |
| Open Question | What approval levels are required before payout execution? |
| Open Question | What is the business process for resolving reconciliation exceptions? |
| Open Question | How should partner mergers, transfers, or ownership changes be handled? |
| Open Question | What is the required retention period for commission and payout records? |

### Items Requiring Business Confirmation

The following areas require formal business confirmation before finalization of detailed solution design:

- Commission calculation methodology
- Incentive slab logic
- Clawback rules
- Payout frequency
- Tax treatment
- Invoice requirements
- Reconciliation ownership
- Exception resolution process
- Record retention policy
- Regulatory and compliance requirements