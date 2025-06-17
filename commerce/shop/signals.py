import json
import os
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.db import transaction
from .models import Product, ProductImage

# Define the backup file path at module level
BACKUP_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'backups'
)
BACKUP_FILE = os.path.join(BACKUP_DIR, 'products_backup.json')

def create_backup():
    """Create a backup of all products with their related data"""
    try:
        # Ensure the backup directory exists
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Use select_related for foreign keys and prefetch_related for many-to-many
        products = Product.objects.all().select_related(
            'seller', 'category'
        ).prefetch_related(
            'color_options', 'images'
        )

        backup_data = []
        for product in products:
            # Get all image paths
            images = []
            for image in product.images.all():
                images.append({
                    'image': image.image.name,
                    'alt_text': image.alt_text or ''
                })

            backup_data.append({
                'model': 'shop.product',  # Make sure this matches your app name
                'pk': product.pk,
                'fields': {
                    'seller': product.seller.id,
                    'name': product.name,
                    'description': product.description,
                    'price': str(product.price),
                    'stock': product.stock,
                    'category': product.category.id if product.category else None,
                    'color_options': [c.id for c in product.color_options.all()],
                    'size': product.size,
                    'sku': product.sku,
                    'source': product.source,
                    'aliexpress_url': product.aliexpress_url,
                    'supplier_name': product.supplier_name,
                    'supplier_contact': product.supplier_contact,
                    'supplier_price': str(product.supplier_price) if product.supplier_price else None,
                    'delivery_fee': str(product.delivery_fee) if product.delivery_fee else None,
                    'created_at': product.created_at.isoformat(),
                    'updated_at': product.updated_at.isoformat(),
                    'images': images
                }
            })

        with open(BACKUP_FILE, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

    except Exception as e:
        # Log the error but don't crash the application
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Failed to create product backup: {str(e)}")

@receiver(post_save, sender=Product)
def on_product_save(sender, instance, **kwargs):
    transaction.on_commit(create_backup)

@receiver(post_delete, sender=Product)
def on_product_delete(sender, instance, **kwargs):
    transaction.on_commit(create_backup)

@receiver(m2m_changed, sender=Product.color_options.through)
def on_color_change(sender, instance, action, **kwargs):
    if action in ("post_add", "post_remove", "post_clear"):
        transaction.on_commit(create_backup)

@receiver(post_save, sender=ProductImage)
def on_image_save(sender, instance, **kwargs):
    transaction.on_commit(create_backup)

@receiver(post_delete, sender=ProductImage)
def on_image_delete(sender, instance, **kwargs):
    transaction.on_commit(create_backup)