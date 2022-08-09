from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from .models import *
import requests
from .forms import CustomerForm, ShippingForm, RegisterUserForm
import uuid
import json


def user_check(request):
    try:
        customer = request.user.customer
    except:
        try:
            device = request.session['device']
            customer = Customer.objects.get(device=device)
        except:
            request.session['device'] = str(uuid.uuid4())
            customer = Customer.objects.create(device=request.session['device'])
    return customer


def order_check(customer):
    try:
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    except MultipleObjectsReturned:
        order = Order.objects.filter(customer=customer, complete=False).last()
    return order


def store(request):         # store page
    customer = user_check(request)
    order = order_check(customer)

    products = Product.objects.all()
    order_items = OrderItem.objects.filter(order=order)
    order_items_tuple = tuple(str(i) for i in order_items)
    return render(request, 'store.html', {'products': products, 'order': order, 'order_items_tuple': order_items_tuple})


def add_item(request, pk):                # add item to cart
    product = Product.objects.get(pk=pk)
    customer = user_check(request)
    order = order_check(customer)

    order_item, created = OrderItem.objects.get_or_create(order=order, product=product)
    order_item.quantity += 1
    order.save()

    return HttpResponse('Додано до кошика')


def get_cart_number(request):
    customer = user_check(request)
    order = order_check(customer)

    cart = order.get_cart_items
    return JsonResponse({'cart': str(cart)})


def product(request, pk):                           # product detail page
    product = Product.objects.get(id=pk)
    customer = user_check(request)
    order = order_check(customer)

    if request.method == 'POST':
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
        orderItem.quantity += int(request.POST['quantity'])
        orderItem.save()

        messages.success(request, ("Додано до кошика"))
        return HttpResponseRedirect(reverse('product', args=[str(product.id)]))

    return render(request, 'product.html', {'product': product, 'order': order})


def cart(request):
    customer = user_check(request)
    order = order_check(customer)

    context = {'order': order, 'customer': customer}
    return render(request, 'cart.html', context)


def minus_quantity(request, pk):
    item = OrderItem.objects.get(pk=pk)
    customer = user_check(request)

    if customer == item.order.customer:
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('store')


def plus_quantity(request, pk):
    item = OrderItem.objects.get(pk=pk)
    customer = user_check(request)

    if customer == item.order.customer:
        if item.quantity < 100:
            item.quantity += 1
            item.save()
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('store')


def remove_item(request, pk):                       # remove item from cart
    item = OrderItem.objects.get(pk=pk)
    customer = user_check(request)

    if customer == item.order.customer:
        item.delete()
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('store')


def checkout(request, order_id):                             # order checkout page
    customer = user_check(request)

    order = Order.objects.get(pk=order_id)

    url = 'https://api.novaposhta.ua/v2.0/json/'
    data = {
        "apiKey": "",
        "modelName": "Address",
        "calledMethod": "getCities",
        "methodProperties": {}
    }
    city_json = requests.post(url, json=data).text
    city_dict = {d['Description']: d['Ref'] for d in json.loads(city_json)['data']}

    if not order.orderitem_set.all():
        return redirect('store')

    if request.method == 'POST':
        form2 = ShippingForm(request.POST)
        if form2.is_valid():
            if not request.user.is_authenticated:
                form = CustomerForm(request.POST or None, instance=customer)
                if form.is_valid():
                    form.save()
            shipping = form2.save(commit=False)
            shipping.customer = customer
            shipping.order = order
            shipping.city = request.POST['city']
            shipping.warehouse = request.POST['warehouse']
            shipping.save()
            order.complete = True
            order.save()
            return redirect('success_page')

    else:
        form = CustomerForm(instance=customer)
        form2 = ShippingForm()

    return render(request, 'checkout.html', {'form': form,
                                             'form2': form2,
                                             'order': order,
                                             'city_dict': city_dict,
                                             'customer': customer})


def order_copy(request, pk):                             # make order copy from user_page
    order = Order.objects.get(pk=pk)
    if request.user.customer == order.customer:
        customer = request.user.customer
        new_order = Order.objects.create(customer=customer)
        for item in order.orderitem_set.all():
            OrderItem.objects.create(product=item.product, order=new_order, quantity=item.quantity)
        return redirect('checkout', new_order.id)


def success_page(request):
    return render(request, 'success_page.html', {})


# ------------------------USERS----------------------------


def create_password(request):
    customer = user_check(request)

    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data['password1']
            phone = customer.phone
            user.phone = phone
            user.first_name = customer.first_name
            user.last_name = customer.last_name
            user.save()
            user = authenticate(phone=phone, password=password)
            login(request, user)
            customer.user = user
            customer.save()
            messages.success(request, (
                'Вас було успішно зареєстровано! Переглянути історію ваших замовлень ви можете в особистому кабінеті.'))
            return redirect('store')

    else:
        form = RegisterUserForm()

    return render(request, 'create_password.html', {'form': form})


def login_user(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']
        user = authenticate(request, phone=phone, password=password)
        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.success(request, ("Щось пійшло не так :( Спробуйте ще раз!"))
            return redirect('login_user')
    else:
        return render(request, 'login_user.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, ("Ви вийшли з облікового запису"))
    return redirect('store')


def user_registration(request):
    customer = user_check(request)
    form = RegisterUserForm(request.POST or None)
    form2 = CustomerForm(request.POST or None, instance=customer)
    if form.is_valid() and form2.is_valid():
        customer = form2.save()
        user = form.save(commit=False)
        password = form.cleaned_data['password1']
        phone = customer.phone
        user.phone = phone
        user.first_name = customer.first_name
        user.last_name = customer.last_name
        user.save()
        user = authenticate(phone=phone, password=password)
        login(request, user)
        customer.user = user
        customer.device = None
        customer.save()
        messages.success(request, (
            'Вас було успішно зареєстровано! Переглянути історію ваших замовлень ви можете в особистому кабінеті.'))
        return redirect('store')

    return render(request, 'user_registration.html', {'form': form, 'form2': form2})


def user_page(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        orders = Order.objects.filter(customer=customer, complete=True).order_by('-date_order')
        order = order_check(customer)
        return render(request, 'user_page.html', {'order': order, 'orders': orders, 'customer': customer})

    else:
        messages.success(request, ('Щоб перейти в особистий кабінет будь ласка авторизуйтесь.'))
        redirect('login_user')



