from django.contrib import admin
from .models import Author, Category, Book, User, Transaction, Visit, AdminUser, Library

admin.site.register(AdminUser)
admin.site.register(Library)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(User)
admin.site.register(Transaction)
admin.site.register(Visit)