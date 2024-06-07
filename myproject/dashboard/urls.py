from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('sign-up', views.signup_view, name='signup'),
    path('dashboard', views.dashboard_view, name='dashboard_view'),
    path('profile', views.profile_view, name='profile_view'),
    path('books', views.books_view, name='books_view'),
    path('categories', views.categories_view, name='categories_view'),
    path('users', views.users_view, name='users_view'),
    path('transactions', views.transactions_view, name='transactions_view'),
    path('visits', views.visits_view, name='visits_view'),
    path('books/add', views.add_book, name='add_book'),
    path('users/add', views.add_user, name='add_user'),
    path('transactions/add', views.add_transaction, name='add_transaction'),
    path('visits/add', views.add_visit, name='add_visit'),
    path('books/edit/<int:pk>/', views.edit_book, name='edit_book'),
    path('books/delete/<int:pk>/', views.delete_book, name='delete_book'),
    path('add_library', views.add_library, name='add_library'),
    path('users/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('users/delete/<int:pk>/', views.delete_user, name='delete_user'),
    path('', views.home_view, name='home'),
]