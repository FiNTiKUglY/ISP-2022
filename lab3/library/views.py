import operator

from django.shortcuts import render, redirect
from django.views import View

from .models import Book, Order, Mail
from .forms import SignUpForm, LogInForm, MailForm
from django.contrib.auth import login, logout


class BookList(View):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        books = sorted(books, key=operator.attrgetter('title'))
        return render(request, 'list.html', {'books': books})

    def post(self, request, *args, **kwargs):
        books = Book.objects.filter(title__icontains=request.POST['search'])
        books = sorted(books, key=operator.attrgetter('title'))
        return render(request, 'list.html', {'books': books})


class Registration(View):
    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
        return render(request, 'registration.html', {'form': form})

    def get(self, request, *args, **kwargs):
        form = SignUpForm()
        return render(request, 'registration.html', {'form': form})


class LogIn(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logout(request)
            return redirect('')
        else:
            form = LogInForm()
        return render(request, 'login.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = LogInForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('')
        return render(request, 'login.html', {'form': form})


class OrderViewer(View):
    def get(self, request, *args, **kwargs):
        active_order = Order.objects.filter(user__username=request.user.get_username(), is_active=True).first()
        mails = Mail.objects.filter(order__user__username=request.user.get_username())
        return render(request, 'orders.html', {'active_order': active_order, 'mails': mails})


class AddInOrder(View):
    def add_in_order(self, request, id):
        order = Order.objects.filter(is_active=True).first()
        if order is None:
            order = Order()
            order.user = request.user
            order.is_active = True
            order.save()
        order.book.add(Book.objects.get(id=id))
        return redirect('orders')


class RemoveBook(View):
    def get(self, request, id1, id2):
        order = Order.objects.get(id=id1)
        order.book.remove(Book.objects.get(id=id2))
        return redirect('orders')


class BookViewer(View):
    def get(self, request, id):
        book = Book.objects.get(id=id)
        return render(request, 'book.html', {'book': book})


class MailCreator(View):
    def get(self, request, id):
        order = Order.objects.get(id=id)
        form = MailForm()
        return render(request, 'mail.html', {'form': form})

    def post(self, request, id):
        order = Order.objects.get(id=id)
        form = MailForm(data=request.POST)
        if form.is_valid():
            self.order.is_active = False
            self.order.save()
            mail = Mail()
            mail.name = form.cleaned_data['name']
            mail.surname = form.cleaned_data['surname']
            mail.adress = form.cleaned_data['adress']
            mail.index = form.cleaned_data['index']
            mail.order = self.order
            mail.save()
            return redirect('orders')
        return render(request, 'mail.html', {'form': form})
