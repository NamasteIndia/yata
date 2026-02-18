from django.urls import re_path

from .views import main, travel

app_name = "api"
urlpatterns = [
    re_path(r"^$", main.index, name="index"),
    # travel (for bazaar foreign stocks)
    re_path(r"^v1/travel/export/$", travel.exportStocks, name="exportStocks"),
    re_path(r"^v1/travel/import/$", travel.importStocks, name="importStocks"),
]
