from django.urls import path
from .views import login_page, register_page, logout_view
from Library.views import home_view

urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_page, name='login'),
    path('signup/', register_page, name='signup'),
    path('logout/', logout_view, name='logout'),
]
