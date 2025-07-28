from app import views
from django.urls import path


urlpatterns = [
    path('expenses/', views.ExpenseAPIView.as_view(), name='expense-list'),
    path('expenses/create/', views.ExpenseCreateAPIView.as_view(), name='expense-create'),
    path('category/create/', views.CategoryCreateAPIView.as_view(), name='category-create'),
    path('category/', views.CategoryAPIView.as_view(), name='category-list'),
    path('dashboard/', views.DashboardAPIView.as_view(), name='dashboard'),
    path('reports/', views.ReportAPIView.as_view(), name='reports'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
    path('profile/', views.ProfileAPIView.as_view(), name='profile'),
]