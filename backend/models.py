from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from CoffeeStation import settings


class Customer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=200, null=True, blank=False)
    last_name = models.CharField(max_length=200, null=True, blank=False)
    phone = PhoneNumberField(null=True, blank=False, unique=True)
    email = models.EmailField(max_length=200, null=True, blank=True, unique=True)
    device = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        if self.first_name:
            name = self.first_name + ' ' + self.last_name
        else:
            name = self.device
        return str(name)


class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Product(models.Model):
    image = models.ImageField(blank=True, null=True, upload_to="images/")
    name = models.CharField(blank=False, max_length=100)
    weight = models.CharField(choices=[('250', '0,25 kg'), ('500', '0,5 kg'), ('1000', '1 kg')], max_length=200)
    price = models.DecimalField(blank=False, max_digits=12, decimal_places=2)
    category = models.ManyToManyField(Category, verbose_name='category', blank=False)
    origin = models.CharField(blank=False, max_length=100)
    description = models.TextField(blank=False, max_length=200)
    contents = models.CharField(blank=False, max_length=200)
    available = models.BooleanField(blank=False, default=True)
    shown = models.BooleanField(blank=False, default=True)

    def __str__(self):
        return self.name

    @property
    def img_url(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    CHOICES = [('В обробці', 'В обробці'),
               ('Відправлено', 'Відправлено'),
               ('Скасовано', 'Скасовано'),
               ('Доставлено', 'Доставлено')]
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_order = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False, null=True, blank=False)
    status = models.CharField(max_length=200, choices=CHOICES, default='В обробці')

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

    def __str__(self):
        if self.customer.first_name:
            return str(self.id) + ' ' + self.customer.first_name + ' ' + self.customer.last_name
        else:
            return str(self.id)


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        return int(self.product.price) * self.quantity

    def __str__(self):
        return self.product.name


class Shipping(models.Model):
    CHOICES = [
        ('Оплата при отриманні', 'Оплата при отриманні'),
        ('Оплата на картку', 'Оплата на картку')
    ]
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, blank=False, null=True)
    city = models.CharField(max_length=200, blank=False)
    warehouse = models.CharField(max_length=200, blank=False)
    comment = models.CharField(max_length=300, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    payment = models.CharField(max_length=200, choices=CHOICES, default='Оплата при отриманні')

    def __str__(self):
        return self.city




