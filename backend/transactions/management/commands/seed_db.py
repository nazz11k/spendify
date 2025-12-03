from django.core.management.base import BaseCommand
from transactions.models import Transaction, Category
from users.models import CustomUser
from django.utils.dateparse import parse_date


class Command(BaseCommand):
    help = 'Наповнює базу даних тестовими витратами за 2 місяці'

    def handle(self, *args, **kwargs):
        user_email = "user2@gmail.com"

        try:
            user = CustomUser.objects.get(email=user_email)
            self.stdout.write(self.style.SUCCESS(f"Користувача знайдено: {user.email}"))
        except CustomUser.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Користувача з email {user_email} не знайдено! Створіть його спочатку."))
            return

        # 2. Створюємо категорії
        categories_needed = ["Housing", "Groceries", "Restaurants", "Transport", "Entertainment", "Electronics",
                             "Health"]
        for cat_name in categories_needed:
            Category.objects.get_or_create(name=cat_name, owner=None, defaults={"type": "EXPENSE"})

        self.stdout.write("Категорії перевірено.")

        # 3. Дані
        mock_data = [
            # --- OCTOBER 2025 ---
            {"date": "2025-10-01", "category": "Housing", "amount": 12000.00,
             "description": "Apartment Rent (October)"},
            {"date": "2025-10-10", "category": "Housing", "amount": 1850.00, "description": "Utilities"},
            {"date": "2025-10-01", "category": "Entertainment", "amount": 350.00, "description": "Internet Provider"},
            {"date": "2025-10-05", "category": "Groceries", "amount": 2450.00,
             "description": "Silpo: Weekly groceries"},
            {"date": "2025-10-07", "category": "Groceries", "amount": 240.00, "description": "ATB: Bread, milk"},
            {"date": "2025-10-12", "category": "Groceries", "amount": 1890.00, "description": "Novus: Groceries"},
            {"date": "2025-10-15", "category": "Groceries", "amount": 320.00, "description": "Fora: Fruits"},
            {"date": "2025-10-20", "category": "Groceries", "amount": 2100.00, "description": "Metro: Big restock"},
            {"date": "2025-10-26", "category": "Groceries", "amount": 1500.00, "description": "Silpo: Groceries"},
            {"date": "2025-10-02", "category": "Restaurants", "amount": 85.00, "description": "Aroma Kava: Latte"},
            {"date": "2025-10-03", "category": "Restaurants", "amount": 450.00, "description": "Puzata Hata: Lunch"},
            {"date": "2025-10-04", "category": "Restaurants", "amount": 850.00,
             "description": "Domino's: Pizza with friends"},
            {"date": "2025-10-06", "category": "Restaurants", "amount": 75.00, "description": "Morning coffee"},
            {"date": "2025-10-08", "category": "Restaurants", "amount": 320.00, "description": "KFC: Lunch"},
            {"date": "2025-10-09", "category": "Restaurants", "amount": 80.00, "description": "Espresso"},
            {"date": "2025-10-13", "category": "Restaurants", "amount": 90.00, "description": "Coffee"},
            {"date": "2025-10-14", "category": "Restaurants", "amount": 550.00, "description": "Musafir: Dinner"},
            {"date": "2025-10-18", "category": "Restaurants", "amount": 120.00, "description": "Coffee and cake"},
            {"date": "2025-10-22", "category": "Restaurants", "amount": 400.00, "description": "McDonalds"},
            {"date": "2025-10-25", "category": "Restaurants", "amount": 1200.00,
             "description": "Local Bar: Friday night"},
            {"date": "2025-10-03", "category": "Transport", "amount": 230.00, "description": "Uber to work"},
            {"date": "2025-10-05", "category": "Transport", "amount": 1200.00, "description": "OKKO: Gasoline"},
            {"date": "2025-10-10", "category": "Transport", "amount": 180.00, "description": "Bolt: Ride home"},
            {"date": "2025-10-15", "category": "Transport", "amount": 250.00, "description": "Uklon: Rainy day ride"},
            {"date": "2025-10-20", "category": "Transport", "amount": 1100.00, "description": "WOG: Fuel"},
            {"date": "2025-10-28", "category": "Transport", "amount": 300.00, "description": "Uber: Night ride"},
            {"date": "2025-10-11", "category": "Entertainment", "amount": 400.00,
             "description": "Cinema tickets (Multiplex)"},
            {"date": "2025-10-15", "category": "Entertainment", "amount": 150.00, "description": "Spotify Premium"},
            {"date": "2025-10-20", "category": "Entertainment", "amount": 360.00,
             "description": "Netflix Subscription"},

            # --- NOVEMBER 2025 ---
            {"date": "2025-11-01", "category": "Housing", "amount": 12000.00,
             "description": "Apartment Rent (November)"},
            {"date": "2025-11-10", "category": "Housing", "amount": 2800.00, "description": "Utilities (with heating)"},
            {"date": "2025-11-01", "category": "Entertainment", "amount": 350.00, "description": "Internet Provider"},
            {"date": "2025-11-02", "category": "Groceries", "amount": 3200.00, "description": "Metro: Weekly restock"},
            {"date": "2025-11-08", "category": "Groceries", "amount": 2800.00,
             "description": "Silpo: Meat and vegetables"},
            {"date": "2025-11-15", "category": "Groceries", "amount": 1500.00, "description": "Novus"},
            {"date": "2025-11-22", "category": "Groceries", "amount": 2100.00, "description": "Auchan"},
            {"date": "2025-11-29", "category": "Groceries", "amount": 800.00, "description": "Fora: Small items"},
            {"date": "2025-11-05", "category": "Restaurants", "amount": 90.00, "description": "Coffee"},
            {"date": "2025-11-12", "category": "Restaurants", "amount": 120.00, "description": "Coffee with colleague"},
            {"date": "2025-11-18", "category": "Restaurants", "amount": 600.00, "description": "Sushi for dinner"},
            {"date": "2025-11-25", "category": "Restaurants", "amount": 400.00, "description": "McDonalds"},
            {"date": "2025-11-01", "category": "Transport", "amount": 350.00, "description": "Subway pass"},
            {"date": "2025-11-05", "category": "Transport", "amount": 1200.00, "description": "OKKO: Gasoline"},
            {"date": "2025-11-20", "category": "Transport", "amount": 1100.00, "description": "WOG: Fuel"},
            {"date": "2025-11-28", "category": "Electronics", "amount": 8500.00,
             "description": "Rozetka: New Headphones (Black Friday)"},
            {"date": "2025-11-10", "category": "Health", "amount": 1400.00, "description": "Pharmacy: Cold medicine"},
            {"date": "2025-11-12", "category": "Health", "amount": 600.00, "description": "Dila: Blood tests"},
            {"date": "2025-11-15", "category": "Entertainment", "amount": 150.00, "description": "Spotify Premium"},
            {"date": "2025-11-20", "category": "Entertainment", "amount": 360.00,
             "description": "Netflix Subscription"},
        ]

        # 4. Імпорт
        self.stdout.write("Починаю імпорт...")
        count = 0
        for item in mock_data:
            category, _ = Category.objects.get_or_create(
                name=item["category"],
                owner=None,
                defaults={"type": "EXPENSE"}
            )

            Transaction.objects.create(
                owner=user,
                category=category,
                amount=item["amount"],
                date=parse_date(item["date"]),
                description=item["description"]
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Успішно імпортовано {count} транзакцій!"))