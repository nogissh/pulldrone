from django.contrib import admin

from .models import Fake
from .models import Natural

# Register your models here.
admin.site.register(Fake)
admin.site.register(Natural)
