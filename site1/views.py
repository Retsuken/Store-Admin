from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from .models import User, Product, Product_Add, City, Name, District, Team, Payment, Client, Orders, Order_Page, AccessPage, Cart, CartItem
from .forms import ProductAddForm, ProductRedactForm
from django.views.generic import TemplateView, ListView, DetailView, FormView, CreateView, UpdateView
from django.urls import reverse_lazy
import uuid
from urllib.parse import unquote
from .filters import ProductFilter
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from os import path as path_variable
from django.contrib.auth import login
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.utils import timezone
import requests
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id=product_id)

        # Получаем корзину пользователя или корзину из сессии
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id

        # Проверяем, есть ли товар в корзине
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            # Если товар уже есть, увеличиваем количество
            cart_item.quantity += 1
            cart_item.save()
        except CartItem.DoesNotExist:
            # Если товара нет, создаем новую запись
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=1)

        # Обновляем общую сумму и количество товаров в корзине
        cart.update_total()

        return redirect('home_page')

    return redirect('home_page')

def remove_from_cart(request, cart_item_id):
    cart_item = CartItem.objects.get(pk=cart_item_id)
    cart = cart_item.cart
    cart_item.delete()
    cart.update_total()  # Обновите общую сумму в корзине
    return redirect('home_page')

def home_page(request):
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(city__icontains=query)
        )
        selected_city = query
    else:
        products = Product.objects.all()
        selected_city = None

    if 'user_id' in request.session:
        user = User.objects.get(pk=request.session['user_id'])
    else:
        user = None
    viewed_products = request.session.get('viewed_products', [])

    # Получаем корзину пользователя или корзину из сессии
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id

    cart.total_price = 0  # Инициализируем общую сумму
    for cart_item in cart.cartitem_set.all():
        cart_item.total_price = cart_item.quantity * cart_item.product.cost
        cart_item.save()
        cart.total_price += cart_item.total_price  # Добавляем сумму товара к общей сумме
    cart.save() 
    total_products = products.count()
    context = {
        'products': products,
        'user': user,
        'selected_city': selected_city,
        'viewed_products': viewed_products,
        'cart': cart,
        'total_products': total_products,
    }
    return render(request, 'home-page-search.html', context)

def cards_product(request, product_id):
    if 'user_id' in request.session:
        user = User.objects.get(pk=request.session['user_id'])
    product = get_object_or_404(Product, id=product_id)
    viewed_products = request.session.get('viewed_products', [])

    product_data = {
        'name': product.name,
        'image': product.image.url,
        'city': product.city,
        'district': product.district,
        'cost': product.cost,
        
    }
    if product_data not in viewed_products:
       viewed_products.append(product_data)
       request.session['viewed_products'] = viewed_products[-10:]


    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id

    cart.total_price = 0  # Инициализируем общую сумму
    for cart_item in cart.cartitem_set.all():
        cart_item.total_price = cart_item.quantity * cart_item.product.cost
        cart_item.save()
        cart.total_price += cart_item.total_price  # Добавляем сумму товара к общей сумме
    cart.save() 

    context = {
        'product': product,
        'user': user,
        'viewed_products': viewed_products,
        'cart': cart,
    }
    return render(request, 'cards-page.html', context)


def pay_order(request):
    if 'user_id' in request.session:
        user = User.objects.get(pk=request.session['user_id'])
        
    # Получаем данные о последнем заказе пользователя
    order = Orders.objects.filter(name=user).order_by('-date').first()
    



    if order:
        total_price = order.cost * order.quantity

    response = requests.get(
        'https://api.paymentchecker.net/Payment/GetCard',
        headers={'X-Token': 'iOVM2qAJmYeKDOEUA0Q0RhF4mOxQw1Pjv9QCvV0nLSlbzFcyf2'},
        params={'amount': int(total_price), 'currency': 0}
    )

    card_data = response.json()
    context = {
        'user': user,
        'order': order,
        'total_price': total_price,
        'card_data': card_data
        }
    return render(request, 'pay-order.html', context)



def order_polz(request):
    if 'user_id' in request.session:
        user = User.objects.get(pk=request.session['user_id'])
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product_name = request.POST.get('product_name')
        product_image = request.POST.get('product_image')
        product_city = request.POST.get('product_city')
        product_district = request.POST.get('product_district')
        product_cost = request.POST.get('product_cost')
        quantity = int(request.POST.get('quantity', 1))
        # Создайте экземпляр товара
        product = Product(
            id=product_id,
            name=product_name,
            image=product_image,
            city=product_city,
            district=product_district,
            cost=product_cost,
        )
        total_price = quantity * product_cost        
        payments = Payment.objects.all()

        order = Orders.objects.create(
                name_tovar=product_name,
                status='F',  # Установите статус "Создан"
                name=user,  # Используйте объект User 
                product_id=product_id, 
                date=timezone.now(),
                city=product_city,
                district=product_district,
                # Добавьте обработку payment_method и payment_card, если они есть в форме
                cost=product_cost,
                # employee = ... (Обработайте данные о сотруднике)
                quantity=quantity,
                image=product_image,
                # comment = ... (Обработайте комментарий)
            )
  
        context = {
            'payments': payments,
            'product': product, 
            'user': user,
            'quantity': quantity,  # Передаем количество в контекст
            'total_price': total_price, 
            'order_number': order.pk,
        }
        return render(request, 'order.html', context)
    else:
        payments = Payment.objects.all()
        return render(request, 'order.html', {'payments': payments, 'user': user})



def profile_polz(request, user_id):
    if 'user_id' in request.session:
        user = User.objects.get(pk=request.session['user_id'])
    return render(request, 'privat-office-personal-data3.html', {'user': user})


def profile_polz2(request, user_id):
    if 'user_id' in request.session:
        user = User.objects.get(pk=request.session['user_id'])
    return render(request, 'privat-office-personal-data2.html', {'user': user})

def profile_balans2(request, user_id):
    if 'user_id' in request.session:
        user = User.objects.get(pk=request.session['user_id'])
    return render(request, 'privat-office-balance3.html', {'user': user})


def profile_balans3(request, user_id):
    if 'user_id' in request.session:
        user = User.objects.get(pk=request.session['user_id'])
    return render(request, 'privat-office-balance.html', {'user': user})

def profile_balans4(request, user_id):
    if 'user_id' in request.session:
        user = User.objects.get(pk=request.session['user_id'])
    return render(request, 'privat-office-balance2.html', {'user': user})

def profile_balans(request, user_id):
    if 'user_id' in request.session:
        user = User.objects.get(pk=request.session['user_id'])
    return render(request, 'privat-office-balance4.html', {'user': user})


def home_page_plit(request):
    if 'user_id' in request.session:
        user = User.objects.get(pk=request.session['user_id'])
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(city__icontains=query)
        )
        selected_city = query
    else:
        products = Product.objects.all()
        selected_city = None
    total_products = products.count()
    cart_id = request.session.get('cart_id')
    if cart_id:
        cart = Cart.objects.get(id=cart_id)
    else:
        cart = Cart.objects.create()
        request.session['cart_id'] = cart.id

    cart.total_price = 0  # Инициализируем общую сумму
    for cart_item in cart.cartitem_set.all():
        cart_item.total_price = cart_item.quantity * cart_item.product.cost
        cart_item.save()
        cart.total_price += cart_item.total_price  # Добавляем сумму товара к общей сумме
    cart.save() 
    context = {
        'products': products,
        'total_products': total_products,
        'selected_city': selected_city,
        'user': user,
        'cart': cart
    }
    return render(request, 'catalog3.html', context)


@login_required
def home(request):
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
        access_pages = team.access_pages.all()
        return render(request, 'statictick.html', {'team': team, 'access_pages': access_pages})
    else:
        return redirect('login')

def block_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.status = 'Не активный'
    client.save()
    return redirect('client_profile', client_id=client_id)

def unblock_client(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    client.status = 'Активный'
    client.save()
    return redirect('client_profile', client_id=client_id)


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['login']
            password = form.cleaned_data['password']

            # Авторизуемся один раз
            user_or_team = authenticate(request, username=username, password=password)

            if user_or_team:
                if isinstance(user_or_team, User):  # Проверяем, что это User
                    request.session['user_id'] = user_or_team.id
                    return redirect('home_page')
                elif isinstance(user_or_team, Team):  # Проверяем, что это Team
                    request.session['team_id'] = user_or_team.id
                    return redirect('home')

            error_message = 'Неверный логин или пароль'
        else:
            error_message = 'Неверный логин или пароль'
    else:
        form = LoginForm()
        error_message = None

    return render(request, 'login.html', {'form': form, 'error_message': error_message})

class UserRedactView(UpdateView):
    model = Product
    form_class = ProductRedactForm
    template_name = 'redact-address.html'
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = City.objects.all()
        return context

    def get_success_url(self):
        return reverse_lazy('redact', args=(self.kwargs['pk'],))




def product_detail(request, product_id):
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    products = Product.objects.all()
    product = get_object_or_404(Product, pk=product_id)
    return render(request, 'product-page.html', {'product': product, 'products': products, 'product_id': product_id, 'team': team})


def redact_address(request):
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    return render(request, 'redact-address.html', {'team': team})



def profile(request, team_id):
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    return render(request, 'lk-privat-office.html', {'team': team})

def profile_sotrudnik(request, team_id):
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    return render(request, 'lk.html', {'team': team})



def index(request):
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    products = Product.objects.all()
    status = request.GET.getlist('status')  # Получаем список всех выбранных статусов
    name = request.GET.get('name')  # Получаем значение фильтра по названию товара
    city = request.GET.getlist('city')  # Получаем список всех выбранных городов
    payment_method = request.GET.getlist('payment_method')
    employee = request.GET.getlist('employee')
    filtered_products = products  # Исходно отображаем все товар
    citys = City.objects.all()
    show_pagination = False  
    if status:
        filtered_products = products.filter(status__in=status)  # Фильтруем товары по выбранным статусам

    if city:
        filtered_products = filtered_products.filter(city__in=city)  # Фильтруем товары по выбранным городам

    
    if employee:
        employee = filtered_products.filter(employee__in=employee)  # Фильтруем товары по названию

    if payment_method:
        filtered_products = filtered_products.filter(payment_method__in=payment_method)  # Фильтруем товары по названию


    if name:
        filtered_products = filtered_products.filter(name__icontains=name)  # Фильтруем товары по названию


    if filtered_products.count() > 30:
        show_pagination = True

    paginator = Paginator(filtered_products, 30)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, 'index.html', {'products': products, 'filtered_products': filtered_products, 'team': team, 'citys': citys, 'show_pagination': show_pagination})

def product_availability(request):
    district = District.objects.all()
    city = City.objects.all()
    product = Product.objects.first()
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    products = Product.objects.all()
    city_id = request.session.get('city_id')
    selected_city = request.session.get('city_id')
    if selected_city:
        city = City.objects.get(id=selected_city)
        products = Product.objects.filter(city=city)
    else:
        products = Product.objects.all()
    if city_id:
           city = City.objects.get(id=city_id)
    return render(request, 'product-availability.html', {'products': products, 'team': team, 'product': product, 'city': city, 'district': district, 'selected_city':selected_city})


def delete_product(request, product_id):
    if request.method == 'POST':
        product = Product.objects.get(id=product_id)
        product.delete()
    return redirect('index')


def add_product(request):
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    cities = City.objects.all()
    name = Name.objects.all()
    district = District.objects.all()
    if request.method == 'POST':
        form = ProductAddForm(request.POST, request.FILES)
        if form.is_valid():
            product_add = form.save(commit=False)
            product = Product(
                status='Y',
                name=form.cleaned_data['product_name'],  # или можно использовать product_add.product_name
                product_id=uuid.uuid4().hex,
                date='2022-01-01',  # указать нужное значение
                city=form.cleaned_data['product_town'],  # или можно использовать product_add.product_town
                district=form.cleaned_data['product_distr'],  # или можно использовать product_add.product_distr
                payment_method='Наличные',  # указать нужное значение
                cost=form.cleaned_data['product_price'],  # или можно использовать product_add.product_price
                employee=form.cleaned_data['product_employee'],
                image=form.cleaned_data['image'],
                product_descr=form.cleaned_data['product_descr'],
                product_comm=form.cleaned_data['product_comm'],
                product_addr=form.cleaned_data['product_addr'],
            )
            product.save()
            product_add.save()
            return redirect('index')
    else:
        form = ProductAddForm()
    return render(request, 'product-base-page.html', {'form': form, 'team': team, 'cities': cities, 'name': name, 'district': district})


def order_page(request, order_id):
    teams = get_object_or_404(Orders, pk=order_id)
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    return render(request, 'order-page.html', {'teams': teams, 'team': team})


def new_order(request, order_id):
    teams = get_object_or_404(Orders, pk=order_id)
    return render(request, 'new-order-for-staff4.html', {'teams': teams})


def team(request):
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    client = Team.objects.all()
    login = request.GET.get('login')
    role = request.GET.getlist('role')
    filtered_team = client
    if login:
        filtered_team = filtered_team.filter(login__icontains=login)

    if role:
        filtered_team = filtered_team.filter(role__in=role)


    return render(request, 'team.html', {'client': client, 'team': team, 'filtered_team': filtered_team })



def team_workers(request, client_id):
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    client = Team.objects.all()
    teams = get_object_or_404(Team, pk=client_id)
    access_pages = AccessPage.objects.all()
    return render(request, 'team-workers-profile.html', {'teams': teams, 'client_id': client_id, 'client': client, 'team': team, 'access_pages': access_pages})


def save_access(request, client_id):
    client = get_object_or_404(Team, pk=client_id)

    if request.method == 'POST':
        selected_pages = request.POST.getlist('access_pages')
        client.access_pages.set(selected_pages)
        client.save()
        return redirect('team')

    access_pages = AccessPage.objects.all()
    return render(request, 'team-workers.html', {'access_pages': access_pages, 'client_id': client_id})





def team_workers2(request, client_id):
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    client = Team.objects.all()
    teams = get_object_or_404(Team, pk=client_id)
    return render(request, 'team-workers-profile2.html', {'client': client, 'team': team, 'teams': teams})

def payment(request):
    payments = Payment.objects.all()
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    return render(request, 'payments-system.html', {'payments': payments, 'team': team})


def team_form(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        role = request.POST.get('role')
        access_pages_selected = request.POST.getlist('access_pages')

        new_employee = Team()
        new_employee.login = login
        new_employee.role = role
        new_employee.save()  # Сохранить сотрудника, чтобы у него был назначен уникальный идентификатор
        
        for access_page_id in access_pages_selected:
            access_page = AccessPage.objects.get(id=access_page_id)
            new_employee.access_pages.add(access_page)  # Добавить связанные access_pages

        return redirect('team')  # Замените 'success_page' на URL страницы, которую вы хотите показать после успешного добавления сотрудника
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    teams = Team.objects.all()
    access_pages = AccessPage.objects.all()
    return render(request, 'form.html', {'team': team, 'teams': teams, 'role_choices': Team.ROLE_CHOICES, 'access_pages': access_pages})

def clients(request):
    client = Client.objects.all()
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    login = request.GET.get('login')
    filtered_client = client
    if login:
        filtered_client = filtered_client.filter(login__icontains=login) 
    order = Orders.objects.all()
    problem_orders_count = Orders.objects.filter(status='H').count()


    page_size = 30
    paginator = Paginator(filtered_client, page_size)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'clients.html', {'client': client, 'team': team, 'filtered_client': filtered_client, 'order': order, 'problem_orders_count': problem_orders_count, 'page_obj': page_obj,})

def clients_profile(request, client_id):
    client = get_object_or_404(Client, pk=client_id)
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    return render(request, 'client-profile.html', {'client': client, 'client_id': client_id, 'team': team})


def client_redact(request, client_id):
    client = get_object_or_404(Client, pk=client_id)

    if request.method == 'POST':
        # Получаем данные из формы
        login = request.POST.get('login')
        telegram = request.POST.get('telegram')
        email = request.POST.get('email')

        # Обновляем данные клиента
        client.login = login
        client.telegram = telegram
        client.Email = email
        client.save()

        # Перенаправляем пользователя на страницу профиля клиента
        return redirect('client_profile', client_id=client.id)

    # Рендерим форму редактирования на странице client-profile1.html
    return render(request, 'client-profile1.html', {'client': client})

def orders(request):
    if 'team_id' in request.session:  # Проверка team_id
        team = Team.objects.get(id=request.session['team_id'])
    order = Orders.objects.all()
    client = Client.objects.all()
    status = request.GET.getlist('status')  # Получаем список всех выбранных статусов
    name = request.GET.get('name')  # Получаем значение фильтра по названию товара
    city = request.GET.getlist('city')  # Получаем список всех выбранных городов
    payment_method = request.GET.getlist('payment_method')
    employee = request.GET.getlist('employee')
    filtered_products = order
    citys = City.objects.all()
    show_pagination = False


    if status:
        filtered_products = order.filter(status__in=status)  # Фильтруем товары по выбранным статусам

    if city:
        filtered_products = filtered_products.filter(city__in=city)  # Фильтруем товары по выбранным городам

    
    if employee:
        employee = filtered_products.filter(employee__in=employee)  # Фильтруем товары по названию

    if payment_method:
        filtered_products = filtered_products.filter(payment_method__in=payment_method)  # Фильтруем товары по названию


    if name:
        filtered_products = filtered_products.filter(name__icontains=name)  # Фильтруем товары по названию


    if filtered_products.count() > 30:
        show_pagination = True

    paginator = Paginator(filtered_products, 30)
    page = request.GET.get('page')

    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)


    return render(request, 'orders.html', {'team': team, 'order': order, 'filtered_products': filtered_products, 'citys': citys, 'show_pagination': show_pagination, 'client': client })



def get_product_info(request, product_name):
    product = get_object_or_404(Product, name=product_name)
    # Здесь вы можете подготовить данные о товаре и вернуть их в JSON-формате
    product_info = {
        'name': product.name,
        'product_id': product.product_id,
        'date': product.date,
        'city': product.city,
        'district': product.district,
        'payment_method': product.payment_method,
        'price': product.cost,
        'employee': product.employee
    }
    return JsonResponse(product_info)

def get_product_info1(request, product_city):
    product = get_object_or_404(Product, city=product_city)
    # Здесь вы можете подготовить данные о товаре и вернуть их в JSON-формате
    product_info = {
        'name': product.name,
        'product_id': product.product_id,
        'date': product.date,
        'city': product.city,
        'district': product.district,
        'payment_method': product.payment_method,
        'price': product.cost,
        'employee': product.employee
    }
    return JsonResponse(product_info)

def get_product_info2(request, product_payment_method):
    product = get_object_or_404(Product, payment_method=product_payment_method)
    # Здесь вы можете подготовить данные о товаре и вернуть их в JSON-формате
    product_info = {
        'name': product.name,
        'product_id': product.product_id,
        'date': product.date,
        'city': product.city,
        'district': product.district,
        'payment_method': product.payment_method,
        'price': product.cost,
        'employee': product.employee
    }
    return JsonResponse(product_info)
def get_product_info3(request, product_employee):
    product = get_object_or_404(Product, employee=product_employee)
    # Здесь вы можете подготовить данные о товаре и вернуть их в JSON-формате
    product_info = {
        'name': product.name,
        'product_id': product.product_id,
        'date': product.date,
        'city': product.city,
        'district': product.district,
        'payment_method': product.payment_method,
        'price': product.cost,
        'employee': product.employee
    }
    return JsonResponse(product_info)

def update_city(request):
       if request.method == 'POST':
           city_id = request.POST.get('city')
           city = City.objects.get(id=city_id)
           # сохраняем выбранный город в сессии пользователя
           request.session['city_id'] = city_id
           return redirect('product_availability')

       cities = City.objects.all()
       return render(request, 'choose_city.html', {'cities': cities})



def cancel_sale(request, profile_id):
    team = Team.objects.get(id=request.session['team_id'])
    team.skidka = 0
    team.save()
    return redirect('profile')

from itertools import groupby

# Get the products queryset or list
products = Product.objects.all()  # replace with your actual queryset or list

# Perform grouping by name
