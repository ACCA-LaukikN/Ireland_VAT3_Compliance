"""
main.py
Entry point for the Irish VAT3 Compliance Tool.

Run with: python main.py

Provides an interactive CLI menu for:
- Adding transactions (sales and purchases)
- Viewing VAT3 calculations for a period
- Generating full formatted VAT3 returns
- Checking overdue filing periods
- Creating new VAT periods
"""

from db_setup import initialise_database
from vat_calculator import add_transaction, calculate_vat3, generate_vat3_report
from period_manager import generate_vat_period, check_overdue_periods


def main_menu(conn, cursor):
    while True:
        print("\n" + "=" * 40)
        print("  IRISH VAT3 COMPLIANCE TOOL")
        print("=" * 40)
        print("  1. Add a transaction")
        print("  2. View VAT3 calculation for a period")
        print("  3. Generate full VAT3 report")
        print("  4. Check overdue periods")
        print("  5. Create new VAT period")
        print("  6. Exit")
        print("=" * 40)

        choice = input("Choose an option (1-6): ").strip()

        if choice == "1":
            print("\n--- ADD TRANSACTION ---")
            business_id = int(input("Business ID: "))
            period_id = int(input("Period ID: "))
            date = input("Transaction date (YYYY-MM-DD): ")
            trans_type = input("Type (sale/purchase): ").strip().lower()
            counterparty = input("Counterparty name: ")
            net_amount = float(input("Net amount (€): "))
            print("\nVAT Rates:")
            print("  1 = Standard (23%)   2 = Reduced (13.5%)")
            print("  3 = Second Reduced (9%)  4 = Livestock (4.8%)")
            print("  5 = Zero Rated (0%)  6 = Exempt (0%)")
            vat_rate_id = int(input("VAT rate ID: "))
            invoice_number = input("Invoice number: ")
            supply_type = input("Supply type (domestic/intra_eu/export): ").strip().lower()
            reverse_input = input("Reverse charge? (y/n): ").strip().lower()
            is_reverse_charge = reverse_input == "y"
            counterparty_vat_no = None
            if supply_type == "intra_eu":
                counterparty_vat_no = input("Counterparty VAT number: ")

            add_transaction(cursor, conn, business_id, period_id, date, trans_type,
                            counterparty, net_amount, vat_rate_id, invoice_number,
                            supply_type, counterparty_vat_no=counterparty_vat_no,
                            is_reverse_charge=is_reverse_charge)

        elif choice == "2":
            print("\n--- VAT3 CALCULATION ---")
            period_id = int(input("Period ID: "))
            result = calculate_vat3(cursor, period_id)
            print()
            for box, value in result.items():
                print(f"  {box}: €{value:.2f}")

        elif choice == "3":
            print("\n--- GENERATE VAT3 REPORT ---")
            business_id = int(input("Business ID: "))
            period_id = int(input("Period ID: "))
            generate_vat3_report(cursor, conn, period_id, business_id)

        elif choice == "4":
            print("\n--- OVERDUE PERIODS ---")
            business_id = int(input("Business ID: "))
            check_overdue_periods(cursor, business_id)

        elif choice == "5":
            print("\n--- CREATE VAT PERIOD ---")
            business_id = int(input("Business ID: "))
            period_start = input("Period start date (YYYY-MM-DD, must be 1st of month): ")
            generate_vat_period(cursor, conn, business_id, period_start)

        elif choice == "6":
            print("\nExiting. All data saved to vat3.db")
            break

        else:
            print("Invalid option — please enter a number between 1 and 6")


if __name__ == "__main__":
    conn, cursor = initialise_database()
    main_menu(conn, cursor)
