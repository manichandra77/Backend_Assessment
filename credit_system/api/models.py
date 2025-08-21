from django.db import models

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    phone_number = models.BigIntegerField(unique=True)
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

class Loan(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='loans')
    loan_id = models.AutoField(primary_key=True)
    loan_amount = models.DecimalField(max_digits=12, decimal_places=2)
    tenure = models.IntegerField()
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    monthly_payment = models.DecimalField(max_digits=10, decimal_places=2)
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()