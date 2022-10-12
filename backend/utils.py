import json
import uuid

import requests
from django.core.exceptions import MultipleObjectsReturned
from backend.models import Customer, Order


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


def get_np_cities():
    url = 'https://api.novaposhta.ua/v2.0/json/'
    data = {
        "apiKey": "",
        "modelName": "Address",
        "calledMethod": "getCities",
        "methodProperties": {}
    }
    city_json = requests.post(url, json=data).text
    city_dict = {d['Description']: d['Ref'] for d in json.loads(city_json)['data']}

    return city_dict
