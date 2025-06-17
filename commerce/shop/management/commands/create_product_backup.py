import json
import os
from django.core.management.base import BaseCommand
from shop.models import Product
from shop.signals import update_product_backup

class Command(BaseCommand):
    help = 'Creates a JSON backup of all products'

    def handle(self, *args, **options):
        update_product_backup(Product)
        self.stdout.write(self.style.SUCCESS('✅ Successfully created product backup'))
