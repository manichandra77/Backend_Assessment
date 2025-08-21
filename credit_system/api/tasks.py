from celery import shared_task
import pandas as pd
from .models import Customer, Loan
from django.db import transaction

@shared_task
def ingest_data_task():
    try:
        # --- Make sure your Excel files are named correctly ---
        customer_df = pd.read_excel('customer_data.xlsx')
        loan_df = pd.read_excel('loan_data.xlsx')
    except FileNotFoundError as e:
        print(f"Error: {e}. Make sure Excel files are in the root directory.")
        return

    # --- Ingest Customer Data ---
    with transaction.atomic():
        customers_to_update = []
        customers_to_create = []
        existing_customer_ids = set(Customer.objects.values_list('customer_id', flat=True))

        for _, row in customer_df.iterrows():
            customer_data = {
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'age': row['Age'],  # Reading the 'Age' column
                'phone_number': row['phone_number'],
                'monthly_salary': row['monthly_salary'],
                'approved_limit': row['approved_limit'],
            }
            if row['customer_id'] in existing_customer_ids:
                customer = Customer(customer_id=row['customer_id'], **customer_data)
                customers_to_update.append(customer)
            else:
                customer = Customer(customer_id=row['customer_id'], **customer_data)
                customers_to_create.append(customer)
        
        update_fields = ['first_name', 'last_name', 'age', 'phone_number', 'monthly_salary', 'approved_limit']
        if customers_to_create:
            Customer.objects.bulk_create(customers_to_create)
        if customers_to_update:
            Customer.objects.bulk_update(customers_to_update, fields=update_fields)

    # --- Ingest Loan Data (No changes needed here) ---
    with transaction.atomic():
        loans_to_create = []
        for _, row in loan_df.iterrows():
            loans_to_create.append(Loan(
                customer_id=row['customer_id'], loan_id=row['loan_id'],
                loan_amount=row['loan_amount'], tenure=row['tenure'],
                interest_rate=row['interest_rate'], monthly_payment=row['monthly_repayment'],
                emis_paid_on_time=row['EMIs_paid_on_time'],
                start_date=row['start_date'], end_date=row['end_date']
            ))
        Loan.objects.bulk_create(loans_to_create, ignore_conflicts=True)