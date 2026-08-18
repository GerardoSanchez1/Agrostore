from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """Custom manager for User model that uses email as the unique identifier."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model that uses email as the unique identifier instead of username."""
    username = None
    email = models.EmailField('correo electrónico', unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return self.email


class Brand(models.Model):
    """Product brand with logo."""
    name = models.CharField('nombre', max_length=200)
    logo = models.ImageField('logotipo', upload_to='brands/', blank=True)

    class Meta:
        verbose_name = 'marca'
        verbose_name_plural = 'marcas'
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    """Product category."""
    name = models.CharField('nombre', max_length=200, unique=True)

    class Meta:
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['name']

    def __str__(self):
        return self.name


class Item(models.Model):
    """A product in the store."""
    name = models.CharField('nombre', max_length=300)
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='marca',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='categoría',
    )
    price = models.DecimalField('precio', max_digits=12, decimal_places=2)
    description = models.TextField('descripción', blank=True)
    details = models.TextField('detalles', blank=True)

    class Meta:
        verbose_name = 'producto'
        verbose_name_plural = 'productos'
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def first_image(self):
        """Return the first associated Picture or None."""
        return self.pictures.first()

    @property
    def formatted_price(self):
        """Return the price formatted in MXN."""
        return f"${self.price:,.2f} MXN"


class Picture(models.Model):
    """Product image."""
    photo = models.ImageField('foto', upload_to='products/')
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='pictures',
        verbose_name='producto',
    )

    class Meta:
        verbose_name = 'imagen'
        verbose_name_plural = 'imágenes'

    def __str__(self):
        return f"{self.item.name} - Imagen {self.pk}"


class Wishlist(models.Model):
    """User wishlist entry — one row per user-item pair."""
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        verbose_name='usuario',
    )
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='wishlisted_by',
        verbose_name='producto',
    )
    added_at = models.DateTimeField('agregado el', auto_now_add=True)

    class Meta:
        verbose_name = 'lista de deseos'
        verbose_name_plural = 'listas de deseos'
        unique_together = ('user', 'item')

    def __str__(self):
        return f"{self.user.email} → {self.item.name}"


class ContactRequest(models.Model):
    """Purchase request / contact form submission."""
    name = models.CharField('nombre', max_length=200)
    email = models.EmailField('correo electrónico')
    message = models.TextField('mensaje')
    products = models.ManyToManyField(
        Item,
        blank=True,
        related_name='contact_requests',
        verbose_name='productos',
    )
    created_at = models.DateTimeField('fecha de envío', auto_now_add=True)

    class Meta:
        verbose_name = 'solicitud de contacto'
        verbose_name_plural = 'solicitudes de contacto'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.created_at:%Y-%m-%d %H:%M}"
