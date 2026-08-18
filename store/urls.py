from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    # Homepage
    path('', views.home, name='home'),

    # Product detail
    path('producto/<int:pk>/', views.product_detail, name='product_detail'),

    # Categories
    path('categorias/', views.categories_view, name='categories'),
    path('categoria/<int:pk>/', views.category_detail, name='category_detail'),

    # Search
    path('buscar/', views.search_view, name='search'),

    # Wishlist
    path('lista-deseos/', views.wishlist_view, name='wishlist'),
    path('lista-deseos/toggle/<int:pk>/', views.wishlist_toggle, name='wishlist_toggle'),

    # Contact
    path('contacto/', views.contact_view, name='contact'),

    # Authentication
    path('registro/', views.register_view, name='register'),
    path('iniciar-sesion/', views.login_view, name='login'),
    path('cerrar-sesion/', views.logout_view, name='logout'),
]
