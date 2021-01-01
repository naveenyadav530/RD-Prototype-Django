from django.contrib import admin
from .models import NewLedger, SubLedger, MakeReceipt

# Register your models here.
admin.site.register(NewLedger)
admin.site.register(SubLedger)
admin.site.register(MakeReceipt)