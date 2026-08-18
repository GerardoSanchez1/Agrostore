from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST

from .models import Item, Category, Brand, Wishlist
from .forms import RegistrationForm, LoginForm, ContactForm, SearchForm


def home(request):
    """Homepage — display all products."""
    items = Item.objects.select_related('brand', 'category').prefetch_related('pictures').all()
    categories = Category.objects.all()
    brands = Brand.objects.all()

    # Get wishlist item IDs for authenticated users
    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('item_id', flat=True)
        )

    return render(request, 'store/home.html', {
        'items': items,
        'categories': categories,
        'brands': brands,
        'wishlist_ids': wishlist_ids,
        'page_title': 'Todos los Productos',
    })


def product_detail(request, pk):
    """Product detail page."""
    item = get_object_or_404(
        Item.objects.select_related('brand', 'category').prefetch_related('pictures'),
        pk=pk,
    )
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, item=item).exists()

    # Related products (same category, exclude current)
    related = Item.objects.filter(category=item.category).exclude(pk=item.pk).select_related('brand').prefetch_related('pictures')[:4]

    return render(request, 'store/product_detail.html', {
        'item': item,
        'in_wishlist': in_wishlist,
        'related': related,
        'page_title': item.name,
    })


def categories_view(request):
    """Display all categories with their products."""
    categories = Category.objects.prefetch_related(
        'items__brand', 'items__pictures'
    ).all()

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('item_id', flat=True)
        )

    return render(request, 'store/categories.html', {
        'categories': categories,
        'wishlist_ids': wishlist_ids,
        'page_title': 'Categorías',
    })


def category_detail(request, pk):
    """Display products for a single category."""
    category = get_object_or_404(Category, pk=pk)
    items = Item.objects.filter(category=category).select_related('brand').prefetch_related('pictures')

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('item_id', flat=True)
        )

    return render(request, 'store/category_detail.html', {
        'category': category,
        'items': items,
        'wishlist_ids': wishlist_ids,
        'page_title': category.name,
    })


def search_view(request):
    """Search products by name, brand, or category."""
    form = SearchForm(request.GET)
    items = Item.objects.none()
    query = ''

    if form.is_valid():
        query = form.cleaned_data.get('q', '').strip()
        if query:
            items = Item.objects.filter(
                Q(name__icontains=query) |
                Q(brand__name__icontains=query) |
                Q(category__name__icontains=query)
            ).select_related('brand', 'category').prefetch_related('pictures').distinct()

    wishlist_ids = set()
    if request.user.is_authenticated:
        wishlist_ids = set(
            Wishlist.objects.filter(user=request.user).values_list('item_id', flat=True)
        )

    return render(request, 'store/search_results.html', {
        'form': form,
        'items': items,
        'query': query,
        'wishlist_ids': wishlist_ids,
        'page_title': f'Buscar: {query}' if query else 'Buscar',
    })


@login_required
def wishlist_view(request):
    """Display the authenticated user's wishlist."""
    wishlist_entries = Wishlist.objects.filter(
        user=request.user
    ).select_related('item__brand', 'item__category').prefetch_related('item__pictures')

    items = [entry.item for entry in wishlist_entries]
    wishlist_ids = {entry.item_id for entry in wishlist_entries}

    return render(request, 'store/wishlist.html', {
        'items': items,
        'wishlist_ids': wishlist_ids,
        'page_title': 'Mi Lista de Deseos',
    })


@login_required
@require_POST
def wishlist_toggle(request, pk):
    """Add or remove a product from the user's wishlist (AJAX endpoint)."""
    item = get_object_or_404(Item, pk=pk)
    entry, created = Wishlist.objects.get_or_create(user=request.user, item=item)

    if not created:
        entry.delete()
        added = False
    else:
        added = True

    # Return JSON for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'added': added, 'item_id': pk})

    # Fallback: redirect back
    return redirect(request.META.get('HTTP_REFERER', '/'))


def contact_view(request):
    """Contact / purchase request form."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message_text = form.cleaned_data['message']
            products = form.cleaned_data.get('products', [])

            # Build email body
            product_list = '\n'.join(f'  - {p.name} ({p.formatted_price})' for p in products) if products else '  (Ninguno especificado)'
            email_body = (
                f"Nueva solicitud de contacto\n"
                f"{'=' * 40}\n\n"
                f"Nombre: {name}\n"
                f"Correo: {email}\n\n"
                f"Productos de interés:\n{product_list}\n\n"
                f"Mensaje:\n{message_text}\n"
            )

            send_mail(
                subject=f'[AgroStore] Nueva solicitud de {name}',
                message=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['gerardo-sanchez-1@hotmail.com'],
                fail_silently=False,
            )

            messages.success(request, '¡Tu mensaje ha sido enviado exitosamente! Nos pondremos en contacto contigo pronto.')
            return redirect('store:contact')
    else:
        form = ContactForm()

    return render(request, 'store/contact.html', {
        'form': form,
        'page_title': 'Contacto',
    })


def register_view(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Cuenta creada exitosamente! Bienvenido.')
            return redirect('store:home')
    else:
        form = RegistrationForm()

    return render(request, 'store/register.html', {
        'form': form,
        'page_title': 'Registro',
    })


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('store:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, '¡Bienvenido de vuelta!')
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'Correo electrónico o contraseña incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'store/login.html', {
        'form': form,
        'page_title': 'Iniciar Sesión',
    })


def logout_view(request):
    """User logout."""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('store:home')
