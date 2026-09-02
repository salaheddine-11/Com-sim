-- ============================================================================
-- SOUSS AGRI-PACK SARL — CANONICAL RELATIONAL DATABASE SCHEMA (PostgreSQL / SQLite)
-- Zone Industrielle Ait Melloul, Agadir, Maroc | ICE: 002345678000091
-- Applicable Standards: Plan Comptable Marocain (CGNC), CGI 2025/2026, Loi 69-21
-- Precision: NUMERIC(15,2) for Monetary Amounts, Full Referential Integrity
-- ============================================================================

-- Table 1: Company Profile & Legal Identity
CREATE TABLE IF NOT EXISTS dim_company (
    entity_id VARCHAR(32) PRIMARY KEY,
    corporate_name VARCHAR(128) NOT NULL,
    legal_form VARCHAR(32) NOT NULL CHECK (legal_form IN ('SARL', 'SARL_AU', 'SA', 'COOPERATIVE', 'PERSONNE_PHYSIQUE')),
    ice VARCHAR(15) NOT NULL UNIQUE,
    identifiant_fiscal VARCHAR(10) NOT NULL UNIQUE,
    registre_commerce VARCHAR(10) NOT NULL,
    taxe_professionnelle VARCHAR(10) NOT NULL,
    cnss_affiliation VARCHAR(10) NOT NULL,
    headquarters_address TEXT NOT NULL,
    share_capital_mad NUMERIC(15, 2) NOT NULL CHECK (share_capital_mad >= 10000.00),
    legal_gerant_cin VARCHAR(12) NOT NULL,
    legal_gerant_name VARCHAR(128) NOT NULL,
    legal_gerant_role VARCHAR(32) NOT NULL DEFAULT 'GERANT_ASSOCIE_MAJORITAIRE',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 2: Chart of Accounts (Plan Comptable Général Marocain - Classes 1 to 8)
CREATE TABLE IF NOT EXISTS dim_chart_of_accounts (
    account_number VARCHAR(10) PRIMARY KEY,
    account_title VARCHAR(255) NOT NULL,
    class_code INTEGER NOT NULL CHECK (class_code BETWEEN 1 AND 8),
    account_level VARCHAR(16) NOT NULL CHECK (account_level IN ('CLASSE', 'RUBRIQUE', 'POSTE', 'COMPTE_PRINCIPAL', 'SOUS_COMPTE')),
    normal_balance VARCHAR(2) NOT NULL CHECK (normal_balance IN ('DR', 'CR')),
    statement_type VARCHAR(16) NOT NULL CHECK (statement_type IN ('BILAN_ACTIF', 'BILAN_PASSIF', 'CPC_CHARGES', 'CPC_PRODUITS', 'SPECIAL')),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

-- Table 3: Commercial Clients Master (6 Market Segments)
CREATE TABLE IF NOT EXISTS dim_clients (
    client_id VARCHAR(16) PRIMARY KEY,
    company_name VARCHAR(128) NOT NULL,
    market_segment VARCHAR(32) NOT NULL CHECK (market_segment IN ('AGRI_EXPORTER', 'MODERN_RETAIL', 'SOUK_WHOLESALE', 'AGRO_INDUSTRIAL', 'DIRECT_EU_EXPORT', 'COOPERATIVE')),
    ice VARCHAR(15) NOT NULL,
    identifiant_fiscal VARCHAR(10) NOT NULL,
    payment_terms_days INTEGER NOT NULL CHECK (payment_terms_days BETWEEN 0 AND 180),
    settlement_method VARCHAR(16) NOT NULL CHECK (settlement_method IN ('LCN', 'VIREMENT', 'CHEQUE', 'ESPECES')),
    credit_limit_mad NUMERIC(15, 2) NOT NULL CHECK (credit_limit_mad >= 0.00),
    tva_regime VARCHAR(32) NOT NULL CHECK (tva_regime IN ('NORMAL_20', 'EXEMPT_EXPORT_ART_92', 'SUSPENSION_ART_94')),
    bank_rib VARCHAR(24) NOT NULL,
    pcm_account VARCHAR(10) NOT NULL DEFAULT '34210000',
    FOREIGN KEY (pcm_account) REFERENCES dim_chart_of_accounts(account_number)
);

-- Table 4: Suppliers Master (Raw Paper, Consumables, Energy, Logistics & Services)
CREATE TABLE IF NOT EXISTS dim_suppliers (
    supplier_id VARCHAR(16) PRIMARY KEY,
    company_name VARCHAR(128) NOT NULL,
    supplier_category VARCHAR(32) NOT NULL CHECK (supplier_category IN ('PAPER_MILL_LOCAL', 'PAPER_MILL_IMPORT', 'AUXILIARY_CHEMICALS', 'ENERGY_UTILITY', 'TRANSPORT_LOGISTICS', 'MAINTENANCE_SERVICES', 'PROFESSIONAL_SERVICES')),
    country_origin VARCHAR(2) NOT NULL,
    ice VARCHAR(15) NOT NULL,
    identifiant_fiscal VARCHAR(10) NOT NULL,
    payment_terms_days INTEGER NOT NULL CHECK (payment_terms_days BETWEEN 0 AND 120),
    settlement_method VARCHAR(16) NOT NULL CHECK (settlement_method IN ('LCN', 'VIREMENT', 'CHEQUE', 'ESPECES', 'LETTER_OF_CREDIT')),
    bank_rib VARCHAR(24) NOT NULL,
    pcm_account VARCHAR(10) NOT NULL DEFAULT '44110000',
    FOREIGN KEY (pcm_account) REFERENCES dim_chart_of_accounts(account_number)
);

-- Table 5: Banking Partner Institutions & Authorized Credit Lines
CREATE TABLE IF NOT EXISTS dim_banks (
    bank_code VARCHAR(16) PRIMARY KEY CHECK (bank_code IN ('AWB', 'BP', 'CAM', 'BMCE')),
    bank_name VARCHAR(128) NOT NULL,
    agency_name VARCHAR(128) NOT NULL,
    bank_rib VARCHAR(24) NOT NULL UNIQUE,
    pcm_account VARCHAR(10) NOT NULL,
    escompte_ceiling_mad NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (escompte_ceiling_mad >= 0.00),
    decouvert_ceiling_mad NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (decouvert_ceiling_mad >= 0.00),
    campaign_credit_mad NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (campaign_credit_mad >= 0.00),
    interest_spread_bps NUMERIC(6, 2) NOT NULL DEFAULT 0.00 CHECK (interest_spread_bps >= 0.00),
    FOREIGN KEY (pcm_account) REFERENCES dim_chart_of_accounts(account_number)
);

-- Table 6: Employees & Human Resources Master (22 Permanent + 5 Seasonal)
CREATE TABLE IF NOT EXISTS dim_employees (
    matricule VARCHAR(16) PRIMARY KEY,
    cin VARCHAR(12) NOT NULL UNIQUE,
    cnss_number VARCHAR(10) NOT NULL UNIQUE,
    full_name VARCHAR(128) NOT NULL,
    role_title VARCHAR(64) NOT NULL,
    contract_type VARCHAR(32) NOT NULL CHECK (contract_type IN ('CDI', 'CDD', 'SAISONNIER', 'GERANT_STATUTAIRE')),
    base_gross_monthly_mad NUMERIC(15, 2) NOT NULL CHECK (base_gross_monthly_mad >= 0.00),
    hourly_rate_mad NUMERIC(10, 2) NOT NULL CHECK (hourly_rate_mad >= 0.00),
    dependents_count INTEGER NOT NULL DEFAULT 0 CHECK (dependents_count BETWEEN 0 AND 6),
    hire_date DATE NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

-- Table 7: Fixed Assets Register & Depreciation Schedule
CREATE TABLE IF NOT EXISTS dim_fixed_assets (
    asset_code VARCHAR(16) PRIMARY KEY,
    designation VARCHAR(255) NOT NULL,
    asset_pcm_account VARCHAR(10) NOT NULL,
    depreciation_pcm_account VARCHAR(10) NOT NULL,
    dotation_pcm_account VARCHAR(10) NOT NULL DEFAULT '61810000',
    acquisition_date DATE NOT NULL,
    gross_value_mad NUMERIC(15, 2) NOT NULL CHECK (gross_value_mad > 0.00),
    salvage_value_mad NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (salvage_value_mad >= 0.00),
    lifespan_years NUMERIC(4, 1) NOT NULL CHECK (lifespan_years > 0.0),
    depreciation_method VARCHAR(16) NOT NULL DEFAULT 'LINEAIRE' CHECK (depreciation_method IN ('LINEAIRE', 'DEGRESSIF')),
    accumulated_depr_opening_mad NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (accumulated_depr_opening_mad >= 0.00),
    FOREIGN KEY (asset_pcm_account) REFERENCES dim_chart_of_accounts(account_number),
    FOREIGN KEY (depreciation_pcm_account) REFERENCES dim_chart_of_accounts(account_number),
    FOREIGN KEY (dotation_pcm_account) REFERENCES dim_chart_of_accounts(account_number)
);

-- Table 8: Inventory Items Catalog & Production SKUs
CREATE TABLE IF NOT EXISTS dim_inventory_items (
    sku_code VARCHAR(16) PRIMARY KEY,
    sku_category VARCHAR(32) NOT NULL CHECK (sku_category IN ('RAW_MATERIAL', 'AUXILIARY', 'FINISHED_GOOD', 'SCRAP_WASTE')),
    designation VARCHAR(255) NOT NULL,
    unit_of_measure VARCHAR(16) NOT NULL CHECK (unit_of_measure IN ('M2', 'KG', 'UNIT', 'LITER')),
    standard_cost_mad NUMERIC(10, 4) NOT NULL CHECK (standard_cost_mad >= 0.0000),
    current_cump_mad NUMERIC(10, 4) NOT NULL DEFAULT 0.0000 CHECK (current_cump_mad >= 0.0000),
    stock_quantity NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (stock_quantity >= 0.00),
    stock_pcm_account VARCHAR(10) NOT NULL,
    variation_pcm_account VARCHAR(10) NOT NULL,
    FOREIGN KEY (stock_pcm_account) REFERENCES dim_chart_of_accounts(account_number),
    FOREIGN KEY (variation_pcm_account) REFERENCES dim_chart_of_accounts(account_number)
);

-- Table 9: Business Transaction Events Log (8 Operational Cycles)
CREATE TABLE IF NOT EXISTS fact_events (
    event_id VARCHAR(32) PRIMARY KEY,
    event_code VARCHAR(32) NOT NULL,
    event_name VARCHAR(128) NOT NULL,
    operational_cycle VARCHAR(32) NOT NULL CHECK (operational_cycle IN ('ORDER_TO_CASH', 'PROCURE_TO_PAY', 'PAYROLL_SOCIAL', 'BANKING_TREASURY', 'TAX_COMPLIANCE', 'INVENTORY_PRODUCTION', 'RISK_SHOCKS', 'YEAR_END_CLOSING')),
    trigger_type VARCHAR(16) NOT NULL CHECK (trigger_type IN ('SCHEDULED', 'TRANSACTIONAL', 'CONDITIONAL', 'STOCHASTIC')),
    fiscal_year INTEGER NOT NULL CHECK (fiscal_year IN (2025, 2026)),
    effective_date DATE NOT NULL,
    reference_document VARCHAR(64) NOT NULL,
    payload_json TEXT NOT NULL,
    status VARCHAR(16) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'PROCESSED', 'FAILED', 'REVERSED')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table 10: Double-Entry Journal Entries Header (Strict Balance Enforced)
CREATE TABLE IF NOT EXISTS fact_journal_entries (
    entry_id VARCHAR(32) PRIMARY KEY,
    event_id VARCHAR(32) NOT NULL,
    journal_code VARCHAR(16) NOT NULL CHECK (journal_code IN ('RAN', 'ACH', 'VEN', 'BQ-AWB', 'BQ-BP', 'BQ-CAM', 'BQ-BMCE', 'CAI', 'PAI', 'OD')),
    entry_date DATE NOT NULL,
    accounting_period VARCHAR(7) NOT NULL,
    piece_justificative VARCHAR(64) NOT NULL,
    total_debit NUMERIC(15, 2) NOT NULL CHECK (total_debit >= 0.00),
    total_credit NUMERIC(15, 2) NOT NULL CHECK (total_credit >= 0.00),
    status VARCHAR(16) NOT NULL DEFAULT 'POSTED' CHECK (status IN ('DRAFT', 'VALIDATED', 'POSTED', 'REVERSED')),
    posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_journal_balanced CHECK (ROUND(total_debit, 2) = ROUND(total_credit, 2)),
    FOREIGN KEY (event_id) REFERENCES fact_events(event_id)
);

-- Table 11: Double-Entry Journal Lines (Debits and Credits Details)
CREATE TABLE IF NOT EXISTS fact_journal_lines (
    line_id VARCHAR(36) PRIMARY KEY,
    entry_id VARCHAR(32) NOT NULL,
    line_order INTEGER NOT NULL CHECK (line_order >= 1),
    account_number VARCHAR(10) NOT NULL,
    third_party_id VARCHAR(32),
    line_description VARCHAR(255) NOT NULL,
    debit_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (debit_amount >= 0.00),
    credit_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (credit_amount >= 0.00),
    analytical_code VARCHAR(32),
    CONSTRAINT chk_dr_cr_exclusive CHECK ((debit_amount > 0.00 AND credit_amount = 0.00) OR (credit_amount > 0.00 AND debit_amount = 0.00) OR (debit_amount = 0.00 AND credit_amount = 0.00)),
    FOREIGN KEY (entry_id) REFERENCES fact_journal_entries(entry_id),
    FOREIGN KEY (account_number) REFERENCES dim_chart_of_accounts(account_number)
);

-- Table 12: Commercial Payment Instruments Register (LCN, Cheques, Traites)
CREATE TABLE IF NOT EXISTS fact_payment_instruments (
    instrument_id VARCHAR(32) PRIMARY KEY,
    instrument_type VARCHAR(16) NOT NULL CHECK (instrument_type IN ('LCN', 'CHEQUE', 'VIREMENT', 'BILLET_A_ORDRE')),
    reference_number VARCHAR(64) NOT NULL UNIQUE,
    drawer_id VARCHAR(32) NOT NULL,
    drawee_id VARCHAR(32) NOT NULL,
    beneficiary_id VARCHAR(32) NOT NULL,
    nominal_amount_mad NUMERIC(15, 2) NOT NULL CHECK (nominal_amount_mad > 0.00),
    issue_date DATE NOT NULL,
    due_date DATE NOT NULL,
    bank_code VARCHAR(16) NOT NULL,
    current_status VARCHAR(24) NOT NULL DEFAULT 'ISSUED' CHECK (current_status IN ('ISSUED', 'IN_PORTFOLIO', 'DISCOUNTED', 'COLLECTED', 'PROTESTED', 'CANCELLED')),
    FOREIGN KEY (bank_code) REFERENCES dim_banks(bank_code)
);

-- Table 13: Tax Declarations & Regulatory Compliance Register (CGI & Law 69-21)
CREATE TABLE IF NOT EXISTS fact_tax_declarations (
    declaration_id VARCHAR(32) PRIMARY KEY,
    tax_type VARCHAR(16) NOT NULL CHECK (tax_type IN ('TVA', 'IR', 'IS_ACOMPTE', 'IS_RELIQUAT', 'TP', 'TSC', 'CNSS', 'L69_21')),
    period_label VARCHAR(16) NOT NULL,
    filing_deadline DATE NOT NULL,
    filing_date DATE,
    turnover_base_mad NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (turnover_base_mad >= 0.00),
    tax_due_mad NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (tax_due_mad >= 0.00),
    tax_paid_mad NUMERIC(15, 2) NOT NULL DEFAULT 0.00 CHECK (tax_paid_mad >= 0.00),
    settlement_reference VARCHAR(64),
    payment_status VARCHAR(16) NOT NULL DEFAULT 'PENDING' CHECK (payment_status IN ('PENDING', 'DECLARED', 'PAID', 'LATE_PAID', 'CREDIT_CARRIED'))
);

-- ============================================================================
-- PERFORMANCE & AUDIT INDEXES
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_je_period ON fact_journal_entries(accounting_period);
CREATE INDEX IF NOT EXISTS idx_je_journal ON fact_journal_entries(journal_code);
CREATE INDEX IF NOT EXISTS idx_je_event ON fact_journal_entries(event_id);
CREATE INDEX IF NOT EXISTS idx_jl_account ON fact_journal_lines(account_number);
CREATE INDEX IF NOT EXISTS idx_jl_entry ON fact_journal_lines(entry_id);
CREATE INDEX IF NOT EXISTS idx_inst_status ON fact_payment_instruments(current_status);
CREATE INDEX IF NOT EXISTS idx_inst_due ON fact_payment_instruments(due_date);
CREATE INDEX IF NOT EXISTS idx_events_cycle ON fact_events(operational_cycle);
CREATE INDEX IF NOT EXISTS idx_events_year ON fact_events(fiscal_year);
CREATE INDEX IF NOT EXISTS idx_tax_type_period ON fact_tax_declarations(tax_type, period_label);
