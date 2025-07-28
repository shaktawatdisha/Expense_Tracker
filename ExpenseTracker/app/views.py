from rest_framework import permissions
from django.utils.timezone import now
from django.shortcuts import redirect
from rest_framework.response import Response
from .models import Expense, Category
from .serializers import ExpenseSerializer, CategorySerializer
from rest_framework.views import APIView
from rest_framework.renderers import TemplateHTMLRenderer
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from collections import OrderedDict
from django.utils import timezone


class ReportAPIView(APIView):
    """
    API view for generating expense reports.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'reports.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Monthly data aggregation------------------------------------------------------
        three_months_ago = date.today() - relativedelta(months=3)

        monthly_expenses = Expense.objects.filter(
            user=request.user,
            date__gte = three_months_ago,
        ).annotate(month=TruncMonth('date')).values('month').annotate(total=Sum('amount')).order_by('month')

        months = OrderedDict()
        for i in range(3):
            month_date = (date.today().replace(day=1) - timedelta(days=30*i)).replace(day=1)
            months[month_date.strftime('%b')] = {
                'month_name': month_date.strftime('%b'),
                'month_date': month_date,
                'total': 0,
                'height': 'h-0'  
            }
        
        max_total = max([e['total'] for e in monthly_expenses] or [0])
        for expense in monthly_expenses:
            month_name = expense['month'].strftime('%b')
            if month_name in months:
                months[month_name]['total'] = expense['total']
                max_height = 128 
                height_px = int((expense['total'] / max_total) * max_height) if max_total > 0 else 0
                months[month_name]['height'] = f"{height_px}px"
        
        months_data = list(reversed(months.values()))
        total_expense = sum(month['total'] for month in months_data)
        # Monthly data aggregation end------------------------------------------------------

        # Category data aggregation------------------------------------------------------
        today = timezone.now().date()
        first_day = today.replace(day=1)
        last_day = (first_day + timezone.timedelta(days=32)).replace(day=1) - timezone.timedelta(days=1)
        category_expenses = Expense.objects.filter(user=request.user,
                                                   date__range=[first_day, last_day]).values('category__name').annotate(total=Sum('amount')).order_by('-total')
        total_expenses_of_catrgory = sum(item['total'] for item in category_expenses)
    
        # Add percentage to each category
        for item in category_expenses:
            item['percentage'] = (item['total'] / total_expenses_of_catrgory) * 100 if total_expenses_of_catrgory > 0 else 0
        print('➡ ExpenseTracker/app/views.py:66 category_expenses:', category_expenses)
        

        # Create ordered dict for all months
        twelve_months_ago = date.today().replace(day=1) - relativedelta(months=11)

        monthly_expense_trend = Expense.objects.filter(
            user=request.user,
            date__gte=twelve_months_ago
        ).annotate(
            month=TruncMonth('date')
        ).values('month').annotate(
            total=Sum('amount')
        ).order_by('month')

        # Create ordered dict for all months
        months_labels = []
        months_totals = []
        for i in range(12):
            m_date = (twelve_months_ago + relativedelta(months=i))
            m_name = m_date.strftime('%b')
            months_labels.append(m_name)
            # find total or 0
            total = next((item['total'] for item in monthly_expense_trend if item['month'].strftime('%b') == m_name), 0)
            months_totals.append(round(total))

        context = {
            'months_data': months_data,
            'total_expense': total_expense,
            'category_data': category_expenses,
            'trend_labels': months_labels,
            'trend_totals': months_totals
        }
        print('➡ ExpenseTracker/app/views.py:105 context:', context)
        return Response(context)


# {% for month in months_data %}
#           <div class="w-1/6 bg-gray-200 {{month.height}} rounded-t">
#             <div class="h-3 border-t border-gray-500"></div>
#             <p class="text-sm text-center mt-2">{{month.month_name}}</p>
#           </div>
#           {% endfor %}

class DashboardAPIView(APIView):
    """
    API view for rendering the dashboard.
    """
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'dashboard.html'

    def get(self, request):
        # Assuming you want to render some data on the dashboard
        if not request.user.is_authenticated:
            return redirect('login')
        
        expenses = Expense.objects.filter(user=request.user)
        categories = Category.objects.all()
        return Response({'expenses': expenses, 'categories': categories})


class LoginAPIView(APIView):
    """
    API view for handling user login.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'login.html'

    def get(self, request):
        return Response({'message': 'Login Page'})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        return Response({'error': 'Invalid credentials'}, status=400)
    
class RegisterAPIView(APIView):
    """
    API view for handling user registration.
    """
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'register.html'

    def get(self, request):
        return Response({'message': 'Register Page'})

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return Response({'error': 'Passwords do not match'}, status=400)
        
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=400)
        
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        # Redirect to the login page after successful registration
        return redirect('dashboard')

class ExpenseAPIView(APIView):
    """
    API view for handling expense-related operations.
    """
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'transactions.html'

    def get(self, request):
        queryset = Expense.objects.all().order_by('-date')
        return Response({'expenses': queryset})
    
    
class ExpenseCreateAPIView(APIView):
    """
    API view for creating a new expense.
    """
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'transaction_create.html'

    def get(self, request):
        # serializer = ExpenseSerializer()
        categories = Category.objects.all()
        print('➡ ExpenseTracker/app/views.py:35 categories:', categories)
        return Response({'categories':categories}, status=200)
    
    def post(self, request):
        data = {
            'amount': request.POST.get('amount'),
            'description': request.POST.get('description'),
            'category': request.POST.get('category'),
        }
        
        user = User.objects.get(username="admin")
        serializer = ExpenseSerializer(data=data)
        print('➡ ExpenseTracker/app/views.py:144 serializer:', serializer)
        if serializer.is_valid():
            data = serializer.save(user=user)
            return redirect('expense-list')
        print('➡ ExpenseTracker/app/views.py serializer.errors:', serializer.errors)
        return Response(serializer.errors, status=400)

class CategoryAPIView(APIView):
    """
    API view for handling category-related operations.
    """
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'categories.html'

    def get(self, request):
        queryset = Category.objects.all()
        return Response({'categories': queryset})

class CategoryCreateAPIView(APIView):
    """
    API view for handling category-related operations.
    """
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'add_category.html'

    def get(self, request):
        queryset = Category.objects.all()
        return Response({'categories': queryset})

    def post(self, request):
        data = {
            'name': request.POST.get('name'),
        }
        print('➡ ExpenseTracker/app/views.py:82 data:', data)

        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return redirect('category-list')
        return Response(serializer.errors, status=400)



class LogoutAPIView(APIView):
    """
    API view for handling user logout.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        print('➡ ExpenseTracker/app/views.py:181 request:', request.user)
        # Log out the user
        from django.contrib.auth import logout
        logout(request)
        return redirect('login')
    

class ProfileAPIView(APIView):
    """
    API view for handling user profile operations.
    """
    permission_classes = [permissions.IsAuthenticated]
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'profile.html'

    def get(self, request):
        # Assuming you want to render the user's profile
        if not request.user.is_authenticated:
            return redirect('login')
        user = request.user
        return Response({'user': user})

    