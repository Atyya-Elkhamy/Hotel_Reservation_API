from django.contrib import admin
from .models import *
admin.site.register(Payment)
admin.site.register(PaymentMethod)
admin.site.register(PaymentSettings)
# Register your models here.
