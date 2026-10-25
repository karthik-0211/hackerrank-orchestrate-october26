# HackerRank Orchestrate (October 2026)
# Ghost Data Still Exists: Evidence-First AI Deletion Audit Agent

An evidence-driven, deterministic deletion-audit agent engineered for the **HackerRank Orchestrate October 2026** competition challenge: **Ghost Data Still Exists**.

The agent audits whether personal data deletion requests across distributed microservice architectures have been completely, partially, or non-compliantly processed at a strict historical cutoff timestamp (`audit_at`).

Official Challenge & Submission URL:
**[https://wwww.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists](https://wwww.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists)**

---

## Key Highlights & Performance Benchmark

- **100.00% Status Accuracy** on the official public reference set (32 / 32 cases).
- **88.60% Step Recall & 85.07% Precision** (F1 Score: **86.80%**).
- **100% Deterministic & Offline-Safe:** Built with zero paid external API dependencies; runs in **~18 seconds** for all 518 cases with **$0.00 API expenditure**.
- **100% Contract Conformance:** Exactly 518 data rows evaluated with **0 validation errors** under the independent contract validator.
- **3 / 3 Synthetic Edge-Case Tests Passed (100%):** Validates non-deletion intent rejection, historical alias discovery, and non-compliant tombstone detection.

---

## The Problem: Why "Ghost Data" Still Exists

In modern distributed platforms, a deletion workflow may claim **Complete** while personal data remains active across downstream stores:
1. **Replication Drift:** Secondary read replicas, regional databases, and reporting replicas fail to sync deletion operations from primary databases.
2. **Active Connectors & Sync Pipelines:** Upstream synchronization processes and connectors repopulate deleted profiles into search indexes and analytics.
3. **Backup Restore Vulnerabilities:** Unblocked backup archives allow restoration paths that can re-inject removed user records into production.
4. **Anonymization Failures:** Telemetry and analytics records retain reversible tokens, telephone numbers, or SHA-256 hashes instead of being irreversibly anonymized.
5. **Account Tombstone Violations:** Tombstones retain direct personal data (names, emails) instead of preserving only the permitted stable internal `user_id`.

Reported workflow statuses and operation results are merely **claims**. The audit agent must establish the real state at `audit_at` from forensic evidence.

---

## System Architecture

```mermaid
flowchart TD
    A[dataset/deletion_requests.csv] --> B[code/classifier.py: RequestClassifier]
    B -->|Non-Deletion Intent| C[NOT_APPLICABLE: steps_json = []]
    B -->|Authorized Deletion| D[code/identity.py: IdentityResolver]
    
    E[dataset/user_identities.csv] --> D
    F[dataset/user_audit_log.csv] --> D
    
    G[dataset/evidence_files.csv & dataset/evidence/*] --> H[code/evidence_indexer.py: EvidenceIndexer]
    H -->|2,122 Observations: SQL, JSON, Logs, PDF, Images| I[code/state_reconstructor.py: StateReconstructor]
    
    J[dataset/system_activity.csv] --> K[code/activity_loader.py: ActivityLoader]
    K --> I
    D --> I
    
    I -->|Temporal Cutoff: captured_at <= audit_at| L[code/policy_planner.py: PolicyPlanner]
    M[dataset/deletion_rules.csv] --> L
    
    L --> N[FINDING -> REMEDIATION -> VERIFICATION Sequencing]
    N --> O[code/validator.py: OutputValidator]
    O --> P[./output.csv: 518 Validated Rows]
```

### Modular Pipeline Structure (`code/`)

1. **`code/classifier.py` (`RequestClassifier`):**
   - First decision gate. Evaluates `request_text` to distinguish genuine deletion authorizations from non-deletion inquiries (portable data exports, billing invoice requests, surname updates, marketing opt-outs).
   - Rejects non-deletion cases as `NOT_APPLICABLE` with `steps_json = []`.

2. **`code/identity.py` (`IdentityResolver`):**
   - Unifies `user_identities.csv` and `user_audit_log.csv`.
   - Recovers stable `user_id`, historical email aliases, phone changes, names, and 64-character SHA-256 hashes into a cohesive `IdentityProfile`.

3. **`code/evidence_indexer.py` (`EvidenceIndexer`):**
   - High-throughput forensic parser across all 94 evidence files in `dataset/evidence/`:
     - **24 SQL Databases:** Executed in-memory via SQLite across primary and regional replica tables.
     - **28 JSON Snapshots:** Domain-aware parsing covering 8 key namespaces (`profiles`, `profile_lookups`, `restore_entries`, `connectors`, `index_queries`, `audit_records`, `tickets`).
     - **27 Structured Logs:** Multi-line trace buffering by `trace_id` to correlate asynchronous started/completed event pairs.
     - **4 PDFs:** Document text extraction via `pypdf`.
     - **11 PNG Screenshots:** Structured console state facts extracted from administrative views.
   - Pre-indexes 2,122 observations upfront for instant sub-second lookup across all 518 cases.

4. **`code/activity_loader.py` (`ActivityLoader`):**
   - Indexes `system_activity.csv` operations, data catalog links (`LINK_RESOURCE_IDENTITY`), and worker events.

5. **`code/state_reconstructor.py` (`StateReconstructor`):**
   - Evaluates point-in-time resource states strictly at `audit_at`.
   - Enforces temporal cutoffs (`captured_at <= audit_at`), ignoring post-audit evidence.
   - Disambiguates batch worker operations by matching the request's `reported_status` with worker outcomes (`SUCCESS`, `PARTIAL`, `FAILED`) and time proximity.

6. **`code/policy_planner.py` (`PolicyPlanner`):**
   - Strictly enforces the 15 rules in `dataset/deletion_rules.csv`.
   - Orders steps by phase (`FINDING` $\rightarrow$ `REMEDIATION` $\rightarrow$ `VERIFICATION`), operation precedence, `system_id` ASC, and `resource_id` ASC.
   - Cites real evidence IDs for findings and completed verifications; strictly sets `evidence_id: ""` for proposed remediation and future verifications.

7. **`code/validator.py` (`OutputValidator`):**
   - Automated conformance engine validating CSV headers, row counts, numerical sorting, JSON syntax, step number continuity, and enum legality.

---

## Prerequisites & Installation

### Requirements
- **Python:** Version 3.10, 3.11, or 3.12.
- **Operating System:** Windows, macOS, or Linux.
- **Dependencies:** `pypdf>=4.0.0` (all other modules use Python Standard Library: `sqlite3`, `csv`, `json`, `re`, `hashlib`, `dataclasses`, `typing`, `datetime`, `os`, `sys`).

### 1. Clone the Repository
```bash
git clone https://github.com/interviewstreet/hackerrank-orchestrate-october26.git
cd hackerrank-orchestrate-october26
```

### 2. Set Up a Virtual Environment (Recommended)

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Or install directly: `pip install pypdf`)*

---

## Execution Guide

### 1. Run the Main Audit Agent (Generate `output.csv`)
Execute the main entry point from the repository root:

```bash
python3 code/main.py
```
*(On Windows: `python code\main.py`)*

**Output:** Audits all 518 cases from `dataset/deletion_requests.csv`, generates `./output.csv`, and runs automated validation in ~18 seconds.

### 2. Run the Evaluation Suite
Run automated evaluation against public reference samples and synthetic edge cases:

```bash
python3 code/evaluation/main.py
```
*(On Windows: `python code\evaluation\main.py`)*

**Output:**
```text
=== PUBLIC SAMPLE EVALUATION (32 cases) ===
Status Accuracy: 32/32 (100.00%)
Step Precision:  171/201 (85.07%)
Step Recall:     171/193 (88.60%)
Step F1:         86.80%
Sequence Acc:    6/32 (18.75%)

=== SYNTHETIC EDGE-CASE EVALUATION ===
  PASS: synth_01_non_del -> NOT_APPLICABLE (steps: 0)
  PASS: synth_02_historical_alias -> INCOMPLETE (steps: 5)
  PASS: synth_03_exposed_tombstone -> INCOMPLETE (steps: 5)
Synthetic Tests Passed: 3/3
```

### 3. Validate Output Contract Compliance
Run the independent output validator on the generated `output.csv`:

```bash
python3 -c "from code.validator import OutputValidator; v = OutputValidator(); errs = v.validate_file('output.csv', 518); print(f'Errors: {len(errs)}')"
```

---

## Packaging `code.zip` for Submission

Per the challenge requirements, `code.zip` must include the runnable solution, evaluation reports, and `README.md`, while strictly excluding `dataset/`, virtual environments, caches, and nested archives.

**Windows (PowerShell):**
```powershell
# Remove any temporary pycache folders
Get-ChildItem -Path code -Recurse -Filter "__pycache__" | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Compress into submission code.zip
Compress-Archive -Path README.md, code -DestinationPath code.zip -Force
```

**macOS / Linux:**
```bash
zip -r code.zip README.md code -x "*/__pycache__/*" "*/.venv/*" "*/venv/*" "*/node_modules/*" "*/.git/*" "*/.DS_Store"
```

---

## Output Contract & Schema

The root `output.csv` conforms strictly to the challenge contract:

```text
case_id,deletion_status,steps_json
```

- **`case_id`:** Sorted in consecutive numerical order (`case_33` through `case_550`).
- **`deletion_status`:** Exactly one of `COMPLETE`, `INCOMPLETE`, or `NOT_APPLICABLE`.
- **`steps_json`:** Valid JSON array with consecutive `step_no` starting at 1:
  - For `NOT_APPLICABLE`: `[]`.
  - For `COMPLETE`: Only verification steps with non-empty evidence citations proving compliant state at `audit_at`.
  - For `INCOMPLETE`: Relevant findings (citing evidence), ordered remediation plan (`evidence_id: ""`), and future verification checks (`evidence_id: ""`).

### Allowed Enums & Legal Combinations

| Phase | Operation | Allowed State | Required Evidence ID |
| :--- | :--- | :--- | :--- |
| `FINDING` | `REPORT_REMAINING_RECORD` | `PRESENT` | Valid evidence reference (`file_id`, `activity_id`) |
| `FINDING` | `REPORT_EXPOSED_PII` | `PRESENT` | Valid evidence reference |
| `FINDING` | `REPORT_ACTIVE_DATA_FLOW` | `ACTIVE` | Valid evidence reference |
| `FINDING` | `REPORT_RESTORE_RISK` | `ACTIVE` | Valid evidence reference |
| `REMEDIATION` | `DISABLE_DATA_FLOW` | `DISABLED` | `""` (Empty string) |
| `REMEDIATION` | `BLOCK_RESTORE` | `BLOCKED` | `""` (Empty string) |
| `REMEDIATION` | `DELETE_RECORD` | `ABSENT` | `""` (Empty string) |
| `REMEDIATION` | `REDACT_RECORD` | `REDACTED` | `""` (Empty string) |
| `REMEDIATION` | `ANONYMIZE_RECORD` | `ANONYMIZED` | `""` (Empty string) |
| `VERIFICATION` | `VERIFY_RECORD_ABSENT` | `ABSENT` | Evidence ID if COMPLETE, else `""` |
| `VERIFICATION` | `VERIFY_RECORD_PRESENT` | `PRESENT` | Evidence ID if COMPLETE, else `""` |
| `VERIFICATION` | `VERIFY_RECORD_REDACTED` | `REDACTED` | Evidence ID if COMPLETE, else `""` |
| `VERIFICATION` | `VERIFY_RECORD_ANONYMIZED` | `ANONYMIZED` | Evidence ID if COMPLETE, else `""` |
| `VERIFICATION` | `VERIFY_DATA_FLOW_DISABLED` | `DISABLED` | Evidence ID if COMPLETE, else `""` |
| `VERIFICATION` | `VERIFY_RESTORE_BLOCKED` | `BLOCKED` | Evidence ID if COMPLETE, else `""` |

---

## Hackathon Submission Checklist

To submit on the [HackerRank Challenge Portal](https://wwww.hackerrank.com/contests/hackerrank-orchestrate-october26/challenges/ghost-data-still-exists):

1. **`output.csv` (Predictions File):** Root-level file with 518 sorted data rows.
2. **`code.zip` (Source Archive):** Contains `code/`, `code/evaluation/evaluation_report.md`, `code/evaluation/usage_report.md`, and `README.md`.
3. **`log.txt` (`chat_transcript`):** Root-level log following Section 5 of `AGENTS.md`.
