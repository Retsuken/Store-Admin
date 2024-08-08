from django.db import models
from django.db.models import Count
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
class User(models.Model):
    name = models.TextField()
    password = models.TextField()
    email = models.EmailField()
    phone = models.PositiveIntegerField(default='+7')
    balans_prihod = models.IntegerField(default=0)
    balans_rashod = models.IntegerField(default=0)
    sale = models.TextField()
    balans = models.IntegerField(default=0)
    comment = models.TextField()
    bonus = models.IntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.balans = self.balans_prihod - self.balans_rashod
        super(User, self).save(*args, **kwargs)
    def __str__(self):
        return self.name
    
    
    def check_password(self, raw_password):
        # Используйте библиотеку для хеширования паролей, например bcrypt
        # для сравнения хешированного пароля с raw_password
        # ...
        return True  # Замените на реальную проверку пароля



class Product(models.Model):
    STATUS_CHOICES = (
        ('G', 'Продан'),
        ('Y', 'В продаже'),
        ('O', 'Ожидает подтверждения'),
        ('R', 'Не выполнен'),
        ('H', 'Проблемный'),
    )

    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    name = models.CharField(max_length=100)
    product_id = models.TextField(unique=True)
    date = models.DateField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    cost = models.IntegerField()
    employee = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products_images')
    product_descr = models.TextField()
    product_comm = models.TextField()
    product_addr = models.TextField(_('Характеристики'))
    quantity = models.IntegerField()


    def __str__(self):
        return self.name
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.values('name').annotate(quantity=Count('name'))
        return queryset
    

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(Product, related_name='carts')
    quantity = models.IntegerField(null=True, blank=True)
    def update_total(self):
        self.total_price = 0
        self.total_quantity = 0
        for cart_item in self.cartitem_set.all():
            self.total_price += cart_item.quantity * cart_item.product.cost
            self.total_quantity += cart_item.quantity
        self.save()

# Модель CartItem должна хранить количество товара в корзине
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 

class Product_Add(models.Model):
    product_name = models.TextField()
    product_descr = models.TextField()
    image = models.ImageField(upload_to='products_images')
    product_town = models.TextField()
    product_distr = models.TextField()
    product_addr = models.TextField()
    product_comm = models.TextField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_employee = models.TextField()
    


class District(models.Model):
    district = models.TextField()
    
    def __str__(self):
        return self.district
    
class City(models.Model):
    city = models.TextField()
    districts = models.ManyToManyField(District)

    def __str__(self):
        return self.city
    
class Name(models.Model):
    name = models.TextField()

    def __str__(self):
        return self.name
    

class AccessPage(models.Model):
    name = models.CharField(max_length=255)
    is_accessible = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Team(models.Model):
    STATUS_CHOICES = (
        ('Активный', 'Активный'),
        ('Не активный', 'Не активный'),
        ('Все клиенты', 'Все клиенты'),
        ('Заблокированный', 'Заблокированный'),
    )
    ROLE_CHOICES = (
        ('Сотрудник', 'Сотрудник'),
        ('Менеджер', 'Менеджер'),
        ('Технический сотрудник', 'Технический сотрудник'),
        ('Администратор магазина', 'Администратор магазина'),
    )
    login = models.TextField(unique=True)
    balans = models.IntegerField(null=True, blank=True)
    comment = models.CharField(max_length=156)
    rashod = models.IntegerField()
    prihod = models.IntegerField()
    client_id = models.TextField(null=True, blank=True)
    quantity_orders = models.IntegerField(null=True, blank=True)
    quantity_problems_order = models.IntegerField(null=True, blank=True)
    telegram = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    email = models.EmailField(null=True, blank=True)
    skidka = models.IntegerField(null=True, blank=True)
    orders_problem_sum = models.IntegerField(null=True, blank=True)
    orders_zagruz_sum = models.IntegerField(null=True, blank=True)
    kolvo_tovarov = models.IntegerField(null=True, blank=True)
    role = models.CharField(max_length=60, choices=ROLE_CHOICES)
    access_pages = models.ManyToManyField(AccessPage)
    password = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.login
    def check_password(self, raw_password):
        # Используйте библиотеку для хеширования паролей, например bcrypt
        # для сравнения хешированного пароля с raw_password
        # ...
        return True  # Замените на реальную проверку пароля


class Payment(models.Model):
    Payment_Sposob = models.TextField()
    Vid_oplata = models.TextField()
    info = models.TextField()



class Client(models.Model):
    STATUS_CHOICES = (
        ('Активный', 'Активный'),
        ('Не активный', 'Не активный'),
        ('Все клиенты', 'Все клиенты'),
        ('Заблокированный', 'Заблокированный'),
    )
    ROLE_CHOICES = (
        ('Сотрудник', 'Сотрудник'),
        ('Менеджер', 'Менеджер'),
        ('Технический сотрудник', 'Технический сотрудник'),
        ('Администратор магазина', 'Администратор магазина'),
    )
    login = models.TextField()
    client_id = models.IntegerField()
    quantity_orders = models.IntegerField()
    quantity_problems_order = models.IntegerField()
    date = models.DateTimeField()
    balans = models.IntegerField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    orders_buy = models.TextField()
    orders_buy_sum = models.TextField()
    orders_problem_kolvo = models.IntegerField()
    orders_problem_sum = models.IntegerField()
    procent_orders_problem = models.IntegerField()
    telegram = models.TextField()
    skidka = models.IntegerField()
    Email = models.TextField()
    role = models.CharField(max_length=60, choices=ROLE_CHOICES)
    otmen_zakaz = models.IntegerField()
    zakaz_ojid_oplat = models.IntegerField()

    def __str__(self):
        return self.login

    

class Orders(models.Model):
    STATUS_CHOICES = (
        ('G', 'Продан'),
        ('O', 'Ожидает подтверждения'),
        ('R', 'Отменён'),
        ('H', 'Проблемный'),
        ('F', 'Создан')
    )
    name_tovar = models.CharField(max_length=156)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES)
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.TextField()
    date = models.DateTimeField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    payment_card = models.CharField(max_length=156)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    employee = models.CharField(max_length=100)
    quantity = models.IntegerField()
    image = models.ImageField(upload_to='orders_images')
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.values('name').annotate(quantity=Count('name'))
        return queryset


   
class Order_Page(models.Model):
    order_number = models.TextField()
    order_date = models.DateField()
    order_quant = models.IntegerField()
    order_summ = models.IntegerField()
    order_payment = models.TextField()
    order_addr = models.TextField()
    order_itemid = models.ForeignKey(Product, on_delete=models.CASCADE)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)