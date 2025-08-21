from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanDetailSerializer, CustomerLoanSerializer
from .services import calculate_credit_score, calculate_monthly_installment
from django.db.models import Sum
from datetime import date
from dateutil.relativedelta import relativedelta

class RegisterView(APIView):
    def post(self, request):
        monthly_salary = request.data.get('monthly_income')
        approved_limit = round(36 * monthly_salary / 100000) * 100000
        
        customer = Customer.objects.create(
            first_name=request.data.get('first_name'),
            last_name=request.data.get('last_name'),
            age=request.data.get('age'),
            monthly_salary=monthly_salary,
            approved_limit=approved_limit,
            phone_number=request.data.get('phone_number'),
        )
        serializer = CustomerSerializer(customer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CheckEligibilityView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount'))
        interest_rate = float(request.data.get('interest_rate'))
        tenure = int(request.data.get('tenure'))
        
        try:
            customer = Customer.objects.get(pk=customer_id)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
            
        credit_score = calculate_credit_score(customer_id)
        
        current_emis = Loan.objects.filter(
            customer=customer, end_date__gte=date.today()
        ).aggregate(total=Sum('monthly_payment'))['total'] or 0
        
        if current_emis > customer.monthly_salary / 2:
            return Response({
                'customer_id': customer_id, 'approval': False, 'interest_rate': interest_rate,
                'corrected_interest_rate': None, 'tenure': tenure, 'monthly_installment': None,
                'message': 'High debt burden: EMIs exceed 50% of salary.'
            }, status=status.HTTP_200_OK)

        approval = False
        corrected_interest_rate = interest_rate

        if credit_score > 50:
            approval = True
        elif 30 < credit_score <= 50:
            approval = interest_rate > 12
            corrected_interest_rate = 12.0
        elif 10 < credit_score <= 30:
            approval = interest_rate > 16
            corrected_interest_rate = 16.0
        
        final_interest = corrected_interest_rate if not approval and corrected_interest_rate > interest_rate else interest_rate
        
        response_data = {
            'customer_id': customer_id, 'approval': approval, 'interest_rate': interest_rate,
            'corrected_interest_rate': final_interest if final_interest != interest_rate else None,
            'tenure': tenure,
            'monthly_installment': calculate_monthly_installment(loan_amount, final_interest, tenure)
        }
        return Response(response_data, status=status.HTTP_200_OK)

class CreateLoanView(APIView):
    def post(self, request):
        eligibility_view = CheckEligibilityView()
        eligibility_response = eligibility_view.post(request)
        eligibility_data = eligibility_response.data
        
        if not eligibility_data['approval']:
            return Response({
                'loan_id': None, 'customer_id': request.data.get('customer_id'),
                'loan_approved': False, 'message': 'Loan not approved based on eligibility check.',
                'monthly_installment': None,
            }, status=status.HTTP_200_OK)

        final_interest_rate = request.data.get('interest_rate')
        
        loan = Loan.objects.create(
            customer_id=request.data.get('customer_id'),
            loan_amount=request.data.get('loan_amount'),
            tenure=request.data.get('tenure'),
            interest_rate=final_interest_rate,
            monthly_payment=eligibility_data['monthly_installment'],
            emis_paid_on_time=0,
            start_date=date.today(),
            end_date=date.today() + relativedelta(months=request.data.get('tenure'))
        )
        return Response({
            'loan_id': loan.loan_id, 'customer_id': loan.customer.customer_id,
            'loan_approved': True, 'message': 'Loan Approved',
            'monthly_installment': loan.monthly_payment
        }, status=status.HTTP_201_CREATED)

class ViewLoanView(generics.RetrieveAPIView):
    queryset = Loan.objects.all()
    serializer_class = LoanDetailSerializer
    lookup_field = 'loan_id'

class ViewCustomerLoansView(generics.ListAPIView):
    serializer_class = CustomerLoanSerializer
    def get_queryset(self):
        customer_id = self.kwargs.get('customer_id')
        return Loan.objects.filter(customer_id=customer_id)