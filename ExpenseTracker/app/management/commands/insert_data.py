from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Category, Expense
from random import choice, uniform
from datetime import timedelta, date
from decimal import Decimal

class Command(BaseCommand):
    help = 'Seed the database with sample categories and expenses'

    def handle(self, *args, **kwargs):
        # Sample categories
        categories = ['Food', 'Travel', 'Entertainment', 'Groceries', 'Health', 'Utilities']
        
        # Create categories
        for name in categories:
            obj, created = Category.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))

        # Get or create a test user
        user, _ = User.objects.get_or_create(username='testuser', defaults={'email': 'test@example.com'})
        user.set_password('admin')
        user.save()

        # Create sample expenses
        for _ in range(20):
            category = choice(Category.objects.all())
            amount = round(uniform(10.0, 200.0), 2)
            description = f"Sample expense in {category.name}"
            random_date = date.today() - timedelta(days=choice(range(90)))

            Expense.objects.create(
                user=user,
                category=category,
                amount=Decimal(amount),
                description=description,
                date=random_date
            )

        self.stdout.write(self.style.SUCCESS('✅ Seeded sample expenses successfully!'))
