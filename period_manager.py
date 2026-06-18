"""
period_manager.py
Manages VAT filing periods for the Irish VAT3 compliance tool.

Contains:
- generate_vat_period(): creates a new bi-monthly VAT period with correct due date
- check_overdue_periods(): flags any open periods past their Revenue due date
"""

from datetime import datetime
import calendar


def generate_vat_period(cursor, conn, business_id, period_start_str):
    """
    Creates a new bi-monthly VAT period for a given business.
    Due date is set to the 23rd of the month following the period end,
    in line with Irish Revenue ROS filing requirements.
    """

    period_start = datetime.strptime(period_start_str, "%Y-%m-%d")

    end_month = period_start.month + 1
    end_year = period_start.year
    if end_month > 12:
        end_month -= 12
        end_year += 1

    last_day = calendar.monthrange(end_year, end_month)[1]
    period_end = datetime(end_year, end_month, last_day)

    due_month = period_end.month + 1
    due_year = period_end.year
    if due_month > 12:
        due_month -= 12
        due_year += 1
    due_date = datetime(due_year, due_month, 23)

    cursor.execute('''
        INSERT INTO vat_periods (business_id, period_start, period_end, due_date, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (business_id,
          period_start.strftime("%Y-%m-%d"),
          period_end.strftime("%Y-%m-%d"),
          due_date.strftime("%Y-%m-%d"),
          "open"))

    conn.commit()
    new_period_id = cursor.lastrowid

    print(f"Period created: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')} | Due: {due_date.strftime('%Y-%m-%d')}")
    return new_period_id


def check_overdue_periods(cursor, business_id):
    """
    Lists all open VAT periods whose Revenue due date has passed.
    These represent unfiled or late returns that may incur penalties.
    """

    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute('''
        SELECT period_id, period_start, period_end, due_date FROM vat_periods
        WHERE business_id = ? AND status = 'open' AND due_date < ?
    ''', (business_id, today))

    overdue = cursor.fetchall()

    if not overdue:
        print("No overdue periods — all filing obligations are current")
    else:
        print(f"{len(overdue)} overdue period(s) found:")
        for row in overdue:
            print(f"  OVERDUE — Period {row[0]} ({row[1]} to {row[2]}) was due {row[3]}")

    return overdue
