from .models import Loan, Customer
from django.db.models import Sum
from datetime import date

def calculate_credit_score(customer_id):
    try:
        customer = Customer.objects.get(pk=customer_id)
    except Customer.DoesNotExist:
        return 0
        
    loans = Loan.objects.filter(customer=customer)
    
    paid_on_time_component = 100
    total_emis_tenure = loans.aggregate(total=Sum('tenure'))['total']
    if total_emis_tenure and total_emis_tenure > 0:
        emis_paid_on_time = loans.aggregate(total=Sum('emis_paid_on_time'))['total']
        paid_on_time_component = (emis_paid_on_time / total_emis_tenure) * 100

    num_loans_component = 100 - min(loans.count() * 10, 100)
    
    loan_volume_component = 100 - min(int((loans.aggregate(total=Sum('loan_amount'))['total'] or 0) / 10000), 100)
    
    current_year_loans = loans.filter(start_date__year=date.today().year).count()
    activity_component = min(current_year_loans * 10, 100)

    # Weighted score
    credit_score = int(
        (paid_on_time_component * 0.4) +
        (num_loans_component * 0.2) +
        (loan_volume_component * 0.2) +
        (activity_component * 0.2)
    )

    current_loans_sum = loans.filter(end_date__gte=date.today()).aggregate(total=Sum('loan_amount'))['total'] or 0
    if current_loans_sum > customer.approved_limit:
        return 0

    return min(credit_score, 100)

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    if interest_rate == 0:
        return loan_amount / tenure
    r = (interest_rate / 100) / 12
    n = tenure
    if (1 + r)**n == 1: return loan_amount / tenure
    emi = (loan_amount * r * (1 + r)**n) / ((1 + r)**n - 1)
    return round(emi, 2)