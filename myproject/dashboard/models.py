from django.db import models
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.utils import timezone

class Library(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    zipCode = models.CharField(max_length=10)

    def __str__(self):
        return self.name

class AdminUser(models.Model):
    email = models.EmailField(unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField()
    cin = models.CharField(max_length=8, unique=True)
    phone = models.CharField(max_length=20)
    password = models.CharField(max_length=100)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_authenticated = models.BooleanField(default=True)

    def set_password(self, password):
        self.password = password
    
    def clean(self):
        super().clean()
        
        if self.birth_date is not None:
            if self.birth_date > datetime.now().date():
                raise ValidationError({'birth_date': 'Birth date cannot be in the future.'})
            
            today = datetime.today()
            age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            if age < 12:
                raise ValidationError({'birth_date': 'You must be 12 or older.'})
        
        if self.cin is not None:
            if not self.cin.isdigit() or len(self.cin) != 8 or int(self.cin) <= 0:
                raise ValidationError({'cin': 'Invalid CIN number.'})

    def __str__(self):
        return self.cin

class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(models.Model):
    index = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Book(models.Model):
    central_id = models.CharField(max_length=10)
    local_id = models.CharField(max_length=10)
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author)
    categories = models.ManyToManyField(Category)
    quantity_available = models.PositiveIntegerField()
    notes = models.TextField(null=True, blank=True)
    user_cin = models.CharField(max_length=8)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('central_id', 'library'), ('local_id', 'library'))

    def save(self, *args, **kwargs):
        self.central_id = self.central_id.upper()
        self.local_id = self.local_id.upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

def default_membership_validity():
    return (datetime.now() + relativedelta(years=1)).date()

class User(models.Model):
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField()
    cin = models.CharField(max_length=8, blank=True, null=True)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    membership_id = models.CharField(max_length=10)
    membership_validity = models.DateField(default=default_membership_validity())
    user_cin = models.CharField(max_length=8)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('membership_id', 'library'),('email', 'library'),('cin', 'library'))

    def clean(self):
        super().clean()
        
        if self.birth_date is not None:
            if self.birth_date > datetime.now().date():
                raise ValidationError({'birth_date': 'Birth date cannot be in the future.'})
            
            today = datetime.today()
            age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            if age < 12:
                raise ValidationError({'birth_date': 'You must be 12 or older.'})
        
        if self.cin is not None:
            if not self.cin.isdigit() or len(self.cin) != 8 or int(self.cin) <= 0:
                raise ValidationError({'cin': 'Invalid CIN number.'})

    def __str__(self):
        return self.membership_id

class Transaction(models.Model):
    GET = 'get'
    RETURN = 'return'
    TRANSACTION_TYPE_CHOICES = [
        (GET, 'Get'),
        (RETURN, 'Return'),
    ]
    
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    transaction_date = models.DateTimeField(default=timezone.now)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    return_date = models.DateField(null=True, blank=True)
    user_cin = models.CharField(max_length=8)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.membership_id} - {self.book.title} - {self.transaction_type}'

    class Meta:
        ordering = ['-transaction_date']

class Visit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ManyToManyField(Book)
    visit_date = models.DateField(auto_now_add=True)
    visit_time = models.TimeField(auto_now_add=True)
    user_cin = models.CharField(max_length=8)
    library = models.ForeignKey(Library, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.membership_id} visited your library on {self.visit_date} at {self.visit_time}"

