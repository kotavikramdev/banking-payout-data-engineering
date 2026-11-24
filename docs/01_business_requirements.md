# Banking Partner Commission and Payout Data Engineering Solution
## Business Requirements Document (BRD) — Version 2.1 (Educational / Portfolio Project)

| Document Attribute | Details |
|---|---|
| Document Status | Self-Learning Data Engineering Specification |
| Version | 2.1 |
| Last Updated | 24 November 2026 |
| Project Type | Educational Data Engineering Project (Solo Implementation) |
| Author & Developer | Independent Data Engineering Learner |
| Target Audience | Personal Portfolio, Technical Reviewers, Data Engineering Evaluators |

---

> ### ⚠️ DISCLAIMER & NON-AFFILIATION NOTICE
> **Educational & Self-Learning Purpose Only:** This document and the associated data engineering project are strictly created for self-learning, skill development, and personal portfolio demonstration purposes. 
>
> **No Real Bank Affiliation:** This project **does not represent, refer to, or use proprietary information from any real banking institution, financial service provider, or commercial entity**. All company names, banking workflows, commission structures, tax rules, loan schemas, and transaction datasets described in this document are **100% synthetic, hypothetical, and designed for learning data pipeline engineering concepts**.

---

## 1. Project Objective and Portfolio Goals

### 1.1 Project Objective
The objective of this project is to design, build, and test an end-to-end **Banking Partner Commission and Payout Data Engineering Solution**. 

The pipeline ingests multi-source banking datasets (partner master data, loan disbursements, rate cards, incentive slabs, partner KYC, invoices, and loan adjustment records), validates incoming data quality, calculates multi-tiered commission structures, processes contractual clawbacks/reversals, applies tax logic (TDS), and outputs reconciled financial datasets ready for downstream reporting.

### 1.2 Learning & Skill Development Objectives
As a single-handed self-learning project, this BRD serves as the functional design reference to demonstrate proficiency in:
- **Data Engineering Design:** Translating complex, domain-specific financial rules into data transformation models.
- **Data Quality & Exception Handling:** Implementing robust quarantine pipelines for bad, incomplete, or duplicate records.
- **SCD & Historical Tracking:** Managing effective-dated rate cards, partner agreements, and audit trails.
- **Financial Reconciliation & Traceability:** Structuring data flows so every output calculation is auditable back to its raw source event.
- **Modular Pipeline Development:** Building scalable ETL/ELT workflows using standard data engineering tools (e.g., PySpark, SQL, Orchestration tools).

---

## 2. Business Background and Problem Simulation

In retail banking ecosystems, financial institutions work with external sourcing partners such as Direct Selling Agents (DSAs), dealers, connectors, and Business Correspondents (BCs) to acquire customers. Partners earn financial commissions based on agreed performance structures.

Calculating payouts accurately is notoriously complex due to distributed source systems, changing commission rates, late-arriving cancellation events (clawbacks), invoice mismatches, and compliance/tax controls.

This project simulates these real-world enterprise data challenges within a controlled sandbox environment to practice handling production-grade data engineering scenarios.

### 2.1 Simulated Business Challenges Addressed
- **Multi-Source Data Ingestion:** Handling heterogeneous formats and schema variances across raw files.
- **Deduplication:** Preventing double-counting of loan disbursements or partner invoices.
- **SLA & Late-Arriving Events:** Handling foreclosures or loan cancellations that arrive weeks after a commission has already been calculated or paid.
- **Complex Financial Logic:** Implementing volume-based progressive/retroactive incentive slabs.
- **Data Governance & Auditability:** Retaining full traceability without silently deleting or modifying historic transaction records.

---

## 3. Project Roles & Implementation Context

Since this is a solo learning project, all traditional project roles are executed by the single developer to simulate an end-to-end data engineering lifecycle:

| Role | Simulated Responsibility in Learning Context |
|---|---|
| **Data Engineer (Author)** | Designs schema, builds data pipelines, implements transformations, and writes unit/integration tests. |
| **Business Analyst (Simulated)** | Defines business rules, edge cases, and functional specs (captured in this BRD). |
| **Finance / Compliance (Simulated)** | Establishes synthetic validation gates for tax (TDS), invoice matching, and reconciliation outputs. |
| **Code Reviewer / Portfolio Assessor** | Evaluates pipeline cleanliness, data modeling quality, documentation, and error handling. |

---

## 4. Products and Partner Channels in Scope

### 4.1 Products in Scope
The initial data pipeline scope focuses on three retail loan product lines:
1. **Personal Loans**
2. **Vehicle Loans**
3. **Home Loans**

*Note: Deposit products (CASA/AMB) are excluded in Phase 1 to focus on credit disbursement logic.*

### 4.2 Partner Sourcing Channels
The pipeline supports configurable rate rules across four partner categories:
1. **DSA** — Direct Selling Agents
2. **Dealers** — Vehicle and equipment dealers
3. **Connectors** — Individual business referral partners
4. **BC** — Business Correspondents

---

## 5. Scope Boundaries (Learning Phase 1)

### 5.1 Included In Data Engineering Build
- Automated ingestion and schema validation of CSV/Parquet/JSON synthetic datasets.
- Duplicate detection across transaction and master records.
- Effective-dated commission rate card lookup matching.
- Partner and product eligibility rule verification.
- Monthly volume-based incentive slab aggregation.
- Contractual clawback and cancellation adjustment processing.
- Synthetic Tax (TDS) deduction logic.
- Creation of an Exception/Quarantine dataset for invalid records.
- Generation of downstream reporting data models (Parquet / Analytical SQL tables).

### 5.2 Excluded from Pipeline Build (Out of Scope)
- Real banking payment gateway integrations (no real money is processed).
- Production core banking ledger connections.
- Real-time streaming/fraud processing (focused on batch/micro-batch processing).
- Legal tax advice or regulatory filings (rules are simplified for learning purposes).

---

## 6. Datasets & Data Schema Model (Logical)

The synthetic data environment uses the following logical entities:

| Logical Dataset | Function in Data Pipeline | Learning Focus |
|---|---|---|
| **Partner Master** | Partner profile, channel type, active status | Dimension modeling & status checks |
| **Loan Disbursement** | Core loan transaction facts | Fact processing & deduplication |
| **Product Master** | Product classifications and codes | Referential integrity checks |
| **Commission Rate Master** | Effective-dated rate cards | Point-in-time join logic |
| **Incentive Slab Master** | Tiered volume threshold rules | Complex window aggregation |
| **Partner Agreement** | Contract validity start/end dates | Temporal eligibility rules |
| **Foreclosure / Cancellation** | Late-arriving adjustment events | Delta processing & clawbacks |
| **Partner Invoice** | Partner-submitted payment invoices | Synthetic invoice-to-pay matching |
| **Exception Log (Output)** | Rejected / quarantined data rows | Error tracking data structures |
| **Commission Output (Output)** | Final calculated commission facts | Final reporting data target |

---

## 7. Business Logic & Calculation Rules

### 7.1 Commission Calculation Formula
$$\text{Gross Base Commission} = \text{Eligible Disbursed Amount} \times \text{Applicable Rate (\%)} + \text{Flat Fee (if applicable)}$$

$$\text{Net Commission Payable} = \text{Gross Base Commission} + \text{Incentive Amount} - \text{Clawback Amount} - \text{TDS Tax}$$

### 7.2 Effective-Dated Rate Card Matching
The pipeline must select the commission rate where:
$$\text{Rate Effective Start Date} \le \text{Disbursement Date} \le \text{Rate Effective End Date}$$

### 7.3 Incentive Slab Calculation Logic
Monthly volume incentives are calculated at the end of each billing cycle by aggregating eligible disbursements per partner:
- **Progressive Slabs:** Different rates apply to portions of volume within specific thresholds.
- **Retroactive Slabs:** Reaching a higher volume tier applies the higher rate to the total volume for the month.

---

## 8. Eligibility & Financial Controls

### 8.1 Dual-Gate Eligibility Architecture
The pipeline enforces two distinct status gates:
1. **Commission Calculation Eligibility:** Does the loan transaction qualify for commission? (Requires active partner status, valid agreement on disbursement date, non-duplicate transaction).
2. **Payout Release Eligibility:** Can the calculated commission be released? (Requires verified tax profile, valid invoice matching, no active compliance hold).

### 8.2 Clawbacks and Adjustments
When a loan cancellation or early foreclosure event is ingested:
- The pipeline queries historical commission outputs.
- It generates an explicit **Adjustment Record** linked to the original `Source Transaction ID`.
- Historic rows are **never overwritten or deleted**, ensuring complete financial auditability.

---

## 9. Exception Handling & Quarantine Strategy

To simulate enterprise data resilience, bad data will not crash the pipeline. Instead, invalid records are routed to an `Exception Dataset`:

| Scenario | Quarantined Action | System Behaviour |
|---|---|---|
| **Missing Partner ID** | Quarantine Row | Captured in Exception table with code `ERR_NO_PARTNER` |
| **Missing/Unmapped Rate Card** | Quarantine Row | Suspends calculation; logged as `ERR_RATE_NOT_FOUND` |
| **Duplicate Disbursement ID** | Deduplicate & Quarantine | Retains first valid record; flags duplicate as `ERR_DUPLICATE_TXN` |
| **Expired Contract Date** | Quarantine Row | Flagged as `ERR_CONTRACT_EXPIRED` |

---

## 10. Portfolio Output Data Models & Analytics

The pipeline produces structured data artifacts for portfolio demonstration:

1. **`fact_partner_commission_monthly`**: Aggregate monthly financial payout summary per partner.
2. **`fact_commission_line_items`**: Granular transaction-level audit log showing every calculation step.
3. **`dim_exception_log`**: Detailed record of all quarantined records and failure reasons.
4. **Analytical Dashboard Datasets**: Pre-aggregated datasets optimized for BI tool visualization (e.g., Total Disbursed Volume vs. Total Payout, Clawback Ratio, Pipeline Data Quality Score).

---

## 11. Project Milestones & Verification Criteria

This self-learning project will be considered completed when:
1. Synthetic sample datasets are generated and validated.
2. Pipeline code successfully executes end-to-end without unhandled errors.
3. 100% of invalid synthetic records are successfully captured in the Quarantine dataset.
4. Calculated payout numbers match expected benchmark results across test cases.
5. Code, documentation, and data flow diagrams are pushed to a clean, well-documented public GitHub repository.

---

## 12. Version History

| Version | Date | Summary of Changes |
|---|---|---|
| 1.0 | Initial Draft | Early concept draft. |
| 2.0 | 24 Nov 2026 | Enterprise business requirements refinement. |
| 2.1 | 24 Nov 2026 | Explicitly reframed as a solo self-learning portfolio project with a non-affiliation disclaimer and educational learning targets. |