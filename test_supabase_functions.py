from supabase_client import *

print("=" * 60)
print("ТЕСТУВАННЯ МОДУЛЯ SUPABASE_CLIENT")
print("=" * 60)

# Тест 1: Реєстрація тестового користувача
print("\n1️⃣ Тест реєстрації...")
test_email = "dymyr@i.ua"
test_password = "123456"
test_name = "Тестовий Користувач"

result = register_user(test_email, test_password, test_name)
if result['success']:
    print(f"✅ Користувач зареєстрований! ID: {result['user_id']}")
    user_id = result['user_id']
else:
    print(f"❌ Помилка: {result['error']}")
    print("💡 Можливо, користувач вже існує. Спробуємо увійти...")
    result = login_user(test_email, test_password)
    if result['success']:
        user_id = result['user_id']
        print(f"✅ Вхід успішний! ID: {user_id}")
    else:
        print(f"❌ Не вдалося увійти: {result['error']}")
        exit()

# Тест 2: Збереження профілю
print("\n2️⃣ Тест збереження профілю...")
profile_data = {
    'name': 'Мій Магазин',
    'bio': 'Найкращі товари в Україні',
    'theme_choice': 'gradient',
    'theme_color': '#667eea',
    'font_choice': 'Inter',
    'dark_mode': False,
    'telegram_chat_id': '811492883'
}
if save_profile(user_id, profile_data):
    print("✅ Профіль збережено!")
else:
    print("❌ Помилка збереження профілю")

# Тест 3: Завантаження профілю
print("\n3️⃣ Тест завантаження профілю...")
loaded_profile = load_profile(user_id)
if loaded_profile:
    print(f"✅ Профіль завантажено: {loaded_profile['name']}")
else:
    print("❌ Профіль не знайдено")

# Тест 4: Збереження посилань
print("\n4️⃣ Тест збереження посилань...")
test_links = [
    {'title': 'Instagram', 'url': 'https://instagram.com/test', 'is_paid': False, 'price': 0},
    {'title': 'Telegram', 'url': 'https://t.me/test', 'is_paid': False, 'price': 0},
    {'title': 'Преміум контент', 'url': 'https://example.com/premium', 'is_paid': True, 'price': 100}
]
if save_links(user_id, test_links):
    print("✅ Посилання збережено!")
else:
    print("❌ Помилка збереження посилань")

# Тест 5: Завантаження посилань
print("\n5️⃣ Тест завантаження посилань...")
loaded_links = load_links(user_id)
if loaded_links:
    print(f"✅ Завантажено {len(loaded_links)} посилань:")
    for link in loaded_links:
        print(f"   - {link['title']}: {link['url']}")
else:
    print("❌ Посилання не знайдено")

# Тест 6: Збереження товарів
print("\n6️⃣ Тест збереження товарів...")
test_products = [
    {'title': 'Худі чорна', 'description': '100% бавовна', 'price': 500, 'image': ''},
    {'title': 'Шапка зелена', 'description': 'Тепла і стильна', 'price': 150, 'image': ''}
]
if save_products(user_id, test_products):
    print("✅ Товари збережено!")
else:
    print("❌ Помилка збереження товарів")

# Тест 7: Завантаження товарів
print("\n7️⃣ Тест завантаження товарів...")
loaded_products = load_products(user_id)
if loaded_products:
    print(f"✅ Завантажено {len(loaded_products)} товарів:")
    for prod in loaded_products:
        print(f"   - {prod['title']}: {prod['price']}₴")
else:
    print("❌ Товари не знайдено")

# Тест 8: Створення замовлення
print("\n8️⃣ Тест створення замовлення...")
order_data = {
    'customer_name': 'Олена Петренко',
    'customer_phone': '+380991234567',
    'delivery_type': 'nova_poshta',
    'delivery_city': 'Київ',
    'delivery_address': 'Відділення №5',
    'comment': 'Подзвоніть перед відправкою',
    'items_json': [
        {'title': 'Худі чорна', 'price': 500, 'quantity': 1},
        {'title': 'Шапка зелена', 'price': 150, 'quantity': 2}
    ],
    'total_amount': 800
}
order_id = create_order(user_id, order_data)
if order_id:
    print(f"✅ Замовлення створено! ID: {order_id}")
    print("💡 Перевірте Telegram — має прийти сповіщення!")
else:
    print("❌ Помилка створення замовлення")

print("\n" + "=" * 60)
print("🎉 ТЕСТУВАННЯ ЗАВЕРШЕНО!")
print("=" * 60)