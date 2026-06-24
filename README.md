# Irish VAT3 Compliance Tool

A Python and SQLite project that models end-to-end Irish VAT compliance covering processes from recording transactions to generating a formatted VAT3 return, as filed with Revenue Ireland via ROS.

Built as a portfolio project to demonstrate practical knowledge of Irish tax law, accounting workflows, and database design.

---

## What it does

- Records sales and purchases against VAT-registered businesses
- Applies correct Irish VAT rates (23%, 13.5%, 9%, 4.8%, 0%, Exempt)
- Handles **reverse charge** on intra-EU B2B purchases per Irish VAT rules
- Calculates all VAT3 return boxes: T1, T2, T3, T4, E1, E2
- Manages bi-monthly VAT periods with Revenue due dates (23rd of following month)
- Flags overdue unfiled periods
- Saves generated returns to the database for record-keeping
- Prevents duplicate transactions via invoice number validation

---

## Irish VAT rates implemented

| Rate | % | Applies to |
|------|---|------------|
| Standard | 23% | Most goods and services |
| Reduced | 13.5% | Construction, fuel, vet services, cleaning |
| Second Reduced | 9% | Hospitality, newspapers, sports facilities |
| Livestock | 4.8% | Agriculture and livestock |
| Zero Rated | 0% | Food, children's clothing, exports |
| Exempt | 0% | Financial services, education, healthcare |

---

## VAT3 return boxes

| Box | Description |
|-----|-------------|
| T1 | VAT charged on sales (output VAT) + reverse charge VAT self-accounted |
| T2 | VAT reclaimable on purchases (input VAT) + reverse charge VAT reclaimed |
| T3 | Net VAT payable to Revenue (T1 − T2, if positive) |
| T4 | Net VAT repayable by Revenue (T2 − T1, if positive) |
| E1 | Value of intra-EU supplies made (zero-rated, informational) |
| E2 | Value of intra-EU acquisitions made (informational) |

---

## Reverse charge explained

When purchasing from an EU supplier outside Ireland, the supplier cannot charge Irish VAT. Under Irish VAT law, the buyer self-accounts, declaring the VAT as both output (T1) and input (T2). This means no net cash impact, but the transaction must still appear on the VAT3 return and the net value is reported in E2.

---

## Project structure

```
irish-vat3-tool/
├── main.py              # CLI entry point — run this to use the tool
├── db_setup.py          # Creates database tables and seeds Irish VAT rates
├── vat_calculator.py    # Transaction entry and VAT3 box calculation logic
├── period_manager.py    # VAT period generation and overdue period detection
├── requirements.txt     # Dependencies (all standard library)
└── README.md
```

---

## How to run

**Requirements:** Python 3.8 or higher. No external packages needed, it uses only Python standard library.

```bash
git clone https://github.com/yourusername/irish-vat3-tool.git
cd irish-vat3-tool
python main.py
```

On first run, `main.py` calls `db_setup.py` automatically to create `vat3.db` and seed the Irish VAT rates.

---

## Sample output

```
==================================================
VAT3 RETURN — Aphasia Ireland
VAT Reg No: IE1234567T
Period: 2026-05-01 to 2026-06-30
Due Date: 2026-07-23
==================================================
T1  VAT on Sales:          €872.50
T2  VAT on Purchases:      €529.00
T3  Net Payable:           €343.50
T4  Net Repayable:         €0.00
E1  Intra-EU Sales:        €0.00
E2  Intra-EU Purchases:    €1500.00
==================================================
```

---

## Tech stack

- **Python 3** — core logic, CLI interface
- **SQLite3** — embedded relational database (built-in, no server required)
- **Standard library only** — datetime, calendar, sqlite3

---

## Author

Laukik Naik  
M.Sc. Corporate Finance, University of Galway (2025)  
ACCA (in progress) | Xero Certified Advisor  
[LinkedIn](https://www.linkedin.com/in/laukiknaik-368319165)
