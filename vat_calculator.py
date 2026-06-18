"""
vat_calculator.py
Core VAT logic for the Irish VAT3 compliance tool.

Contains:
- add_transaction(): records a sale/purchase and calculates VAT
- calculate_vat3(): aggregates a period's transactions into VAT3 return boxes
  (T1, T2, T3, T4, E1, E2) per Irish Revenue rules, including reverse charge
  handling for intra-EU B2B purchases.
"""


def add_transaction(cursor, conn, business_id, period_id, date, trans_type,
                     counterparty, net_amount, vat_rate_id,
                     invoice_number, supply_type,
                     counterparty_vat_no=None, is_reverse_charge=False):
    """
    Records a single transaction (sale or purchase), calculating VAT and
    gross amount based on the rate looked up from vat_rates.
    Prevents duplicate entries by checking invoice_number before inserting.
    """

    # Duplicate prevention
    cursor.execute('''
        SELECT transaction_id FROM transactions
        WHERE business_id = ? AND invoice_number = ?
    ''', (business_id, invoice_number))

    if cursor.fetchone():
        print(f"Skipped — invoice {invoice_number} already exists")
        return

    # Look up VAT rate percentage
    cursor.execute("SELECT rate_percentage FROM vat_rates WHERE rate_id = ?", (vat_rate_id,))
    rate_row = cursor.fetchone()
    if rate_row is None:
        raise ValueError(f"VAT rate_id {vat_rate_id} not found in vat_rates table")
    vat_rate = rate_row[0]

    vat_amount = round(net_amount * (vat_rate / 100), 2)
    gross_amount = round(net_amount + vat_amount, 2)

    cursor.execute('''
        INSERT INTO transactions 
        (business_id, period_id, transaction_date, transaction_type,
         counterparty_name, counterparty_vat_no, net_amount, vat_rate_id,
         vat_amount, gross_amount, invoice_number, supply_type, is_reverse_charge)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (business_id, period_id, date, trans_type,
          counterparty, counterparty_vat_no, net_amount, vat_rate_id,
          vat_amount, gross_amount, invoice_number, supply_type, is_reverse_charge))

    conn.commit()
    print(f"Transaction added — {counterparty} | Net: €{net_amount} | VAT: €{vat_amount} | Gross: €{gross_amount}")


def calculate_vat3(cursor, period_id):
    """
    Aggregates all transactions in a given period into VAT3 return boxes.

    T1 - VAT on sales (output VAT), including reverse charge VAT
    T2 - VAT on purchases (input VAT), including reverse charge VAT
    T3 - Net VAT payable to Revenue (T1 - T2, if positive)
    T4 - Net VAT repayable by Revenue (T2 - T1, if positive)
    E1 - Value of intra-EU sales (informational)
    E2 - Value of intra-EU purchases (informational)
    """

    cursor.execute('''
        SELECT SUM(vat_amount) FROM transactions
        WHERE period_id = ? AND transaction_type = 'sale'
    ''', (period_id,))
    t1 = cursor.fetchone()[0] or 0

    cursor.execute('''
        SELECT SUM(vat_amount) FROM transactions
        WHERE period_id = ? AND transaction_type = 'purchase'
    ''', (period_id,))
    t2 = cursor.fetchone()[0] or 0

    # Reverse charge VAT self-accounted on intra-EU purchases also counts toward T1
    cursor.execute('''
        SELECT SUM(vat_amount) FROM transactions
        WHERE period_id = ? AND is_reverse_charge = 1
    ''', (period_id,))
    reverse_charge_vat = cursor.fetchone()[0] or 0

    t1 = t1 + reverse_charge_vat

    if t1 >= t2:
        t3 = round(t1 - t2, 2)
        t4 = 0
    else:
        t3 = 0
        t4 = round(t2 - t1, 2)

    cursor.execute('''
        SELECT SUM(net_amount) FROM transactions
        WHERE period_id = ? AND supply_type = 'intra_eu' AND transaction_type = 'purchase'
    ''', (period_id,))
    e2 = cursor.fetchone()[0] or 0

    cursor.execute('''
        SELECT SUM(net_amount) FROM transactions
        WHERE period_id = ? AND supply_type = 'intra_eu' AND transaction_type = 'sale'
    ''', (period_id,))
    e1 = cursor.fetchone()[0] or 0

    return {
        "T1": round(t1, 2),
        "T2": round(t2, 2),
        "T3": t3,
        "T4": t4,
        "E1": round(e1, 2),
        "E2": round(e2, 2)
    }


def generate_vat3_report(cursor, conn, period_id, business_id):
    """
    Calculates the VAT3 return for a period, saves it to vat3_returns,
    and prints a formatted report matching the Revenue VAT3 form layout.
    """

    result = calculate_vat3(cursor, period_id)

    cursor.execute("SELECT business_name, vat_registration_no FROM businesses WHERE business_id = ?", (business_id,))
    biz = cursor.fetchone()

    cursor.execute("SELECT period_start, period_end, due_date FROM vat_periods WHERE period_id = ?", (period_id,))
    period = cursor.fetchone()

    cursor.execute('''
        INSERT INTO vat3_returns 
        (period_id, T1_vat_on_sales, T2_vat_on_purchases, T3_vat_payable, 
         T4_vat_repayable, E1_intra_eu_sales, E2_intra_eu_purchases, generated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ''', (period_id, result["T1"], result["T2"], result["T3"],
          result["T4"], result["E1"], result["E2"]))

    conn.commit()

    print("=" * 50)
    print(f"VAT3 RETURN — {biz[0]}")
    print(f"VAT Reg No: {biz[1]}")
    print(f"Period: {period[0]} to {period[1]}")
    print(f"Due Date: {period[2]}")
    print("=" * 50)
    print(f"T1  VAT on Sales:          €{result['T1']:.2f}")
    print(f"T2  VAT on Purchases:      €{result['T2']:.2f}")
    print(f"T3  Net Payable:           €{result['T3']:.2f}")
    print(f"T4  Net Repayable:         €{result['T4']:.2f}")
    print(f"E1  Intra-EU Sales:        €{result['E1']:.2f}")
    print(f"E2  Intra-EU Purchases:    €{result['E2']:.2f}")
    print("=" * 50)

    return result
