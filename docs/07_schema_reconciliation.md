# Schema Reconciliation: Canonical DDL vs SQLite Runtime

## TL;DR

The repository ships **two distinct database artifacts** that serve different audiences. This document reconciles them.

| Artifact | Audience | Tables | Purpose |
|---|---|---|---|
| `schemas/schema.sql` | Schema designers, future PostgreSQL migrations | **13** canonical tables | Authoritative design contract for the full multi-cycle Moroccan SME simulation |
| `data/fy2025/database/souss_sim_2025.db` | Audit scripts, BI consumers | **4** materialized runtime tables | Forensic-audit-friendly projection of the most-queried entities |

These are **not contradictory**. The SQLite database is a deliberate downstream materialization: only the tables that the 15-point forensic audit (`scripts/audit_fy2025_data.py`) and downstream report consumers actually query are persisted. The canonical schema is the **executable specification**; the SQLite is the **projection used by Phase 2 forensics**.

## Canonical schema (`schemas/schema.sql`) — 13 tables

| # | Table | Role | Materialized in SQLite? |
|---|---|---|---|
| 1 | `dim_company` | Souss Agri-Pack legal identity (ICE, IF, RC, TP, CNSS) | ❌ (constants in generator modules) |
| 2 | `dim_chart_of_accounts` | PCM 304-account catalogue | ❌ (constants in `config/chart_of_accounts.yaml`) |
| 3 | `dim_clients` | Customer master (6 segments) | ✅ as `customers` (9 cols) |
| 4 | `dim_suppliers` | Supplier master (paper, energy, services) | ❌ (constants in `generator/purchase_generator.py`) |
| 5 | `dim_banks` | Bank facilities (AWB, BP, CAM, BMCE) | ❌ (constants in `generator/treasury_generator.py`) |
| 6 | `dim_employees` | 22 CDI + 5 seasonal workers | ❌ (constants in `config/payroll_grid.yaml`) |
| 7 | `dim_fixed_assets` | Asset register + depreciation | ❌ (constants in `config/fixed_assets_depreciation.yaml`) |
| 8 | `dim_inventory_items` | SKU catalog (P001–P005 + raw materials) | ❌ (constants in `generator/sales_generator.py`) |
| 9 | `fact_events` | Audit log of every business event (52 types × N occurrences) | ❌ (events are replayable from `journal_general.csv` via `event_id`) |
| 10 | `fact_journal_entries` | Journal entry header (with `chk_journal_balanced` CHECK constraint) | ✅ merged into `journal_entries` (entry_id, date, journal_code, event_id) |
| 11 | `fact_journal_lines` | Per-line debit/credit rows | ✅ as `journal_entries.debit_mad` / `credit_mad` columns (denormalized flat layout) |
| 12 | `fact_payment_instruments` | LCR / cheque / virement register | ❌ as DB; ✅ as `data/fy2025/operational/commercial_papers.csv` |
| 13 | `fact_tax_declarations` | TVA / IR / IS / TP / TSC / CNSS filings | ❌ as DB; ✅ embedded in `data/fy2025/reports/financial_summary.json` + `journal_general.csv` |

## SQLite runtime schema (`data/fy2025/database/souss_sim_2025.db`) — 4 tables

```sql
CREATE TABLE customers (
    customer_id          TEXT,
    company_name         TEXT,
    trade_name           TEXT,
    segment              TEXT,
    ice                  TEXT,          -- 15-digit validated
    identifiant_fiscal   TEXT,
    registre_commerce    TEXT,
    payment_terms        TEXT,
    credit_limit_mad     REAL
);

CREATE TABLE sales_invoices (
    invoice_number       TEXT,
    invoice_date         TEXT,
    due_date             TEXT,
    customer_id          TEXT,
    total_ht_mad         REAL,
    total_tva_mad        REAL,
    total_ttc_mad        REAL,
    payment_method       TEXT,
    status               TEXT
);

CREATE TABLE journal_entries (
    id                   INTEGER PRIMARY KEY,
    entry_id             TEXT,
    entry_date           TEXT,
    journal_code         TEXT,
    piece_ref            TEXT,
    event_id             TEXT,
    account_number       TEXT,
    account_title        TEXT,
    debit_mad            REAL,
    credit_mad           REAL,
    description          TEXT
);
```

## Naming divergences (canonical → SQLite)

| Canonical | Runtime | Notes |
|---|---|---|
| `dim_clients` | `customers` | Dropped the `dim_` prefix; SQLite is the runtime materialization |
| `dim_clients.company_name` | `customers.company_name` | Same |
| `dim_clients.trade_name` | `customers.trade_name` | Same |
| `fact_journal_entries` + `fact_journal_lines` | `journal_entries` (denormalized) | Header and lines collapsed into one flat table for forensic query simplicity. The denormalized layout preserves `entry_id` as a group-by key. |
| `journal_code` | `journal_code` | Same |

## Why this is correct, not a bug

1. **The canonical schema is the design contract.** `schema.sql` declares what the system *could* hold in PostgreSQL. It is not a runtime materialization.
2. **The SQLite database is a forensic-audit projection.** Only entities the 15-point `audit_fy2025_data.py` and the `bilan_2025.md` / `cpc_2025.md` / `liasse_fiscale_2025.md` reports need are persisted.
3. **All other canonical entities live as YAML config or Python constants.** When the project moves to PostgreSQL or to a multi-year simulation that demands full persistence, all 13 canonical tables will be populated by the existing generators without code changes.

## Migration path (if/when full PostgreSQL is adopted)

1. Provision a PostgreSQL 14+ database.
2. Apply `schemas/schema.sql` directly — it is Postgres-compatible with the exception of the `CHECK` constraint syntax (Postgres requires `CHECK (legal_form IN (...))` without trailing commas).
3. Run `scripts/run_simulation_fy2025.py --backend postgres --dsn <conn-string>` once the generator is extended to write to a backend-agnostic DAL. (Not yet implemented; current generator writes to CSV/SQLite only.)
4. The 15-point forensic audit (`audit_fy2025_data.py`) reads from CSV/JSON today; it should be re-pointed at the Postgres tables for full coverage.

## Cross-references

- **Canonical DDL**: `schemas/schema.sql`
- **Runtime SQLite**: `data/fy2025/database/souss_sim_2025.db`
- **Forensic audit (reads runtime SQLite + CSVs)**: `scripts/audit_fy2025_data.py`
- **Spec verification (reads YAMLs only, no DB)**: `scripts/verify_specs.py`