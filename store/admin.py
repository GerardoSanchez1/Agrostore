from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Brand, Category, Item, Picture, Wishlist, ContactRequest


# ─── Custom User Admin ───────────────────────────────────────────────────────

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = ('email',)
    ordering = ('email',)

    # Override fieldsets since we removed username
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


# ─── Picture Inline ──────────────────────────────────────────────────────────

class PictureInline(admin.TabularInline):
    model = Picture
    extra = 1
    fields = ('photo',)


# ─── Brand Admin ──────────────────────────────────────────────────────────────

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'logo')
    search_fields = ('name',)


# ─── Category Admin ───────────────────────────────────────────────────────────

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


# ─── Item Admin ───────────────────────────────────────────────────────────────

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'category', 'price')
    list_filter = ('brand', 'category')
    search_fields = ('name', 'brand__name', 'category__name')
    inlines = [PictureInline]


# ─── Picture Admin ────────────────────────────────────────────────────────────

@admin.register(Picture)
class PictureAdmin(admin.ModelAdmin):
    list_display = ('id', 'item', 'photo')
    list_filter = ('item__brand', 'item__category')
    search_fields = ('item__name',)


# ─── Wishlist Admin ───────────────────────────────────────────────────────────

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'item', 'added_at')
    list_filter = ('user', 'added_at')
    search_fields = ('user__email', 'item__name')


# ─── Contact Request Admin ───────────────────────────────────────────────────

@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'message')
    filter_horizontal = ('products',)
    readonly_fields = ('created_at',)
