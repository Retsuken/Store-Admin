from django.contrib import admin
from .models import User, Product, Product_Add, City, Name, District, Team, Payment, Client, Orders, Order_Page, AccessPage, Cart
# Register your models here.
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Product_Add)
admin.site.register(City)
admin.site.register(Name)
admin.site.register(District)
admin.site.register(Team)
admin.site.register(Payment)
admin.site.register(Client)
admin.site.register(Orders)
admin.site.register(Order_Page)
admin.site.register(AccessPage)
admin.site.register(Cart)