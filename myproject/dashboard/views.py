from django.shortcuts import render, redirect
from .forms import BookForm, LibraryForm, LoginForm,UserForm,TransactionForm, VisitForm
from .models import AdminUser, Library, User,Book,Author,Category,Visit,Transaction
from django.db.models import Q,Count
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import AdminUserCreationForm
from django.contrib.auth import logout
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db import models
from django.forms.utils import ErrorList





@login_required(login_url='/login')
def dashboard_view(request):
    logged_in_user = request.user
    library = logged_in_user.library
    books_count = Book.objects.filter(library=library).count()
    users_count = User.objects.filter(library=library).count()
    transactions_count = Transaction.objects.filter(library=library).count()
    visits_count = Visit.objects.filter(library=library).count()
    transactions = Transaction.objects.filter(library=library).order_by('-transaction_date')[:5]
    visits = Visit.objects.filter(library=library).order_by('-visit_date')[:5]

    return render(request, 'dashboard.html', {
        'books_count': books_count,
        'users_count': users_count,
        'transactions_count': transactions_count,
        'visits_count': visits_count,
        'transactions': transactions,
        'visits': visits,
        'logged_in_user': logged_in_user,
        'active_page': 'dashboard'
    })

@login_required(login_url='/login')
def profile_view(request):
    # Access the logged-in user
    logged_in_user = request.user
    return render(request, 'profile.html',{'logged_in_user':logged_in_user,'active_page':'profile'})

@login_required(login_url='/login')
def books_view(request):
    logged_in_user = request.user
    library = logged_in_user.library
    query = request.GET.get('q')
    if query:
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(authors__name__icontains=query) |
            Q(central_id__icontains=query) |
            Q(local_id__icontains=query) |
            Q(categories__name__icontains=query) |
            Q(categories__index__icontains=query) |
            Q(notes__icontains=query),
            library=library
        ).distinct()
    else:
        books = Book.objects.filter(library=library)
    return render(request, 'books.html', {
        'books': books,
        'query': query,
        'logged_in_user': logged_in_user,
        'active_page': 'books'
    })

@login_required(login_url='/login')
def categories_view(request):
    logged_in_user = request.user
    library = logged_in_user.library
    query = request.GET.get('q')
    if query:
        categories_with_counts = Category.objects.filter(
            Q(name__icontains=query) |
            Q(index__icontains=query),
            book__library=library
        ).annotate(num_books=Count('book')).order_by('name')
    else:
        categories_with_counts = Category.objects.filter(
            book__library=library
        ).annotate(num_books=Count('book')).order_by('name')
    return render(request, 'categories.html', {
        'categories_with_counts': categories_with_counts,
        'query': query,
        'logged_in_user': logged_in_user,
        'active_page': 'categories'
    })

@login_required(login_url='/login')
def users_view(request):
    # Access the logged-in user
    logged_in_user = request.user
    library = logged_in_user.library
    query = request.GET.get('q')
    if query:
        users = User.objects.filter(Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(membership_id__icontains=query),library=library).distinct()
    else:
        users = User.objects.filter(library=library)
    return render(request, 'users.html',{'users': users , 'query': query,'logged_in_user':logged_in_user,'active_page': 'users'})

@login_required(login_url='/login')
def transactions_view(request):
    logged_in_user = request.user
    library = logged_in_user.library
    query = request.GET.get('q')
    if query:
        transactions = Transaction.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(book__title__icontains=query),
            library=library
        ).distinct()
    else:
        transactions = Transaction.objects.filter(library=library)
    return render(request, 'transactions.html', {
        'transactions': transactions,
        'query': query,
        'logged_in_user': logged_in_user,
        'active_page': 'transactions'
    })

@login_required(login_url='/login')
def visits_view(request):
    logged_in_user = request.user
    library = logged_in_user.library
    query = request.GET.get('q')
    if query:
        visits = Visit.objects.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(book__title__icontains=query) |
            Q(visit_date__icontains=query),
            library=library
        ).distinct()
    else:
        visits = Visit.objects.filter(library=library)
    return render(request, 'visits.html', {
        'visits': visits,
        'query': query,
        'logged_in_user': logged_in_user,
        'active_page': 'visits'
    })

@login_required(login_url='/login')
def add_book(request):
    # Access the logged-in user
    logged_in_user = request.user
    library = logged_in_user.library
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            central_id = form.cleaned_data['central_id']
            local_id = form.cleaned_data['local_id']

            if Book.objects.filter(models.Q(central_id=central_id), library=library).exists():
                form.add_error('central_id', "This book already exists in your library with the central ID.")
                categories = Category.objects.all()
                return render(request, 'add_book.html', {'form': form,'categories':categories, 'logged_in_user': logged_in_user, 'active_page': 'books'})
            
            if Book.objects.filter(models.Q(local_id=local_id), library=library).exists():
                form.add_error('local_id', "This book already exists in your library with the same local ID.")
                categories = Category.objects.all()
                return render(request, 'add_book.html', {'form': form,'categories':categories, 'logged_in_user': logged_in_user, 'active_page': 'books'})

            # Get the author's name from the form data
            author_name = form.cleaned_data['author_name']
            # Check if the author already exists
            author, created = Author.objects.get_or_create(name=author_name)

            # Save the book object but do not commit yet
            book = form.save(commit=False)
            book.user_cin = logged_in_user.cin
            book.library = library
            book.save()  # Save to generate a primary key

            # Assign the author to the book
            book.authors.add(author)

            # Add categories to the book
            categories = form.cleaned_data['categories']
            for category in categories:
                book.categories.add(category)

            # Save many-to-many relationships
            book.save()

            # Redirect to a success page or another view
            return redirect('books_view')
    else:
        form = BookForm()

    categories = Category.objects.all()

    return render(request, 'add_book.html', {'form': form, 'categories': categories,'logged_in_user':logged_in_user,'active_page': 'books'})

@login_required(login_url='/login')
def add_user(request):
    # Access the logged-in user
    logged_in_user = request.user
    library = logged_in_user.library
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            membership_id = form.cleaned_data['membership_id']
            cin = form.cleaned_data['cin']
            email = form.cleaned_data['email']
            if User.objects.filter(models.Q(membership_id=membership_id), library=library).exists():
                form.add_error('membership_id', "This user already exists in your library with the same membership ID.")
                return render(request, 'add_user.html', {'form': form, 'logged_in_user':logged_in_user, 'active_page': 'users'})

            if User.objects.filter(models.Q(cin=cin), library=library).exists():
                form.add_error('cin', "This user already exists in your library with the same CIN.")
                return render(request, 'add_user.html', {'form': form, 'logged_in_user':logged_in_user, 'active_page': 'users'})
            
            if User.objects.filter(models.Q(email=email), library=library).exists():
                form.add_error('email', "This user already exists in your library with the same email.")
                return render(request, 'add_user.html', {'form': form, 'logged_in_user':logged_in_user, 'active_page': 'users'})

            user = form.save(commit=False)
            user.user_cin = logged_in_user.cin
            user.library = library
            form.save()
            return redirect('users_view')
    else:
        form = UserForm()
    return render(request, 'add_user.html', {'form': form,'logged_in_user':logged_in_user,'active_page': 'users'})

@login_required(login_url='/login')
def add_transaction(request):
    # Access the logged-in user
    logged_in_user = request.user
    library = logged_in_user.library
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            print("Form is valid")
            membership_id = form.cleaned_data['membership_id']
            book_id = form.cleaned_data['book_id']
            get_or_return = form.cleaned_data['get_or_return']
            return_date = form.cleaned_data['return_date']

            # Verify if user exists with the provided membership ID
            user = User.objects.filter(library=library,membership_id=membership_id).first()
            if not user:
                # Add an error to the form
                form.add_error('membership_id', 'User with this membership ID does not exist.')
                return render(request, 'add_transaction.html', {'form': form})

            # Fetch the book object
            book = Book.objects.filter(
                models.Q(local_id=book_id) | models.Q(central_id=book_id),library=library).first()
            if not book:
                # Add an error to the form
                form.add_error('book_id', 'Book with this ID does not exist.')
                return render(request, 'add_transaction.html', {'form': form})

            # If "get" is selected
            if get_or_return == 'get':
                if book.quantity_available > 0:
                    # If the book is available, decrease its quantity by 1
                    new_quantity = book.quantity_available - 1
                    Book.objects.filter(models.Q(local_id=book_id) | models.Q(central_id=book_id),library=library).update(quantity_available=new_quantity)
                else:
                    # Handle case when book is not available
                    form.add_error('book_id', 'Book is not available.')
                    return render(request, 'add_transaction.html', {'form': form})
            # If "return" is selected
            elif get_or_return == 'return':
                # Increase the book's quantity by 1
                new_quantity = book.quantity_available + 1
                Book.objects.filter(models.Q(local_id=book_id) | models.Q(central_id=book_id),library=library).update(quantity_available=new_quantity)

            # If return date is provided, validate that it's not in the past
            if return_date and return_date < timezone.now().date():
                # Add an error to the form
                form.add_error('return_date', 'Return date cannot be in the past.')
                return render(request, 'add_transaction.html', {'form': form})

            # Create transaction object
            Transaction.objects.create(
                user=user,
                book=book,
                transaction_type=get_or_return,
                return_date=return_date,
                user_cin = logged_in_user.cin,
                library = logged_in_user.library
            )
            # Redirect to a success page or another view
            return redirect('transactions_view')
    else:
        form = TransactionForm()

    return render(request, 'add_transaction.html', {'form': form,'logged_in_user':logged_in_user,'active_page': 'transactions'})






@login_required(login_url='/login')
def add_visit(request):
    # Access the logged-in user
    logged_in_user = request.user
    library = logged_in_user.library

    if request.method == 'POST':
        form = VisitForm(request.POST)
        if form.is_valid():
            user_id = form.cleaned_data['user_id']
            book_id = form.cleaned_data.get('book_id', None)  # Use .get() to handle optional field

            user = User.objects.filter(membership_id=user_id, library=library).first()
            if not user:
                form.add_error('user_id', 'User with this membership ID does not exist.')
                return render(request, 'add_visit.html', {'form': form})

            if book_id:
                book = Book.objects.filter(models.Q(local_id=book_id) | models.Q(central_id=book_id), library=library).first()
                if not book:
                    form.add_error('book_id', 'Book with this ID does not exist.')
                    return render(request, 'add_visit.html', {'form': form})
                else:
                    visit = Visit.objects.create(user=user, user_cin=logged_in_user.cin, library=library)
                    visit.book.set([book])
            else:
                # Create visit without a book
                Visit.objects.create(user=user, user_cin=logged_in_user.cin, library=library)

            return redirect('visits_view')
    else:
        form = VisitForm()

    return render(request, 'add_visit.html', {'form': form, 'logged_in_user': logged_in_user, 'active_page': 'visits'})

def login_view(request):
    error = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cin = form.cleaned_data['cin']
            password = form.cleaned_data['password']
            try:
                user = AdminUser.objects.get(cin=cin)
                print(user.password)
                if password == user.password:
                    # Password matches, log in the user
                    login(request, user,backend='dashboard.backends.CINAuthBackend')
                    return redirect('dashboard_view')
                else:
                    error = "Invalid password"
            except AdminUser.DoesNotExist:
                error = "Invalid CIN"
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form, 'error': error})


def signup_view(request):
    libraries = Library.objects.order_by('city')
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = AdminUserCreationForm()
    return render(request, 'sign-up.html', {'form': form, 'libraries': libraries})

def logout_view(request):
    logout(request)
    return redirect('home')

def add_library(request):
    if request.method == 'POST':
        form = LibraryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('signup')
    else:
        form = LibraryForm()
    return render(request, 'add_library.html', {'form': form})

@login_required(login_url='/login')
def edit_book(request, pk):
    # Access the logged-in user
    logged_in_user = request.user
    library = logged_in_user.library
    book = get_object_or_404(Book, pk=pk)
    
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        
        if form.is_valid():
            local_id = form.cleaned_data['local_id']
            central_id = form.cleaned_data['central_id']

            if Book.objects.filter(local_id=local_id, library=library).exclude(pk=book.pk).exists():
                form.add_error('local_id', 'A book with this local ID already exists.')
                categories = Category.objects.all()
                return render(request, 'edit_book.html', {
                    'form': form, 
                    'book': book, 
                    'categories': categories,
                    'logged_in_user': logged_in_user, 
                    'active_page': 'books'
                })
            
            if Book.objects.filter(central_id=central_id, library=library).exclude(pk=book.pk).exists():
                form.add_error('central_id', 'A book with this central ID already exists.')
                categories = Category.objects.all()
                return render(request, 'edit_book.html', {
                    'form': form, 
                    'book': book, 
                    'categories': categories, 
                    'logged_in_user': logged_in_user, 
                    'active_page': 'books'
                })
            
            # Get the author's name from the form data
            author_name = form.cleaned_data['author_name']

            if author_name:
                # Check if the author already exists
                author, created = Author.objects.get_or_create(name=author_name)

            # Save the book object but do not commit yet
            book = form.save(commit=False)
            book.save()

            # Clear existing authors and assign the new author to the book
            book.authors.clear()
            if author_name:
                book.authors.add(author)

            # Clear existing categories and add new ones
            book.categories.clear()
            categories = form.cleaned_data['categories']
            for category in categories:
                book.categories.add(category)

            # Save many-to-many relationships
            book.save()

            # Redirect to a success page or another view
            return redirect('books_view')
    else:
        # Prepare initial data for the form
        initial_data = {
            'author_name': book.authors.first().name if book.authors.exists() else '',
        }
        form = BookForm(instance=book, initial=initial_data)
    
    # Ensure categories are pre-selected in the form
    categories = Category.objects.all()
    
    return render(request, 'edit_book.html', {
        'form': form, 
        'categories': categories, 
        'book': book,
        'logged_in_user': logged_in_user, 
        'active_page': 'books'
    })



@login_required(login_url='/login')
@require_POST
def delete_book(request,pk):
    book_id = request.POST.get('book_id')
    book = get_object_or_404(Book, pk=book_id)
    book.delete()
    return redirect('books_view')

@login_required(login_url='/login')
def edit_user(request, pk):
    # Access the logged-in user
    logged_in_user = request.user
    library = logged_in_user.library
    user = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            membership_id = form.cleaned_data['membership_id']
            cin = form.cleaned_data['cin']
            email = form.cleaned_data['email']

            # Check for unique fields excluding the current user
            if User.objects.filter(membership_id=membership_id, library=library).exclude(pk=user.pk).exists():
                form.add_error('membership_id', 'A user with this membership ID already exists.')
                return render(request, 'edit_user.html', {'form': form, 'user': user, 'logged_in_user': logged_in_user, 'active_page': 'users'})

            if User.objects.filter(cin=cin, library=library).exclude(pk=user.pk).exists():
                form.add_error('cin', 'A user with this CIN already exists.')
                return render(request, 'edit_user.html', {'form': form, 'user': user, 'logged_in_user': logged_in_user, 'active_page': 'users'})

            if User.objects.filter(email=email, library=library).exclude(pk=user.pk).exists():
                form.add_error('email', 'A user with this email already exists.')
                return render(request, 'edit_user.html', {'form': form, 'user': user, 'logged_in_user': logged_in_user, 'active_page': 'users'})

            form.save()
            return redirect('users_view')
    else:
        form = UserForm(instance=user)

    return render(request, 'edit_user.html', {'form': form, 'user': user, 'logged_in_user': logged_in_user, 'active_page': 'users'})


@login_required(login_url='/login')
@require_POST
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return redirect('users_view')

def home_view(request):
    return render(request, 'home.html')