import streamlit as st
import json
import base64
import os
import supabase_client as db
from datetime import datetime
from typing import List, Dict, Optional, Any  # <-- ДОДАНО Any
# ============================================================================
# КОНФІГУРАЦІЯ
# ============================================================================

PAGE_CONFIG = {
    "page_title": "SmartLink - Конструктор сайтів",
    "layout": "wide"
}

THEMES = {
    'gradient': {
        'name': '🌈 Gradient',
        'bg': lambda color: f'linear-gradient(135deg, {color} 0%, #764ba2 100%)',
        'container_bg': '#ffffff',
        'text': '#333333',
        'link_bg': lambda color: f'linear-gradient(135deg, {color} 0%, #764ba2 100%)',
        'link_text': '#ffffff',
        'border': 'none',
        'shadow': '0 20px 60px rgba(0,0,0,0.3)',
        'border_radius': '20px'
    },
    'minimal': {
        'name': '✨ Minimal',
        'bg': lambda color: '#ffffff',
        'container_bg': '#ffffff',
        'text': '#333333',
        'link_bg': lambda color: color,
        'link_text': '#ffffff',
        'border': '1px solid #e0e0e0',
        'shadow': 'none',
        'border_radius': '8px'
    },
    'dark': {
        'name': '🌙 Dark',
        'bg': lambda color: '#1a1a1a',
        'container_bg': '#2d2d2d',
        'text': '#ffffff',
        'link_bg': lambda color: color,
        'link_text': '#ffffff',
        'border': '1px solid #444444',
        'shadow': '0 10px 40px rgba(0,0,0,0.5)',
        'border_radius': '16px'
    },
    'glass': {
        'name': '💎 Glass',
        'bg': lambda color: f'linear-gradient(135deg, {color} 0%, #764ba2 100%)',
        'container_bg': 'rgba(255, 255, 255, 0.15)',
        'text': '#ffffff',
        'link_bg': lambda color: 'rgba(255, 255, 255, 0.2)',
        'link_text': '#ffffff',
        'border': '1px solid rgba(255, 255, 255, 0.3)',
        'shadow': '0 8px 32px rgba(0,0,0,0.2)',
        'border_radius': '24px',
        'backdrop_filter': 'blur(10px)'
    },
    'neumorphism': {
        'name': '🎨 Neumorphism',
        'bg': lambda color: '#e0e5ec',
        'container_bg': '#e0e5ec',
        'text': '#333333',
        'link_bg': lambda color: '#e0e5ec',
        'link_text': lambda color: color,
        'border': 'none',
        'shadow': '9px 9px 16px rgba(163, 177, 198, 0.6), -9px -9px 16px rgba(255, 255, 255, 0.5)',
        'border_radius': '20px'
    }
}

FONTS = ["Inter", "Roboto", "Montserrat", "Poppins", "Playfair Display", "Open Sans", "Lato", "Oswald"]

BIO_TEMPLATES = {
    'instagram+tiktok': "📸 Контент-кріейтор | Створюю трендовий контент | Instagram & TikTok",
    'instagram+youtube': "🎥 Відеоблогер | Ділюся цікавим контентом | YouTube & Instagram",
    'instagram+telegram': "💬 Активний блогер | Спілкування та контент | Пиши мені!",
    'tiktok+youtube': "🎬 Відеокріейтор | Короткі та довгі відео | Підписуйся!",
    'instagram+design': "🎨 Дизайнер | Візуальний стиліст | Портфоліо та замовлення",
    'github+linkedin': "💻 Розробник | Tech enthusiast | Відкритий до співпраці",
    'music+instagram': "🎵 Музикант | Нові треки та виступи | Слухай та підписуйся!",
    'instagram': "📸 Фотограф | Ловлю моменти | Замовлення відкриті",
    'tiktok': "🎭 TikTok кріейтор | Розваги та тренди | Підписуйся!",
    'youtube': "🎥 YouTube блогер | Цікаві відео щотижня | Підписуйся на канал!",
    'telegram': "💬 Telegram канал | Корисний контент | Приєднуйся!",
    'design': "🎨 Дизайнер | Створюю красу | Портфоліо нижче",
    'github': "💻 Розробник | Open source | Мої проєкти",
    'music': "🎵 Музикант | Слухай мої треки | Посилання нижче",
    'default': "✨ Ласкаво прошу! Тут зібрані всі мої контакти та посилання"
}

CONFIG_FILE = "last_config.json"

# ============================================================================
# ДОПОМІЖНІ ФУНКЦІЇ
# ============================================================================

def generate_icon_svg(name: str, color: str = "#667eea") -> str:
    letter = name[0].upper() if name else "M"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 192 192">
        <rect width="192" height="192" rx="40" fill="{color}"/>
        <text x="96" y="130" font-family="Arial, sans-serif" font-size="110" font-weight="bold" fill="white" text-anchor="middle">{letter}</text>
    </svg>"""

def svg_to_data_uri(svg: str) -> str:
    encoded = svg.replace('\n', '').replace('  ', '')
    return f"data:image/svg+xml;base64,{base64.b64encode(encoded.encode()).decode()}"

def image_to_data_uri(uploaded_file) -> Optional[str]:
    """Конвертує завантажений файл в data URI з правильною нормалізацією MIME-типу"""
    if uploaded_file is None:
        return None
    encoded = base64.b64encode(uploaded_file.getvalue()).decode()
    mime_type = uploaded_file.type.split('/')[1].lower()
    
    # Нормалізуємо MIME-тип
    if mime_type == 'jpg':
        mime_type = 'jpeg'
    elif mime_type == 'tif':
        mime_type = 'tiff'
    
    return f"data:image/{mime_type};base64,{encoded}"
def fix_image_mime_type(image_data: str) -> str:
    """Виправляє неправильні MIME-типи у data URI"""
    if not image_data or not image_data.startswith('data:image/'):
        return image_data
    
    # Виправляємо поширені помилки
    image_data = image_data.replace('data:image/jpg;', 'data:image/jpeg;')
    image_data = image_data.replace('data:image/tif;', 'data:image/tiff;')
    
    return image_data

def detect_platforms(links: List[Dict]) -> List[str]:
    platforms = []
    platform_keywords = {
        'instagram': ['instagram'], 'tiktok': ['tiktok'], 'youtube': ['youtube'],
        'telegram': ['telegram'], 'facebook': ['facebook'], 'twitter': ['twitter', 'x.com'],
        'linkedin': ['linkedin'], 'github': ['github'], 'design': ['behance', 'dribbble'],
        'music': ['spotify', 'soundcloud']
    }
    for link in links:
        url = link.get('url', '').lower()
        for platform, keywords in platform_keywords.items():
            if any(keyword in url for keyword in keywords) and platform not in platforms:
                platforms.append(platform)
    return platforms

def generate_bio_from_links(links: List[Dict]) -> str:
    if not links: return BIO_TEMPLATES['default']
    platforms = detect_platforms(links)
    if len(platforms) >= 2:
        for i in range(len(platforms)):
            for j in range(i+1, len(platforms)):
                combo = f"{platforms[i]}+{platforms[j]}"
                if combo in BIO_TEMPLATES: return BIO_TEMPLATES[combo]
    if len(platforms) == 1 and platforms[0] in BIO_TEMPLATES:
        return BIO_TEMPLATES[platforms[0]]
    return BIO_TEMPLATES['default']

def get_theme_styles(theme: str, color: str) -> Dict:
    theme_config = THEMES.get(theme, THEMES['gradient'])
    styles = {}
    for key, value in theme_config.items():
        if key == 'name': continue
        styles[key] = value(color) if callable(value) else value
    return styles

def get_user_plan_status(user_id: str) -> Dict[str, Any]:
    """Визначає статус користувача згідно з новими правилами."""
    try:
        profile = db.load_profile(user_id)
        if not profile:
            return {'name': 'Free 🥉', 'links': 3, 'products': 2, 'has_gif': False, 'gallery_limit': 1, 'is_pro': False}
        
        plan = profile.get('plan', 'free')
        trial_date_str = profile.get('trial_end_date')
        
        is_trial_active = False
        if trial_date_str:
            try:
                if isinstance(trial_date_str, str):
                    clean_date = trial_date_str.replace('Z', '+00:00')
                    trial_date = datetime.fromisoformat(clean_date)
                else:
                    trial_date = trial_date_str
                
                if trial_date.tzinfo is None:
                    now = datetime.now()
                else:
                    now = datetime.now(trial_date.tzinfo)
                    
                if trial_date > now:
                    is_trial_active = True
            except Exception:
                pass

        # 🥇 Unlimited
        if plan == 'unlimited':
            return {'name': 'Unlimited ', 'links': 9999, 'products': 9999, 'has_gif': True, 'gallery_limit': 9999, 'is_pro': True}
        
        # 🥈 Pro (включно з Trial)
        elif plan == 'pro' or is_trial_active:
            status_name = 'Pro (Trial 14 days) 🚀' if is_trial_active else 'Pro 🥈'
            return {'name': status_name, 'links': 20, 'products': 15, 'has_gif': True, 'gallery_limit': 15, 'is_pro': True}
        
        # 🥉 Free (Ваші нові правила)
        else:
            return {'name': 'Free ', 'links': 3, 'products': 2, 'has_gif': False, 'gallery_limit': 1, 'is_pro': False}
            
    except Exception as e:
        print(f"Помилка перевірки тарифу: {e}")
        return {'name': 'Free 🥉', 'links': 3, 'products': 2, 'has_gif': False, 'gallery_limit': 1, 'is_pro': False}

# ============================================================================
# ЕКСПОРТ / ІМПОРТ КОНФІГУРАЦІЇ
# ============================================================================

def save_config_to_supabase(user_id: str):
    """Зберігає ВСЮ конфігурацію користувача в Supabase."""
    try:
        # 1. Збираємо повну конфігурацію як JSON
        full_config_json = export_config()
        
        # 🔍 ДІАГНОСТИКА: Що ми зберігаємо?
        st.info("🔍 **ПЕРЕВІРКА ДАНИХ ПЕРЕД ЗБЕРЕЖЕННЯМ:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            gif_url = st.session_state.get('gif_url', '')
            st.write(f"**GIF:** {'✅ Є' if gif_url else ' Немає'}")
            if gif_url:
                st.code(gif_url[:80] + "...")
        with col2:
            gallery = st.session_state.get('gallery_images', [])
            st.write(f"**Галерея:** {'✅ ' + str(len(gallery)) + ' фото' if gallery else '❌ Немає'}")
        with col3:
            products = st.session_state.get('products', [])
            st.write(f"**Товари:** {'✅ ' + str(len(products)) + ' шт' if products else '❌ Немає'}")
            if products:
                has_images = sum(1 for p in products if p.get('image'))
                st.write(f"Зображень товарів: {has_images}")
        
        import json
        config_dict = json.loads(full_config_json)
        st.write(f"📦 **Розмір JSON:** {len(full_config_json)} символів")
        st.write(f" **GIF в JSON:** {'✅ Так' if 'gif_url' in config_dict and config_dict['gif_url'] else '❌ Ні'}")
        
        # 2. Перетворюємо рядок JSON у словник Python
        full_config_dict = json.loads(full_config_json)
        
        # 3. Формуємо дані профілю
        profile_data = {
            'name': st.session_state.get('name_value', ''),
            'bio': st.session_state.get('bio_value', ''),
            'telegram_chat_id': st.session_state.get('telegram_chat_id_value', ''),
            'theme_choice': st.session_state.get('theme_choice_value', 'gradient'),
            'theme_color': st.session_state.get('theme_color_value', '#667eea'),
            'font_choice': st.session_state.get('font_choice_value', 'Inter'),
            'dark_mode': st.session_state.get('dark_mode_value', False),
            'avatar_url': st.session_state.get('avatar_image_data_uri', ''),
            'background_url': st.session_state.get('background_image_data_uri', ''),
            'site_config': full_config_dict
        }
        
        # Зберігаємо в базу
        db.save_profile(user_id, profile_data)
        
        # Зберігаємо посилання та товари
        links = st.session_state.get('links_list', [])
        db.save_links(user_id, links)
        
        products = st.session_state.get('products', [])
        db.save_products(user_id, products)
        
        st.success("✅ Дані збережено в базу!")
        return True
    except Exception as e:
        st.error(f"❌ Помилка збереження в Supabase: {e}")
        return False
def load_config_from_supabase(user_id: str):
    """Завантажує ВСЮ конфігурацію користувача з Supabase (безпечна версія)."""
    print(f"🟢 ПОЧАТОК: Спроба завантажити дані для user_id: {user_id}")
    try:
        profile = db.load_profile(user_id)
        if not profile:
            print("🟡 УВАГА: Профіль не знайдено в базі даних!")
            return False
            
        print("✅ Профіль знайдено. Завантажуємо основні поля...")
        st.session_state['name_value'] = profile.get('name', '')
        st.session_state['bio_value'] = profile.get('bio', '')
        st.session_state['telegram_chat_id_value'] = profile.get('telegram_chat_id', '')
        st.session_state['theme_choice_value'] = profile.get('theme_choice', 'gradient')
        st.session_state['theme_color_value'] = profile.get('theme_color', '#667eea')
        st.session_state['font_choice_value'] = profile.get('font_choice', 'Inter')
        st.session_state['dark_mode_value'] = profile.get('dark_mode', False)
        st.session_state['avatar_image_data_uri'] = profile.get('avatar_url', '')
        st.session_state['background_image_data_uri'] = profile.get('background_url', '')
        
        # Безпечне завантаження site_config
        if profile.get('site_config'):
            try:
                import json
                print("🟡 Обробка site_config...")
                if isinstance(profile['site_config'], str):
                    config = json.loads(profile['site_config'])
                else:
                    config = profile['site_config']
                
                print(f"🔍 Розмір site_config: {len(str(config))} символів")
                
                st.session_state['faq_items'] = config.get('faq_items', [])
                st.session_state['countdown_date'] = config.get('countdown_date', '')
                st.session_state['countdown_title'] = config.get('countdown_title', 'До події залишилось')
                st.session_state['custom_html'] = config.get('custom_html', '')
                st.session_state['gif_url'] = config.get('gif_url', '')
                st.session_state['gif_caption'] = config.get('gif_caption', '')
                st.session_state['quote_text'] = config.get('quote_text', '')
                st.session_state['quote_author'] = config.get('quote_author', '')
                st.session_state['features'] = config.get('features', [])
                st.session_state['gallery_images'] = config.get('gallery_images', [])
                st.session_state['contact_title'] = config.get('contact_title', '')
                st.session_state['contact_info'] = config.get('contact_info', '')
                st.session_state['products'] = config.get('products', [])
                print("✅ Блоки з site_config успішно завантажено!")
            except Exception as e:
                print(f"❌ ПОМИЛКА читання site_config: {e}. Пропускаємо блоки.")
        else:
            print("🟡 site_config відсутній, використовуємо значення за замовчуванням.")
            # Ініціалізуємо порожні списки, щоб уникнути помилок KeyError
            for key in ['faq_items', 'features', 'gallery_images', 'products']:
                if key not in st.session_state:
                    st.session_state[key] = []
        
        # Завантажуємо посилання
        print("🟡 Завантажуємо посилання...")
        links = db.load_links(user_id)
        st.session_state.links_list = links if links else []
        print(f"✅ Завантажено {len(st.session_state.links_list)} посилань.")
        
        print("🟢 ЗАВЕРШЕНО: Дані успішно завантажено в session_state!")
        return True
        
    except Exception as e:
        print(f"🔴 КРИТИЧНА ПОМИЛКА в load_config_from_supabase: {e}")
        import traceback
        traceback.print_exc()
        return False
    
def export_config():
    config = {
        'name': st.session_state.get('name_value', ''),
        'bio': st.session_state.get('bio_value', ''),
        'theme_color': st.session_state.get('theme_color_value', '#667eea'),
        'theme_choice': st.session_state.get('theme_choice_value', 'gradient'),
        'font_choice': st.session_state.get('font_choice_value', 'Inter'),
        'dark_mode': st.session_state.get('dark_mode_value', False),
        'avatar_image_data_uri': st.session_state.get('avatar_image_data_uri', ''),
        # 'background_image_data_uri' видалено - зберігається окремо в background_url
        'links_list': st.session_state.get('links_list', []),
        'faq_items': st.session_state.get('faq_items', []),
        'countdown_date': st.session_state.get('countdown_date', ''),
        'countdown_title': st.session_state.get('countdown_title', 'До події залишилось'),
        'custom_html': st.session_state.get('custom_html', ''),
        'gif_url': st.session_state.get('gif_url', ''),
        'gif_caption': st.session_state.get('gif_caption', ''),
        'quote_text': st.session_state.get('quote_text', ''),
        'quote_author': st.session_state.get('quote_author', ''),
        'features': st.session_state.get('features', []),
        'gallery_images': st.session_state.get('gallery_images', []),
        'contact_title': st.session_state.get('contact_title', ''),
        'contact_info': st.session_state.get('contact_info', ''),
        'products': st.session_state.get('products', []),
    }
    return json.dumps(config, ensure_ascii=False, indent=2)
def import_config(json_string):
    try:
        config = json.loads(json_string)
        st.session_state['name_value'] = config.get('name', '')
        st.session_state['bio_value'] = config.get('bio', '')
        st.session_state['theme_color_value'] = config.get('theme_color', '#667eea')
        st.session_state['theme_choice_value'] = config.get('theme_choice', 'gradient')
        st.session_state['font_choice_value'] = config.get('font_choice', 'Inter')
        st.session_state['dark_mode_value'] = config.get('dark_mode', False)
        st.session_state['avatar_image_data_uri'] = config.get('avatar_image_data_uri', '')
        st.session_state['background_image_data_uri'] = config.get('background_image_data_uri', '')
        st.session_state.links_list = config.get('links_list', [])
        st.session_state.faq_items = config.get('faq_items', [])
        st.session_state.countdown_date = config.get('countdown_date', '')
        st.session_state.countdown_title = config.get('countdown_title', 'До події залишилось')
        st.session_state.custom_html = config.get('custom_html', '')
        st.session_state.gif_url = config.get('gif_url', '')
        st.session_state.gif_caption = config.get('gif_caption', '')
        st.session_state.quote_text = config.get('quote_text', '')
        st.session_state.quote_author = config.get('quote_author', '')
        st.session_state.features = config.get('features', [])
        st.session_state.gallery_images = config.get('gallery_images', [])
        st.session_state.contact_title = config.get('contact_title', '')
        st.session_state.contact_info = config.get('contact_info', '')
        st.session_state.products = config.get('products', [])
        save_config_to_supabase(st.session_state.user_id)
        return True
    except Exception as e:
        st.error(f"❌ Помилка імпорту: {e}")
        return False

# ============================================================================
# ІНІЦІАЛІЗАЦІЯ SESSION STATE (Обов'язково на початку!)
# ============================================================================
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
    
if 'config_loaded' not in st.session_state:
    st.session_state.config_loaded = False

# Завантажуємо конфігурацію ТІЛЬКИ якщо користувач увійшов і ще не завантажував
if not st.session_state.config_loaded and st.session_state.user_id:
    load_config_from_supabase(st.session_state.user_id)
    st.session_state.config_loaded = True

# ============================================================================
# ГЕНЕРАЦІЯ ДОДАТКОВИХ БЛОКІВ
# ============================================================================

def generate_faq_block(faq_items: List[Dict]) -> str:
    if not faq_items: return ""
    items_html = "".join([f"""
        <div class="faq-item">
            <button class="faq-question" onclick="toggleFAQ({idx})" aria-expanded="false">
                <span>{item['question']}</span><span class="faq-icon">+</span>
            </button>
            <div class="faq-answer" id="faq-answer-{idx}"><p>{item['answer']}</p></div>
        </div>""" for idx, item in enumerate(faq_items)])
    return f'<div class="faq-section"><h2 class="block-title">❓ Часті питання</h2>{items_html}</div>'

def generate_countdown_block(target_date: str, title: str) -> str:
    if not target_date: return ""
    return f"""
    <div class="countdown-section">
        <h2 class="block-title">⏰ {title}</h2>
        <div class="countdown" id="countdown" data-target="{target_date}">
            <div class="countdown-item"><span class="countdown-value" id="days">00</span><span class="countdown-label">Днів</span></div>
            <div class="countdown-item"><span class="countdown-value" id="hours">00</span><span class="countdown-label">Годин</span></div>
            <div class="countdown-item"><span class="countdown-value" id="minutes">00</span><span class="countdown-label">Хвилин</span></div>
            <div class="countdown-item"><span class="countdown-value" id="seconds">00</span><span class="countdown-label">Секунд</span></div>
        </div>
    </div>"""

def generate_custom_html_block(custom_html: str) -> str:
    return f'<div class="custom-html-section">{custom_html}</div>' if custom_html.strip() else ""

def generate_gif_block(gif_url: str, caption: str = "") -> str:
    if not gif_url: return ""
    caption_html = f"<p class='gif-caption'>{caption}</p>" if caption else ""
    return f'<div class="gif-section"><img src="{gif_url}" alt="GIF" class="gif-image" loading="lazy">{caption_html}</div>'

def generate_quote_block(quote_text: str, quote_author: str) -> str:
    if not quote_text: return ""
    author_html = f'<cite class="quote-author">— {quote_author}</cite>' if quote_author else ""
    return f"""
    <div class="quote-section">
        <blockquote class="quote-block">
            <span class="quote-mark">"</span><p class="quote-text">{quote_text}</p>{author_html}
        </blockquote>
    </div>"""

def generate_features_block(features: List[Dict]) -> str:
    if not features: return ""
    items_html = "".join([f"""
        <div class="feature-card">
            <div class="feature-icon">{feat.get('icon', '✨')}</div>
            <h3 class="feature-title">{feat['title']}</h3>
            <p class="feature-desc">{feat['description']}</p>
        </div>""" for feat in features])
    return f'<div class="features-section"><h2 class="block-title">⭐ Переваги</h2><div class="features-grid">{items_html}</div></div>'

def generate_gallery_block(images: List[Dict]) -> str:
    if not images: return ""
    items_html = "".join([f'<div class="gallery-item" onclick="openLightbox({idx})"><img src="{img["src"]}" alt="{img.get("caption", "")}" loading="lazy"></div>' for idx, img in enumerate(images)])
    lightbox_items = "".join([f'<div class="lightbox-slide"><img src="{img["src"]}" alt="{img.get("caption", "")}"></div>' for img in images])
    return f"""
    <div class="gallery-section"><h2 class="block-title">📸 Галерея</h2><div class="gallery-grid">{items_html}</div></div>
    <div class="lightbox" id="lightbox" onclick="closeLightbox()">
        <span class="lightbox-close">&times;</span><div class="lightbox-content" id="lightbox-content">{lightbox_items}</div>
    </div>"""

def generate_contact_form_block(form_title: str, recipient_info: str) -> str:
    if not form_title: return ""
    return f"""
    <div class="contact-section">
        <h2 class="block-title">{form_title}</h2>
        <form class="contact-form" onsubmit="submitContactForm(event)">
            <input type="text" name="name" placeholder="Ваше ім'я" required class="form-input">
            <input type="email" name="email" placeholder="Ваш email" required class="form-input">
            <textarea name="message" placeholder="Ваше повідомлення" required class="form-input form-textarea"></textarea>
            <button type="submit" class="form-submit">📩 Надіслати</button>
        </form>
        <p class="form-info">{recipient_info}</p>
        <div id="form-success" class="form-success" style="display:none;">✅ Дякуємо! Ваше повідомлення надіслано.</div>
    </div>"""

def generate_products_block(products: List[Dict], theme_color: str) -> str:
    """Генерує каталог товарів з кошиком"""
    if not products: return ""
    items_html = ""
    
    for idx, prod in enumerate(products):
        prod_id = prod.get('id', str(idx))
        
        # Підтримуємо як 'image' (з конструктора), так і 'image_url' (з бази даних)
        prod_img = prod.get('image') or prod.get('image_url', '')
        if prod_img:
            img_src = fix_image_mime_type(prod_img)
            safe_title = prod['title'].replace("'", "\\'").replace('"', '\\"')
            img_html = f"""
            <div class="product-image-wrapper" 
                 data-img-src="{img_src}" 
                 data-img-title="{safe_title}"
                 onclick="openProductLightbox(this)">
                <img src="{img_src}" alt="{prod["title"]}" class="product-image" loading="lazy">
                <div class="zoom-icon">🔍</div>
            </div>"""
        else:
            img_html = '<div class="product-placeholder">🛍️</div>'
        
        safe_title_btn = prod['title'].replace("'", "\\'").replace('"', '\\"')
        
        items_html += f"""
        <div class="product-card" data-product-id="{prod_id}">
            {img_html}
            <h3 class="product-title">{prod['title']}</h3>
            <p class="product-desc">{prod.get('description', '')}</p>
            <div class="product-price">{prod.get('price', 0)}₴</div>
            <button class="product-btn" 
                    onclick="addToCart('{prod_id}', '{safe_title_btn}', {prod.get('price', 0)})">
                🛒 В кошик
            </button>
        </div>"""
    
    return f"""
    <div class="products-section" id="section-products">
        <h2 class="block-title">🛍️ Каталог товарів</h2>
        <div class="products-grid">{items_html}</div>
    </div>
    
    <div class="cart-icon" onclick="openCart()" id="cartIcon">
        🛒 <span class="cart-count" id="cartCount">0</span>
    </div>
    
    <div class="modal" id="cartModal" onclick="closeCart()">
        <div class="modal-content cart-modal-content" onclick="event.stopPropagation()">
            <span class="lightbox-close" onclick="closeCart()">&times;</span>
            <h2 class="modal-title">🛒 Ваш кошик</h2>
            <div id="cartItems" class="cart-items">
                <p class="cart-empty">Кошик порожній</p>
            </div>
            <div class="cart-total" id="cartTotal" style="display:none;">
                <strong>Загальна сума:</strong> <span id="totalAmount">0</span>₴
            </div>
            <button class="btn-pay" id="checkoutBtn" onclick="openCheckoutForm()" style="display:none;">
                ✅ Оформити замовлення
            </button>
        </div>
    </div>
    
    <div class="modal" id="checkoutModal" onclick="closeCheckoutForm()">
        <div class="modal-content checkout-modal-content" onclick="event.stopPropagation()">
            <span class="lightbox-close" onclick="closeCheckoutForm()">&times;</span>
            <h2 class="modal-title">📦 Оформлення замовлення</h2>
            <form id="checkoutForm" onsubmit="submitOrder(event)" autocomplete="off">
                <div class="form-group">
                    <label>Ім'я *</label>
                    <input type="text" name="customer_name" required class="form-input" placeholder="Введіть ваше ім'я">
                </div>
                <div class="form-group">
                    <label>Прізвище *</label>
                    <input type="text" name="customer_surname" required class="form-input" placeholder="Введіть ваше прізвище">
                </div>
                <div class="form-group">
                    <label>Телефон *</label>
                    <input type="tel" name="customer_phone" required class="form-input" placeholder="+380 (00) 000-00-00">
                </div>
                <div class="form-group">
                    <label>Область *</label>
                    <input type="text" name="delivery_region" required class="form-input" placeholder="Наприклад: Київська область">
                </div>
                <div class="form-group">
                    <label>Місто/Населений пункт *</label>
                    <input type="text" name="delivery_city" required class="form-input" placeholder="Наприклад: Київ, Буча">
                </div>
                <div class="form-group">
                    <label>Спосіб доставки *</label>
                    <select name="delivery_type" required class="form-input">
                        <option value="">Оберіть спосіб доставки</option>
                        <option value="Нова Пошта">Нова Пошта</option>
                        <option value="Укрпошта">Укрпошта</option>
                        <option value="Кур'єр">Кур'єр</option>
                        <option value="Самовивіз">Самовивіз</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Відділення / Адреса *</label>
                    <input type="text" name="delivery_address" required class="form-input" placeholder="Наприклад: Відділення №5">
                </div>
                <div class="form-group">
                    <label>Коментар</label>
                    <textarea name="comment" class="form-input form-textarea" placeholder="Додаткові побажання"></textarea>
                </div>
                <button type="submit" class="btn-pay">✅ Підтвердити замовлення</button>
            </form>
            <div id="orderSuccess" style="display:none; text-align:center; padding:30px;">
                <div style="font-size:64px; margin-bottom:20px;">✅</div>
                <h3>Дякуємо за замовлення!</h3>
                <p>З вами зв'яжуться протягом години.</p>
            </div>
        </div>
    </div>
    
    <script>
        var cart = JSON.parse(localStorage.getItem('cart') || '[]');
        
        function updateCartCount() {{
            var count = cart.reduce(function(sum, item) {{ return sum + item.quantity; }}, 0);
            document.getElementById('cartCount').textContent = count;
            localStorage.setItem('cart', JSON.stringify(cart));
        }}
        
        function addToCart(id, title, price) {{
            var existingItem = cart.find(function(item) {{ return item.id === id; }});
            if (existingItem) {{
                existingItem.quantity += 1;
            }} else {{
                cart.push({{ id: id, title: title, price: price, quantity: 1 }});
            }}
            updateCartCount();
            
            var btn = event.target;
            var originalText = btn.innerHTML;
            btn.innerHTML = '✅ Додано!';
            btn.style.background = '#00c853';
            setTimeout(function() {{
                btn.innerHTML = originalText;
                btn.style.background = '';
            }}, 1500);
        }}
        
        function openCart() {{
            var cartItems = document.getElementById('cartItems');
            var cartTotal = document.getElementById('cartTotal');
            var checkoutBtn = document.getElementById('checkoutBtn');
            
            if (cart.length === 0) {{
                cartItems.innerHTML = '<p class="cart-empty">Кошик порожній</p>';
                cartTotal.style.display = 'none';
                checkoutBtn.style.display = 'none';
            }} else {{
                var html = '';
                var total = 0;
                cart.forEach(function(item, index) {{
                    var itemTotal = item.price * item.quantity;
                    total += itemTotal;
                    html += '<div class="cart-item"><div class="cart-item-info"><strong>' + item.title + '</strong><div class="cart-item-price">' + item.price + '₴ × ' + item.quantity + ' = ' + itemTotal + '₴</div></div><div class="cart-item-controls"><button onclick="changeQuantity(' + index + ', -1)">−</button><span>' + item.quantity + '</span><button onclick="changeQuantity(' + index + ', 1)">+</button><button onclick="removeFromCart(' + index + ')" class="remove-btn">🗑️</button></div></div>';
                }});
                cartItems.innerHTML = html;
                document.getElementById('totalAmount').textContent = total;
                cartTotal.style.display = 'block';
                checkoutBtn.style.display = 'block';
            }}
            document.getElementById('cartModal').classList.add('show');
        }}
        
        function closeCart() {{ document.getElementById('cartModal').classList.remove('show'); }}
        
        function changeQuantity(index, delta) {{
            cart[index].quantity += delta;
            if (cart[index].quantity <= 0) {{ cart.splice(index, 1); }}
            updateCartCount();
            openCart();
        }}
        
        function removeFromCart(index) {{
            cart.splice(index, 1);
            updateCartCount();
            openCart();
        }}
        
        function openCheckoutForm() {{
            closeCart();
            document.getElementById('checkoutForm').style.display = 'block';
            document.getElementById('orderSuccess').style.display = 'none';
            document.getElementById('checkoutModal').classList.add('show');
        }}
        
        function closeCheckoutForm() {{ document.getElementById('checkoutModal').classList.remove('show'); }}
        
        function submitOrder(event) {{
            event.preventDefault();
            var form = event.target;
            
            function getVal(name) {{
                var el = form.querySelector('[name="' + name + '"]');
                return el ? el.value.trim() : '';
            }}
            
            var safeItems = cart.map(function(item) {{
                return {{
                    id: String(item.id || ''),
                    title: String(item.title || ''),
                    price: Math.round(Number(item.price) || 0),
                    quantity: Math.round(Number(item.quantity) || 1)
                }};
            }});
            
            var total = Math.round(cart.reduce(function(sum, item) {{ 
                return sum + (Number(item.price) * Number(item.quantity)); 
            }}, 0));
            
            var orderData = {{
                customer_name: getVal('customer_name'),
                customer_surname: getVal('customer_surname'),
                customer_phone: getVal('customer_phone'),
                delivery_region: getVal('delivery_region'),
                delivery_city: getVal('delivery_city'),
                delivery_type: getVal('delivery_type'),
                delivery_address: getVal('delivery_address'),
                comment: getVal('comment'),
                items_json: safeItems,
                total_amount: total
            }};
            
            console.log('📦 Дані замовлення:', JSON.stringify(orderData, null, 2));
            
            if (!window.SUPABASE_URL || !window.PROFILE_ID) {{
                alert('Помилка: Дані для підключення до бази не завантажені.');
                return;
            }}

            var submitBtn = form.querySelector('button[type="submit"]');
            var originalBtnText = submitBtn.innerHTML;
            submitBtn.innerHTML = '⏳ Відправка...';
            submitBtn.disabled = true;
            
            fetch(window.SUPABASE_URL + '/rest/v1/rpc/create_order_rpc', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'apikey': window.SUPABASE_ANON_KEY,
                    'Authorization': 'Bearer ' + window.SUPABASE_ANON_KEY
                }},
                body: JSON.stringify({{
                    p_profile_id: window.PROFILE_ID,
                    p_order_data: orderData
                }})
            }})
            .then(function(response) {{
                console.log('📥 Статус відповіді:', response.status);
                if (!response.ok) {{
                    return response.text().then(function(text) {{
                        throw new Error("Supabase помилка " + response.status + ": " + text);
                    }});
                }}
                return response.json();
            }})
            .then(function(data) {{
                console.log('📥 Успішна відповідь:', data);
                if (data.success) {{
                    form.style.display = 'none';
                    document.getElementById('orderSuccess').style.display = 'block';
                    cart = [];
                    updateCartCount();
                    setTimeout(function() {{
                        closeCheckoutForm();
                        form.reset();
                        form.style.display = 'block';
                        document.getElementById('orderSuccess').style.display = 'none';
                        submitBtn.innerHTML = originalBtnText;
                        submitBtn.disabled = false;
                    }}, 3000);
                }} else {{
                    alert('Помилка: ' + (data.error || 'Невідома помилка'));
                    submitBtn.innerHTML = originalBtnText;
                    submitBtn.disabled = false;
                }}
            }})
            .catch(function(error) {{
                console.error('❌ КРИТИЧНА ПОМИЛКА:', error.message);
                alert('Помилка: ' + error.message);
                submitBtn.innerHTML = originalBtnText;
                submitBtn.disabled = false;
            }});
        }}
        
        function openProductLightbox(element) {{
            var src = element.getAttribute('data-img-src');
            var title = element.getAttribute('data-img-title');
            document.getElementById('productImageModalImg').src = src;
            document.getElementById('productImageModalTitle').textContent = title;
            document.getElementById('productImageModal').classList.add('show');
        }}
        
        function closeProductImageModal() {{
            document.getElementById('productImageModal').classList.remove('show');
        }}
        
        updateCartCount();
    </script>
    """
# ============================================================================
# ГЕНЕРАЦІЯ ПОВНОГО HTML
# ============================================================================

def generate_full_html(name, bio, avatar_image_data_uri, links, theme_color, theme_choice, font_choice, dark_mode, background_image_data_uri, faq_items, countdown_date, countdown_title, custom_html, gif_url, gif_caption, quote_text, quote_author, features, gallery_images, contact_title, contact_info, products, supabase_url='', supabase_anon_key='', profile_id=''):
    icon_svg = generate_icon_svg(name, theme_color)
    icon_data_uri = svg_to_data_uri(icon_svg)
    theme_styles = get_theme_styles(theme_choice, theme_color)
    
    manifest = {
        "name": name, 
        "short_name": name[:12], 
        "description": bio if bio else "🚀 SmartLink - створи свій сайт за 5 хвилин!", 
        "start_url": ".", 
        "display": "standalone",
        "background_color": theme_styles['bg'] if not str(theme_styles['bg']).startswith('linear') else "#ffffff",
        "theme_color": theme_color,
        "icons": [{"src": icon_data_uri, "sizes": "192x192", "type": "image/svg+xml", "purpose": "any maskable"}]
    }
    manifest_data_uri = f"data:application/json;base64,{base64.b64encode(json.dumps(manifest).encode()).decode()}"
    
    backdrop_filter_css = f"backdrop-filter: {theme_styles.get('backdrop_filter', '')};" if theme_styles.get('backdrop_filter') else ""
    background_css = f"background: {theme_styles['bg']};" if not background_image_data_uri else f"background: url('{background_image_data_uri}') center/cover fixed;"
    
    avatar_html = f"<img src='{avatar_image_data_uri}' alt='Avatar' loading='lazy'>" if avatar_image_data_uri else name[0].upper()
    
    links_html = "".join([f"""<a href="#" class="link {'paid' if link.get('is_paid') else ''}" id="{link['id']}" 
        data-title="{link['title']}" data-url="{link['url']}" data-paid="{str(link.get('is_paid', False)).lower()}" data-price="{link.get('price', 0)}" 
        onclick="handleLinkClick(event, this)" aria-label="{link['title']}">
        <span class="drag-handle" aria-hidden="true">⋮⋮</span>
        <span class="lock-icon" aria-hidden="true">{'🔒' if link.get('is_paid') else ''}</span>
        {link['title']}{'<span class="price-badge">$' + str(link.get('price', 0)) + '</span>' if link.get('is_paid') else ''}
    </a>""" for link in links])
    
    extra_blocks = generate_gif_block(gif_url, gif_caption) + generate_quote_block(quote_text, quote_author) + \
                   generate_features_block(features) + generate_gallery_block(gallery_images) + \
                   generate_products_block(products, theme_color) + generate_faq_block(faq_items) + \
                   generate_countdown_block(countdown_date, countdown_title) + \
                   generate_contact_form_block(contact_title, contact_info) + generate_custom_html_block(custom_html)

    return f"""<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>{name}</title>
    <meta name="theme-color" content="{theme_color}">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="{name}">
    <link rel="apple-touch-icon" href="{icon_data_uri}">
    <link rel="icon" type="image/svg+xml" href="{icon_data_uri}">
    <link rel="manifest" href="{manifest_data_uri}">
    <meta name="description" content="{bio}">
    <meta property="og:title" content="{name}">
    <meta property="og:description" content="{bio}">
    <meta property="og:type" content="website">
    <meta name="twitter:card" content="summary">
    <meta name="twitter:title" content="{name}">
    <meta name="twitter:description" content="{bio}">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family={font_choice.replace(' ', '+')}:wght@400;600;700&display=swap" rel="stylesheet">
    <script>
        window.SUPABASE_URL = '{supabase_url}';
        window.SUPABASE_ANON_KEY = '{supabase_anon_key}';
        window.PROFILE_ID = '{profile_id}';
    </script>
    <script src="https://cdn.jsdelivr.net/npm/build/heatmap.min.js"></script>
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
         body {{ font-family: '{font_choice}', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; {background_css} min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; position: relative; transition: background 0.3s ease; overflow-x: hidden; }}
        .container {{ background: {theme_styles['container_bg']}; border-radius: {theme_styles['border_radius']}; padding: 40px; max-width: 500px; width: 100%; box-shadow: {theme_styles['shadow']}; text-align: center; position: relative; z-index: 10; border: {theme_styles['border']}; {backdrop_filter_css} animation: fadeIn 0.6s ease; }}
        @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .avatar {{ width: 120px; height: 120px; border-radius: 50%; margin: 0 auto 20px; background: {theme_styles['link_bg']}; display: flex; align-items: center; justify-content: center; font-size: 48px; color: {theme_styles['link_text']}; overflow: hidden; animation: scaleIn 0.5s ease 0.2s both; }}
        @keyframes scaleIn {{ from {{ transform: scale(0); }} to {{ transform: scale(1); }} }}
        .avatar img {{ width: 100%; height: 100%; object-fit: cover; }}
        h1 {{ color: {theme_styles['text']}; margin-bottom: 10px; font-size: 28px; animation: slideUp 0.5s ease 0.3s both; }}
        .bio {{ color: {theme_styles['text']}; margin-bottom: 30px; line-height: 1.6; opacity: 0.8; animation: slideUp 0.5s ease 0.4s both; }}
        @keyframes slideUp {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        .links {{ display: flex; flex-direction: column; gap: 15px; }}
        .link {{ background: {theme_styles['link_bg']}; color: {theme_styles['link_text']}; padding: 15px 30px; border-radius: {theme_styles['border_radius']}; text-decoration: none; font-weight: 600; transition: all 0.3s ease; cursor: pointer; position: relative; display: flex; align-items: center; justify-content: center; gap: 10px; animation: slideUp 0.5s ease both; }}
        .link:nth-child(1) {{ animation-delay: 0.5s; }} .link:nth-child(2) {{ animation-delay: 0.6s; }} .link:nth-child(3) {{ animation-delay: 0.7s; }} .link:nth-child(4) {{ animation-delay: 0.8s; }} .link:nth-child(5) {{ animation-delay: 0.9s; }}
        .link:hover {{ transform: translateY(-3px) scale(1.02); box-shadow: 0 15px 30px rgba(0,0,0,0.2); }}
        .link.paid {{ background: linear-gradient(135deg, #ffd700 0%, #ff8c00 100%); }}
        .link.paid.unlocked {{ background: linear-gradient(135deg, #00c853 0%, #009624 100%); }}
        .price-badge {{ background: rgba(0,0,0,0.3); padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; }}
        .lock-icon {{ font-size: 18px; }}
        .link.sortable-ghost {{ opacity: 0.4; }} .link.sortable-chosen {{ transform: scale(1.05); }}
        .drag-handle {{ position: absolute; left: 15px; top: 50%; transform: translateY(-50%); cursor: move; opacity: 0.6; }}
        .modal {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 10002; justify-content: center; align-items: center; }}
        .modal.show {{ display: flex; align-items: center; justify-content: center; padding: 20px; }}
        .modal-content {{ 
            background: white; border-radius: 20px; padding: 30px; max-width: 400px; width: 100%; 
            text-align: center; animation: modalSlide 0.3s ease; 
            max-height: 90vh; overflow-y: auto; position: relative;
        }}
        @keyframes modalSlide {{ from {{ transform: translateY(-50px); opacity: 0; }} to {{ transform: translateY(0); opacity: 1; }} }}
        .modal-icon {{ font-size: 64px; margin-bottom: 20px; }} .modal-title {{ font-size: 24px; color: #333; margin-bottom: 10px; }}
        .modal-price {{ font-size: 36px; font-weight: 700; color: {theme_color}; margin: 20px 0; }}
        .modal-description {{ color: #666; margin-bottom: 30px; line-height: 1.6; }}
        .modal-buttons {{ display: flex; gap: 10px; flex-direction: column; }}
        .btn-pay {{ background: linear-gradient(135deg, #00c853 0%, #009624 100%); color: white; border: none; padding: 15px 30px; border-radius: 50px; font-weight: 600; font-size: 16px; cursor: pointer; transition: transform 0.2s; }}
        .btn-pay:hover {{ transform: scale(1.05); }}
        .btn-cancel {{ background: #f0f0f0; color: #666; border: none; padding: 12px 30px; border-radius: 50px; cursor: pointer; font-size: 14px; }}
        .payment-methods {{ display: flex; justify-content: center; gap: 15px; margin: 20px 0; font-size: 24px; }}
        .edit-mode-toggle {{ position: fixed; bottom: 20px; left: 20px; background: {theme_color}; color: white; border: none; padding: 10px 20px; border-radius: 25px; cursor: pointer; z-index: 10000; font-size: 14px; }}
        .edit-mode-active {{ background: #ff6b6b; }}
        .pwa-banner {{ position: fixed; bottom: 80px; left: 20px; right: 20px; background: white; padding: 15px 20px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); display: none; align-items: center; gap: 15px; z-index: 10001; max-width: 400px; margin: 0 auto; }}
        .pwa-banner.show {{ display: flex; }} .pwa-banner-icon {{ width: 50px; height: 50px; border-radius: 10px; }}
        .pwa-banner-text {{ flex: 1; font-size: 14px; }} .pwa-banner-text strong {{ display: block; margin-bottom: 3px; }}
        .pwa-banner-btn {{ background: {theme_color}; color: white; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; }}
        .pwa-banner-close {{ background: none; border: none; font-size: 20px; cursor: pointer; color: #999; }}
        #heatmap-container {{ position: fixed; top: 0; left: 0; right: 0; bottom: 0; width: auto; height: auto; pointer-events: none; z-index: 9999; transform: scale(0); opacity: 0; transition: transform 0.3s, opacity 0.3s; will-change: transform, opacity; }}
        #heatmap-container.active {{ transform: scale(1); opacity: 1; }}
        .heatmap-toggle {{ position: fixed; bottom: 70px; left: 20px; background: #333; color: white; border: none; padding: 10px 20px; border-radius: 25px; cursor: pointer; z-index: 10000; font-size: 14px; }}
        .stats-panel {{ position: fixed; top: 20px; right: 20px; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.2); z-index: 10000; display: none; max-width: 350px; }}
        .stats-panel.show {{ display: block; }} .stats-panel h3 {{ margin-bottom: 15px; color: #333; }}
        .stats-filters {{ display: flex; gap: 5px; margin-bottom: 15px; flex-wrap: wrap; }}
        .filter-btn {{ flex: 1; min-width: 60px; padding: 6px 10px; border: 1px solid #ddd; background: white; border-radius: 15px; cursor: pointer; font-size: 11px; font-weight: 600; transition: all 0.2s; }}
        .filter-btn:hover {{ background: #f0f0f0; }}
        .filter-btn.active {{ background: {theme_color}; color: white; border-color: {theme_color}; }}
        .period-info {{ font-size: 11px; color: #999; margin-bottom: 10px; text-align: center; }}
        .stat-item {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }}
        .theme-toggle {{ position: fixed; top: 20px; left: 20px; background: {theme_color}; color: white; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; z-index: 10000; font-size: 20px; display: flex; align-items: center; justify-content: center; }}
        body.dark-mode {{ background: #0f0f0f !important; }}
        body.dark-mode .container {{ background: #1e1e1e !important; box-shadow: 0 10px 40px rgba(0,0,0,0.8) !important; }}
        body.dark-mode h1, body.dark-mode .bio {{ color: #ffffff !important; }}
        body.dark-mode .bio {{ opacity: 0.85 !important; }}
        body.dark-mode .modal-content {{ background: #1e1e1e !important; }}
        body.dark-mode .modal-title {{ color: #ffffff !important; }}
        body.dark-mode .modal-description {{ color: #cccccc !important; }}
        body.dark-mode .btn-cancel {{ background: #333333 !important; color: #ffffff !important; }}
        body.dark-mode .stats-panel {{ background: #1e1e1e !important; color: #ffffff !important; }}
        body.dark-mode .stats-panel h3 {{ color: #ffffff !important; }}
        body.dark-mode .stat-item {{ border-bottom-color: #333 !important; color: #ffffff !important; }}
        body.dark-mode .pwa-banner {{ background: #1e1e1e !important; color: #ffffff !important; }}
        body.dark-mode .pwa-banner-text strong {{ color: #ffffff !important; }}
        body.dark-mode .filter-btn {{ background: #2d2d2d; color: #fff; border-color: #444; }}
        body.dark-mode .filter-btn:hover {{ background: #3d3d3d; }}
        body.dark-mode .filter-btn.active {{ background: {theme_color}; border-color: {theme_color}; }}
        .faq-section {{ margin-top: 30px; text-align: left; }}
        .block-title {{ color: {theme_styles['text']}; font-size: 22px; margin-bottom: 20px; text-align: center; }}
        .faq-item {{ margin-bottom: 10px; border: 1px solid rgba(0,0,0,0.1); border-radius: 10px; overflow: hidden; }}
        body.dark-mode .faq-item {{ border-color: rgba(255,255,255,0.1); }}
        .faq-question {{ width: 100%; padding: 15px 20px; background: {theme_styles['container_bg']}; border: none; text-align: left; cursor: pointer; font-size: 16px; font-weight: 600; color: {theme_styles['text']}; display: flex; justify-content: space-between; align-items: center; transition: background 0.2s; }}
        .faq-question:hover {{ background: rgba(0,0,0,0.05); }}
        body.dark-mode .faq-question:hover {{ background: rgba(255,255,255,0.05); }}
        .faq-icon {{ font-size: 24px; transition: transform 0.3s; }}
        .faq-item.active .faq-icon {{ transform: rotate(45deg); }}
        .faq-answer {{ max-height: 0; overflow: hidden; transition: max-height 0.3s ease, padding 0.3s ease; background: rgba(0,0,0,0.02); }}
        body.dark-mode .faq-answer {{ background: rgba(255,255,255,0.02); }}
        .faq-item.active .faq-answer {{ max-height: 500px; padding: 15px 20px; }}
        .faq-answer p {{ color: {theme_styles['text']}; opacity: 0.8; line-height: 1.6; }}
        .countdown-section {{ margin-top: 30px; }}
        .countdown {{ display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; }}
        .countdown-item {{ background: {theme_styles['link_bg']}; color: {theme_styles['link_text']}; padding: 20px 25px; border-radius: 15px; min-width: 90px; text-align: center; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .countdown-value {{ font-size: 36px; font-weight: 700; display: block; }}
        .countdown-label {{ font-size: 12px; text-transform: uppercase; opacity: 0.8; margin-top: 5px; display: block; }}
        .custom-html-section {{ margin-top: 30px; padding: 20px; background: rgba(0,0,0,0.02); border-radius: 10px; }}
        body.dark-mode .custom-html-section {{ background: rgba(255,255,255,0.05); }}
        .gif-section {{ margin-top: 30px; text-align: center; }}
        .gif-image {{ max-width: 100%; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.2); }}
        .gif-caption {{ margin-top: 10px; color: {theme_styles['text']}; opacity: 0.7; font-size: 14px; }}
        .quote-section {{ margin-top: 30px; }}
        .quote-block {{ position: relative; padding: 30px; background: rgba(0,0,0,0.03); border-left: 4px solid {theme_color}; border-radius: 10px; text-align: left; }}
        body.dark-mode .quote-block {{ background: rgba(255,255,255,0.05); }}
        .quote-mark {{ position: absolute; top: -10px; left: 15px; font-size: 80px; color: {theme_color}; opacity: 0.3; font-family: Georgia, serif; }}
        .quote-text {{ color: {theme_styles['text']}; font-size: 18px; line-height: 1.6; font-style: italic; margin-bottom: 10px; }}
        .quote-author {{ color: {theme_styles['text']}; opacity: 0.7; font-size: 14px; font-style: normal; }}
        .features-section {{ margin-top: 30px; }}
        .features-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; }}
        .feature-card {{ background: rgba(0,0,0,0.03); padding: 20px; border-radius: 15px; text-align: center; transition: transform 0.2s; }}
        body.dark-mode .feature-card {{ background: rgba(255,255,255,0.05); }}
        .feature-card:hover {{ transform: translateY(-3px); }}
        .feature-icon {{ font-size: 36px; margin-bottom: 10px; }}
        .feature-title {{ color: {theme_styles['text']}; font-size: 16px; margin-bottom: 5px; }}
        .feature-desc {{ color: {theme_styles['text']}; opacity: 0.7; font-size: 13px; }}
        .gallery-section {{ margin-top: 30px; }}
        .gallery-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px; }}
        .gallery-item {{ aspect-ratio: 1; overflow: hidden; border-radius: 10px; cursor: pointer; transition: transform 0.2s; }}
        .gallery-item:hover {{ transform: scale(1.05); }}
        .gallery-item img {{ width: 100%; height: 100%; object-fit: cover; }}
        .lightbox {{ display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 20000; justify-content: center; align-items: center; }}
        .lightbox.show {{ display: flex; }}
        .lightbox-close {{ position: absolute; top: 20px; right: 30px; color: white; font-size: 40px; cursor: pointer; z-index: 20001; }}
        .lightbox-slide {{ display: none; max-width: 90%; max-height: 90%; }}
        .lightbox-slide.active {{ display: block; }}
        .lightbox-slide img {{ max-width: 100%; max-height: 90vh; border-radius: 10px; }}
        .contact-section {{ margin-top: 30px; text-align: left; }}
        .contact-form {{ display: flex; flex-direction: column; gap: 12px; }}
        .form-input {{ padding: 12px 15px; border: 1px solid rgba(0,0,0,0.1); border-radius: 10px; font-size: 14px; font-family: inherit; background: rgba(255,255,255,0.8); color: #333; }}
        body.dark-mode .form-input {{ background: rgba(255,255,255,0.1); border-color: rgba(255,255,255,0.2); color: #fff; }}
        .form-textarea {{ min-height: 100px; resize: vertical; }}
        .form-submit {{ background: {theme_color}; color: white; border: none; padding: 12px; border-radius: 10px; font-weight: 600; cursor: pointer; transition: transform 0.2s; }}
        .form-submit:hover {{ transform: scale(1.02); }}
        .form-info {{ margin-top: 10px; font-size: 15px; color: {theme_styles['text']}; opacity: 1.0; text-align: center; font-weight: 600; }}
        .form-success {{ margin-top: 15px; padding: 15px; background: #d4edda; color: #155724; border-radius: 10px; text-align: center; }}
        .products-section {{ margin-top: 30px; }}
        .products-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 15px; }}
        .product-card {{ background: rgba(0,0,0,0.03); border-radius: 15px; padding: 15px; text-align: center; transition: transform 0.2s; }}
        body.dark-mode .product-card {{ background: rgba(255,255,255,0.05); }}
        .product-card:hover {{ transform: translateY(-3px); }}
        .product-image-wrapper {{ position: relative; cursor: pointer; overflow: hidden; border-radius: 10px; }}
        .product-image-wrapper:hover .zoom-icon {{ opacity: 1; }}
        .zoom-icon {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 30px; opacity: 0; transition: opacity 0.2s; pointer-events: none; background: rgba(0,0,0,0.5); border-radius: 50%; width: 50px; height: 50px; display: flex; align-items: center; justify-content: center; }}
        .product-image {{ width: 100%; height: 120px; object-fit: cover; border-radius: 10px; margin-bottom: 10px; }}
        .product-placeholder {{ width: 100%; height: 120px; background: rgba(0,0,0,0.05); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 48px; margin-bottom: 10px; }}
        .product-title {{ color: {theme_styles['text']}; font-size: 15px; margin-bottom: 5px; }}
        .product-desc {{ color: {theme_styles['text']}; opacity: 0.7; font-size: 12px; margin-bottom: 10px; min-height: 30px; }}
        .product-price {{ color: {theme_color}; font-size: 20px; font-weight: 700; margin-bottom: 10px; }}
        .product-btn {{ background: {theme_color}; color: white; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 13px; font-weight: 600; width: 100%; }}
                /* Кошик */
        .cart-icon {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: {theme_color};
            color: white;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            cursor: pointer;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            z-index: 10000;
            transition: transform 0.2s;
        }}
        .cart-icon:hover {{ transform: scale(1.1); }}
        .cart-count {{
            position: absolute;
            top: -5px;
            right: -5px;
            background: #ff6b6b;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            font-size: 14px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
                /* Lightbox для фото товару */
        .product-image-modal-content {{
            background: transparent !important;
            box-shadow: none !important;
            max-width: 90vw;
            padding: 20px;
        }}
        .product-image-modal-content img {{
            max-width: 100%;
            max-height: 80vh;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
        }}
        .cart-modal-content {{
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
        }}
        .cart-items {{
            margin: 20px 0;
            text-align: left;
        }}
        .cart-empty {{
            text-align: center;
            color: #999;
            padding: 20px;
        }}
        .cart-item {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #eee;
        }}
        .cart-item-info {{
            flex: 1;
        }}
        .cart-item-price {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        .cart-item-controls {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .cart-item-controls button {{
            background: #f0f0f0;
            border: none;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 16px;
            font-weight: 700;
        }}
        .cart-item-controls button:hover {{
            background: #e0e0e0;
        }}
        .cart-item-controls .remove-btn {{
            background: #ff6b6b;
            color: white;
        }}
                /* Форма замовлення */
        .checkout-modal-content {{
            max-width: 500px;
            max-height: 90vh;
            overflow-y: auto;
        }}
        .form-group {{
            margin-bottom: 15px;
            text-align: left;
        }}
        .form-group label {{
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }}
        .form-group .form-input {{
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }}
        .form-group .form-textarea {{
            min-height: 80px;
            resize: vertical;
        }}
        .cart-total {{
            text-align: right;
            font-size: 18px;
            padding: 15px;
            border-top: 2px solid #333;
            margin-top: 10px;
        }}
        .product-image-modal-content {{ background: transparent !important; box-shadow: none !important; max-width: 90vw; padding: 20px; }}
        .product-image-modal-content img {{ max-width: 100%; max-height: 80vh; border-radius: 10px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }}
    </style>
</head>
<body data-dark-mode="{str(dark_mode).lower()}">
    <div id="heatmap-container"></div>
    <button class="theme-toggle" id="themeToggle" onclick="toggleDarkMode()" aria-label="Перемкнути тему">🌙</button>
    <div class="container">
        <div class="avatar">{avatar_html}</div>
        <h1>{name}</h1>
        <p class="bio">{bio}</p>
        <div class="links" id="linksContainer">{links_html}</div>
        {extra_blocks}
    </div>
        <a href="https://share.streamlit.io/user/smartlink-ua" target="_blank" class="smartlink-badge">
        🚀 SmartLink
    </a>
    <div class="modal" id="paymentModal" role="dialog">
        <div class="modal-content">
            <div class="modal-icon">🔒</div>
            <h2 class="modal-title" id="modalTitle">Ексклюзивний контент</h2>
            <div class="modal-price" id="modalPrice">$0</div>
            <p class="modal-description">Цей контент доступний тільки після оплати.</p>
            <div class="payment-methods"><span>💳</span><span>🅿️</span><span>₿</span></div>
            <div class="modal-buttons">
                <button class="btn-pay" onclick="processPayment()">💰 Оплатити зараз</button>
                <button class="btn-cancel" onclick="closeModal()">Скасувати</button>
            </div>
        </div>
    </div>
    <div class="modal" id="productImageModal" onclick="closeProductImageModal()">
        <div class="modal-content product-image-modal-content" onclick="event.stopPropagation()">
            <span class="lightbox-close" onclick="closeProductImageModal()">&times;</span>
            <img id="productImageModalImg" src="" alt="">
            <h3 id="productImageModalTitle" style="margin-top: 15px; color: {theme_styles['text']};"></h3>
        </div>
    </div>
        
        <div class="pwa-banner" id="pwaBanner">
        <img src="{icon_data_uri}" class="pwa-banner-icon" alt="icon" loading="lazy">
        <div class="pwa-banner-text"><strong>Додати на головний екран</strong>Швидкий доступ до {name}</div>
        <button class="pwa-banner-btn" onclick="installPWA()">Додати</button>
        <button class="pwa-banner-close" onclick="closeBanner()">×</button>
    </div>
        <div class="stats-panel" id="statsPanel">
        <h3>📊 Статистика кліків</h3>
        <div class="stats-filters">
            <button class="filter-btn active" onclick="setPeriod('all')" data-period="all">Всі</button>
            <button class="filter-btn" onclick="setPeriod('month')" data-period="month">Місяць</button>
            <button class="filter-btn" onclick="setPeriod('week')" data-period="week">Тиждень</button>
            <button class="filter-btn" onclick="setPeriod('today')" data-period="today">Сьогодні</button>
        </div>
        <div id="statsContent"></div>
    </div>
    
    <script>
        let currentLink = null, currentProductLink = null, currentPeriod = 'all';
        let purchasedItems = JSON.parse(localStorage.getItem('purchasedItems') || '[]');
        let contactMessages = JSON.parse(localStorage.getItem('contactMessages') || '[]');
        let clickData = JSON.parse(localStorage.getItem('clickData') || '[]');
        let linkStats = JSON.parse(localStorage.getItem('linkStats') || '{{}}');

        document.addEventListener('DOMContentLoaded', function() {{
            purchasedItems.forEach(id => {{
                const link = document.getElementById(id);
                if (link && link.dataset.paid === 'true') {{ link.classList.add('unlocked'); link.querySelector('.lock-icon').textContent = '🔓'; }}
            }});
            if (document.body.dataset.darkMode === 'true') {{
                document.body.classList.add('dark-mode');
                document.getElementById('themeToggle').textContent = '☀️';
            }}
        }});

        function handleLinkClick(event, element) {{
            event.preventDefault();
            const isPaid = element.dataset.paid === 'true';
            if (isPaid && !element.classList.contains('unlocked')) {{
                currentLink = element;
                document.getElementById('modalTitle').textContent = element.dataset.title;
                document.getElementById('modalPrice').textContent = '$' + element.dataset.price;
                document.getElementById('paymentModal').classList.add('show');
            }} else {{ window.open(element.dataset.url, '_blank'); }}
            
            const linkId = element.id;
            if (!linkStats[linkId]) linkStats[linkId] = {{ title: element.dataset.title, count: 0 }};
            linkStats[linkId].count++;
            localStorage.setItem('linkStats', JSON.stringify(linkStats));
            
            heatmapInstance.addData({{ x: event.pageX, y: event.pageY, value: 1 }});
            clickData.push({{ x: event.pageX, y: event.pageY, time: new Date().toISOString(), linkId: linkId }});
            localStorage.setItem('clickData', JSON.stringify(clickData));
        }}

        function processPayment() {{
            if (currentLink) {{
                alert('✅ Оплата успішна! (це демо)');
                currentLink.classList.add('unlocked');
                currentLink.querySelector('.lock-icon').textContent = '🔓';
                purchasedItems.push(currentLink.id);
                localStorage.setItem('purchasedItems', JSON.stringify(purchasedItems));
                closeModal();
                setTimeout(() => window.open(currentLink.dataset.url, '_blank'), 500);
            }}
        }}
        function closeModal() {{ document.getElementById('paymentModal').classList.remove('show'); currentLink = null; }}
        function buyProduct(title, price, link) {{
            currentProductLink = link;
            document.getElementById('productModalTitle').textContent = title;
            document.getElementById('productModalPrice').textContent = '$' + price;
            document.getElementById('productModal').classList.add('show');
        }}
        function confirmProductPurchase() {{
            alert('✅ Дякуємо за покупку! (це демо)');
            closeProductModal();
            if (currentProductLink && currentProductLink !== '#') window.open(currentProductLink, '_blank');
        }}
        function closeProductModal() {{ document.getElementById('productModal').classList.remove('show'); currentProductLink = null; }}
        function closeProductImageModal() {{ document.getElementById('productImageModal').classList.remove('show'); }}
        function submitContactForm(event) {{
            event.preventDefault();
            const form = event.target;
            contactMessages.push({{ name: form.name.value, email: form.email.value, message: form.message.value, time: new Date().toISOString() }});
            localStorage.setItem('contactMessages', JSON.stringify(contactMessages));
            form.style.display = 'none';
            document.getElementById('form-success').style.display = 'block';
            setTimeout(() => {{ form.reset(); form.style.display = 'flex'; document.getElementById('form-success').style.display = 'none'; }}, 3000);
        }}
        let currentSlide = 0;
        function openLightbox(index) {{
            currentSlide = index;
            const slides = document.querySelectorAll('.lightbox-slide');
            slides.forEach((s, i) => s.classList.toggle('active', i === index));
            document.getElementById('lightbox').classList.add('show');
        }}
        function closeLightbox() {{ document.getElementById('lightbox').classList.remove('show'); }}
        let deferredPrompt;
        window.addEventListener('beforeinstallprompt', (e) => {{ e.preventDefault(); deferredPrompt = e; document.getElementById('pwaBanner').classList.add('show'); }});
        function installPWA() {{
            if (deferredPrompt) {{ deferredPrompt.prompt(); deferredPrompt.userChoice.then(() => {{ deferredPrompt = null; closeBanner(); }}); }}
            else {{ alert('📱 iOS: "Поділитися" → "На екран Домашнього"\\n📱 Android: меню ⋮ → "Встановити додаток"'); closeBanner(); }}
        }}
        function closeBanner() {{ document.getElementById('pwaBanner').classList.remove('show'); }}
        function toggleDarkMode() {{
            const body = document.body, btn = document.getElementById('themeToggle');
            if (body.classList.contains('dark-mode')) {{ body.classList.remove('dark-mode'); btn.textContent = '🌙'; localStorage.setItem('darkMode', 'false'); }}
            else {{ body.classList.add('dark-mode'); btn.textContent = '☀️'; localStorage.setItem('darkMode', 'true'); }}
        }}
         
                function toggleHeatmap() {{
            const container = document.getElementById('heatmap-container'), panel = document.getElementById('statsPanel');
            if (container.classList.contains('active')) {{
                container.classList.remove('active');
                panel.classList.remove('show');
            }} else {{
                container.classList.add('active');
                panel.classList.add('show');
                updateStats();
            }}
        }}
        function setPeriod(period) {{
            currentPeriod = period;
            document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.toggle('active', btn.dataset.period === period));
            updateStats();
        }}
        function filterDataByPeriod(data, period) {{
            if (period === 'all') return data;
            const now = new Date();
            let startDate;
            if (period === 'today') startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            else if (period === 'week') startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
            else if (period === 'month') startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
            return data.filter(item => new Date(item.time) >= startDate);
        }}
        function getPeriodLabel(period) {{ return {{'all': 'за весь час', 'today': 'сьогодні', 'week': 'за тиждень', 'month': 'за місяць'}}[period] || ''; }}
        function updateStats() {{
            const statsContent = document.getElementById('statsContent');
            let html = '', totalClicks = 0;
            const filteredClickData = filterDataByPeriod(clickData, currentPeriod);
            const periodLinkStats = {{}};
            filteredClickData.forEach(click => {{
                if (click.linkId) {{
                    if (!periodLinkStats[click.linkId]) periodLinkStats[click.linkId] = {{ title: linkStats[click.linkId]?.title || 'Невідомо', count: 0 }};
                    periodLinkStats[click.linkId].count++;
                }}
            }});
            const sortedStats = Object.entries(periodLinkStats).sort((a, b) => b[1].count - a[1].count);
            sortedStats.forEach(([linkId, stat]) => {{
                totalClicks += stat.count;
                html += '<div class="stat-item"><span>' + stat.title + '</span><strong>' + stat.count + ' кліків</strong></div>';
            }});
            if (html === '') html = '<p style="color: #999;">Поки немає кліків по посиланнях</p>';
            html += '<div style="margin-top: 15px; padding-top: 15px; border-top: 2px solid #eee;">';
            html += '<div class="period-info">📅 Статистика ' + getPeriodLabel(currentPeriod) + '</div>';
            html += '<div class="stat-item"><strong>Кліків по посиланнях:</strong><strong>' + totalClicks + '</strong></div>';
            html += '<div class="stat-item"><strong>Загальних кліків:</strong><strong>' + filteredClickData.length + '</strong></div>';
            html += '<div class="stat-item"><strong>Повідомлень:</strong><strong>' + contactMessages.length + '</strong></div>';
            html += '</div>';
            statsContent.innerHTML = html;
        }}
        function toggleFAQ(index) {{
            const item = document.querySelectorAll('.faq-item')[index];
            const button = item.querySelector('.faq-question');
            const isActive = item.classList.contains('active');
            document.querySelectorAll('.faq-item').forEach(i => {{ i.classList.remove('active'); i.querySelector('.faq-question').setAttribute('aria-expanded', 'false'); }});
            if (!isActive) {{ item.classList.add('active'); button.setAttribute('aria-expanded', 'true'); }}
        }}
        function updateCountdown() {{
            const countdown = document.getElementById('countdown');
            if (!countdown) return;
            const distance = new Date(countdown.dataset.target).getTime() - new Date().getTime();
            if (distance < 0) {{ countdown.innerHTML = '<h3 style="color: white; text-align: center;">🎉 Подія почалась!</h3>'; return; }}
            document.getElementById('days').textContent = String(Math.floor(distance / (1000 * 60 * 60 * 24))).padStart(2, '0');
            document.getElementById('hours').textContent = String(Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))).padStart(2, '0');
            document.getElementById('minutes').textContent = String(Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60))).padStart(2, '0');
            document.getElementById('seconds').textContent = String(Math.floor((distance % (1000 * 60)) / 1000)).padStart(2, '0');
        }}
        if (document.getElementById('countdown')) {{ updateCountdown(); setInterval(updateCountdown, 1000); }}
    </script>
</body>
</html>"""
# ============================================================================
# ПЕРЕВІРКА: Чи це публічне посилання користувача? (100% надійний варіант)
# ============================================================================
public_user_id = None
try:
    params = st.query_params
    val = params.get("user")
    public_user_id = val[0] if isinstance(val, list) and val else val
except Exception:
    try:
        val = st.experimental_get_query_params().get("user", [None])
        public_user_id = val[0] if val else None
    except Exception:
        pass

if public_user_id:
    st.set_page_config(page_title="SmartLink", layout="wide", page_icon="🔗")
    
    profile = db.load_profile(public_user_id)
    if not profile:
        st.error(f"❌ Цей сайт не знайдено або він видалений. (ID: {public_user_id})")
        st.stop()
    
    links = db.load_links(public_user_id) or []
    products = db.load_products(public_user_id) or []
    
    import json
    config = {}
    if profile.get('site_config'):
        try:
            # Перевіряємо тип даних: якщо це текст, парсимо. Якщо вже словник - беремо як є.
            if isinstance(profile['site_config'], str):
                config = json.loads(profile['site_config'])
            else:
                config = profile['site_config']
        except Exception as e:
            print(f"Помилка читання JSON: {e}")
            config = {}
        # 🔍 ФІНАЛЬНИЙ ДЕТЕКТОР: Показує, що РЕАЛЬНО прийшло з бази даних
    

    # УВАГА: Цей рядок має починатися з рівно 4 пробілів від початку рядка!
    html_content = generate_full_html(
        name=profile.get('name') or config.get('name', 'SmartLink'),
        bio=profile.get('bio') or config.get('bio', ''),
        avatar_image_data_uri=profile.get('avatar_url') or config.get('avatar_image_data_uri', ''),
        background_image_data_uri=profile.get('background_url') or config.get('background_image_data_uri', ''),
        links=links,
        theme_color=profile.get('theme_color') or config.get('theme_color', '#667eea'),
        theme_choice=profile.get('theme_choice') or config.get('theme_choice', 'gradient'),
        font_choice=profile.get('font_choice') or config.get('font_choice', 'Inter'),
        dark_mode=profile.get('dark_mode') or config.get('dark_mode', False),
        faq_items=config.get('faq_items', []),
        countdown_date=config.get('countdown_date', ''),
        countdown_title=config.get('countdown_title', 'До події залишилось'),
        custom_html=config.get('custom_html', ''),
        gif_url=config.get('gif_url', ''),
        gif_caption=config.get('gif_caption', ''),
        quote_text=config.get('quote_text', ''),
        quote_author=config.get('quote_author', ''),
        features=config.get('features', []),
        gallery_images=config.get('gallery_images', []),
        contact_title=config.get('contact_title', ''),
        contact_info=config.get('contact_info', ''),
        products=products,
        supabase_url=os.getenv('SUPABASE_URL', 'https://nwuijdpamsijypmviwra.supabase.co'),
        supabase_anon_key=os.getenv('SUPABASE_KEY', ''),
        profile_id=str(public_user_id)
    )
    
    st.markdown(
        """
        <style>
        /* Приховуємо ВСІ елементи Streamlit */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .stAppDeployButton {visibility: hidden;}
        .viewerBadge {visibility: hidden;}
        
        /* Основні відступи */
        .block-container { padding-top: 0rem; padding-bottom: 0rem; padding-left: 0rem; padding-right: 0rem; max-width: 100%; }
        .main .block-container { max-width: 100%; padding: 0; }
        iframe { border: none; width: 100vw; height: 100vh; }
        
        /* Додаткове приховування */
        .stDecoration {display: none;}
        header[data-testid="stHeader"] {display: none;}
                .smartlink-badge {
            position: fixed; bottom: 20px; left: 20px; 
            background: rgba(255, 255, 255, 0.15); backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white; text-decoration: none; padding: 8px 16px; border-radius: 30px;
            font-size: 13px; font-weight: 600; font-family: sans-serif;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s ease;
            z-index: 10000; display: flex; align-items: center; gap: 6px;
        }
        .smartlink-badge:hover { transform: translateY(-3px); background: rgba(255, 255, 255, 0.25); }
        body:not(.dark-mode) .smartlink-badge { 
            background: rgba(0, 0, 0, 0.05); color: #333; border-color: rgba(0,0,0,0.1); 
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.components.v1.html(html_content, height=1000, scrolling=True)
    st.stop()

# ============================================================================
# ОСНОВНИЙ ІНТЕРФЕЙС STREAMLIT
# ============================================================================

st.set_page_config(**PAGE_CONFIG)

# Перевіряємо, чи користувач увійшов у систему
if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if not st.session_state.user_id:
    st.title("🔐 Вхід у SmartLink")
    st.write("Ласкаво просимо! Увійдіть або зареєструйтеся, щоб почати.")
    
    tab_login, tab_register = st.tabs(["🔑 Вхід", "📝 Реєстрація"])
    
    with tab_login:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            submit = st.form_submit_button("Увійти")
            
            if submit:
                if email and password:
                    result = db.login_user(email, password)
                    if result['success']:
                        st.session_state.user_id = result['user_id']
                        st.success("✅ Вхід успішний!")
                        st.rerun()
                    else:
                        st.error(f"❌ Помилка: {result['error']}")
                else:
                    st.warning("⚠️ Заповніть всі поля!")
                    
    with tab_register:
        with st.form("register_form"):
            reg_name = st.text_input("Ваше ім'я або назва бренду")
            reg_email = st.text_input("Email")
            reg_password = st.text_input("Пароль (мінімум 6 символів)", type="password")
            reg_submit = st.form_submit_button("Зареєструватися")
            
            if reg_submit:
                if reg_name and reg_email and reg_password:
                    result = db.register_user(reg_email, reg_password, reg_name)
                    if result['success']:
                        st.session_state.user_id = result['user_id']
                        # Автоматично зберігаємо базовий профіль при реєстрації
                        db.save_profile(st.session_state.user_id, {'name': reg_name, 'telegram_chat_id': ''})
                        st.success("✅ Реєстрація успішна! Ласкаво просимо.")
                        st.rerun()
                    else:
                        st.error(f"❌ Помилка: {result['error']}")
                else:
                    st.warning("⚠️ Заповніть всі поля!")
    
    st.stop() # Зупиняємо виконання решти коду, якщо користувач не увійшов

# ============================================================================
# ЯКЩО КОРИСТУВАЧ УВІЙШОВ, ПОКАЗУЄМО ОСНОВНИЙ ІНТЕРФЕЙС
# ============================================================================

st.title("🚀 SmartLink")
st.subheader(f"Вітаємо! Ви увійшли як: {st.session_state.user_id[:8]}...")

# Кнопка виходу
if st.button("🚪 Вийти з акаунту"):
    db.logout_user()
    st.session_state.user_id = None
    st.rerun()

st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["📝 Створити сайт", "🧩 Блоки", "📊 Статистика", "💰 Монетизація"])

with tab1:
    st.header("📝 Заповни анкету")

        # --- БЛОК ТАРИФІВ ---
    plan_status = get_user_plan_status(st.session_state.user_id)
    
    col_plan1, col_plan2 = st.columns([3, 1])
    with col_plan1:
        st.info(f"**Ваш тариф:** {plan_status['name']}")
    with col_plan2:
        if not plan_status['is_pro']:
            if st.button("🚀 Спробувати Pro (14 днів)", use_container_width=True):
                if db.activate_pro_trial(st.session_state.user_id):
                    st.success("✅ Pro активовано!")
                    st.rerun()
                else:
                    st.error("Помилка активації")
    st.markdown("---")

    # --- Прогрес-бар ---
    progress_items = 0
    total_items = 5
    
    name = st.text_input("Твоє ім'я або назва бренду", 
                         value=st.session_state.get('name_value', ''),
                         placeholder="Наприклад: Іван Петренко",
                         key="name_input")
    if name: 
        st.session_state['name_value'] = name
        progress_items += 1

    col1, col2 = st.columns([3, 1])
    with col1:
        bio = st.text_area("Короткий опис про себе", 
                           value=st.session_state.get('bio_value', ''),
                           placeholder="Наприклад: Фрілансер-дизайнер з Києва.",
                           key="bio_input")
    with col2:
        st.write(""); st.write("")
        generate_button = st.button("🤖 AI опис", help="Автоматично згенерувати опис")
        if bio: 
         st.session_state['bio_value'] = bio
        progress_items += 1

    

    # 📱 ДОДАНО: Поле для Telegram Chat ID
    telegram_chat_id = st.text_input(
        "📱 Telegram Chat ID (для сповіщень про замовлення)", 
        value=st.session_state.get('telegram_chat_id_value', ''),
        placeholder="Наприклад: 811222873",
        help="Ваш ID у Telegram. Дізнатися можна у бота @userinfobot",
        key="telegram_chat_id_input_unique"  # <-- ДОДАНО ЦЕЙ РЯДОК
    )
    st.session_state['telegram_chat_id_value'] = telegram_chat_id
    if telegram_chat_id:
        progress_items += 1

    
    st.subheader("🖼️ Аватар")
    avatar_option = st.radio("Як додати аватар?", ["Завантажити файл", "Вставити посилання (URL)"], horizontal=True)
    
    if 'avatar_image_data_uri' not in st.session_state:
        st.session_state.avatar_image_data_uri = ''
    
    avatar_image_data_uri = st.session_state.avatar_image_data_uri
    
    if avatar_option == "Завантажити файл":
        uploaded_avatar = st.file_uploader("Оберіть зображення", type=['png', 'jpg', 'jpeg'], key="avatar_upload")
        if uploaded_avatar is not None:
            avatar_image_data_uri = image_to_data_uri(uploaded_avatar)
            st.session_state.avatar_image_data_uri = avatar_image_data_uri
            st.success("✅ Аватар завантажено!")
    else:
        saved_avatar = st.session_state.avatar_image_data_uri
        default_url = '' if (saved_avatar and saved_avatar.startswith('data:')) else saved_avatar
        avatar_url = st.text_input("Посилання на аватар", 
                                   value=default_url,
                                   placeholder="https://example.com/avatar.jpg")
        if avatar_url:
            avatar_image_data_uri = avatar_url
            st.session_state.avatar_image_data_uri = avatar_url
    
    # 🌟 ДОДАЄМО ПРЕВ'Ю, ЯКЩО ДАНІ Є В БАЗІ
    if st.session_state.avatar_image_data_uri:
        st.image(st.session_state.avatar_image_data_uri, width=100, caption="✅ Поточний аватар (збережено в базі)")
    
    if avatar_image_data_uri:
        progress_items += 1

    st.subheader("🎨 Обери стиль")
    col1, col2 = st.columns(2)
    with col1:
        theme_color = st.color_picker("Основний колір", 
                                      value=st.session_state.get('theme_color_value', '#667eea'),
                                      key="color_picker")
        st.session_state['theme_color_value'] = theme_color
    with col2:
        theme_choice = st.radio("Тема дизайну", list(THEMES.keys()), 
                                index=list(THEMES.keys()).index(st.session_state.get('theme_choice_value', 'gradient')) if st.session_state.get('theme_choice_value', 'gradient') in THEMES else 0,
                                format_func=lambda x: THEMES[x]['name'],
                                key="theme_radio")
        st.session_state['theme_choice_value'] = theme_choice
        
        # Прев'ю теми
        theme_data = THEMES[theme_choice]
        bg_style = theme_data['bg'](theme_color) if callable(theme_data['bg']) else theme_data['bg']
        container_bg = theme_data['container_bg']
        text_color = theme_data['text']
        link_bg = theme_data['link_bg'](theme_color) if callable(theme_data['link_bg']) else theme_data['link_bg']
        link_text = theme_data['link_text'](theme_color) if callable(theme_data['link_text']) else theme_data['link_text']
        border_radius = theme_data['border_radius']
        
        st.markdown(
            f"""
            <div style="padding: 20px; background: {bg_style}; border-radius: 15px; margin-top: 10px;">
                <div style="background: {container_bg}; border-radius: {border_radius}; padding: 20px; text-align: center;">
                    <div style="width: 50px; height: 50px; border-radius: 50%; background: {link_bg}; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center; font-size: 20px; color: {link_text}; font-weight: bold;">
                        {name[0].upper() if name else "M"}
                    </div>
                    <div style="color: {text_color}; font-size: 16px; font-weight: 600; margin-bottom: 5px;">{name if name else "Ваше ім'я"}</div>
                    <div style="color: {text_color}; font-size: 12px; opacity: 0.7; margin-bottom: 12px;">Короткий опис</div>
                    <div style="background: {link_bg}; color: {link_text}; padding: 8px; border-radius: {border_radius}; font-size: 12px; font-weight: 600; margin-bottom: 6px;">Instagram</div>
                    <div style="background: {link_bg}; color: {link_text}; padding: 8px; border-radius: {border_radius}; font-size: 12px; font-weight: 600;">Telegram</div>
                </div>
            </div>
            <div style="text-align: center; margin-top: 8px; font-size: 11px; color: #999;">👆 Прев'ю теми: <strong>{theme_data['name']}</strong></div>
            """,
            unsafe_allow_html=True
        )
    
    col3, col4 = st.columns(2)
    with col3:
        font_choice = st.selectbox("Шрифт", FONTS, 
                                   index=FONTS.index(st.session_state.get('font_choice_value', 'Inter')) if st.session_state.get('font_choice_value', 'Inter') in FONTS else 0,
                                   key="font_select")
        st.session_state['font_choice_value'] = font_choice
        
        # Прев'ю шрифту
        st.markdown(
            f"""
            <link href="https://fonts.googleapis.com/css2?family={font_choice.replace(' ', '+')}:wght@400;600;700&display=swap" rel="stylesheet">
            <div style="padding: 20px; background: linear-gradient(135deg, {theme_color}22 0%, {theme_color}11 100%); border-radius: 15px; border-left: 4px solid {theme_color}; margin-top: 10px;">
                <div style="font-family: '{font_choice}', sans-serif; font-size: 28px; font-weight: 700; margin-bottom: 8px; color: #333;">{name if name else "Ваше ім'я"}</div>
                <div style="font-family: '{font_choice}', sans-serif; font-size: 15px; line-height: 1.6; color: #555;">Це приклад того, як виглядатиме текст на вашому сайті.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col4:
        dark_mode = st.checkbox("🌙 Dark mode за замовчуванням", 
                                value=st.session_state.get('dark_mode_value', False),
                                key="dark_mode_check")
        st.session_state['dark_mode_value'] = dark_mode
    
        # Фонове зображення
    if 'background_image_data_uri' not in st.session_state:
        st.session_state.background_image_data_uri = ''
    
    background_image_data_uri = st.session_state.background_image_data_uri
    
    uploaded_file = st.file_uploader("Фонове зображення (необов'язково)", type=['png', 'jpg', 'jpeg'], key="bg_upload")
    if uploaded_file is not None:
        background_image_data_uri = image_to_data_uri(uploaded_file)
        st.session_state.background_image_data_uri = background_image_data_uri
        st.success("✅ Фонове зображення завантажено!")

    # 🌟 ДОДАЄМО ПРЕВ'Ю, ЯКЩО ДАНІ Є В БАЗІ
    if st.session_state.background_image_data_uri:
        st.image(st.session_state.background_image_data_uri, width=200, caption="✅ Поточний фон (збережено в базі)")
    if uploaded_file is not None:
        background_image_data_uri = image_to_data_uri(uploaded_file)
        st.session_state.background_image_data_uri = background_image_data_uri

    # Показуємо прогрес перед посиланнями
    progress_percent = progress_items / total_items
    st.progress(progress_percent, text=f"📊 Заповнено: {progress_items}/{total_items} полів")
    if progress_percent == 1.0:
        st.success("🎉 Чудово! Всі базові поля заповнені — можна генерувати сайт!")
    elif progress_percent >= 0.5:
        st.info("💪 Ще трохи — і ваш сайт готовий!")

    st.subheader("🔗 Додай свої посилання")
    st.info("💡 Можеш додати як безкоштовні, так і платні посилання")
    
    if 'links_list' not in st.session_state:
        st.session_state.links_list = []
        
    with st.form(key='add_link_form'):
        col1, col2 = st.columns(2)
        with col1: new_title = st.text_input("Назва посилання", placeholder="Мій курс")
        with col2: new_url = st.text_input("URL посилання", placeholder="https://example.com/course")
        col3, col4 = st.columns(2)
        with col3: is_paid = st.checkbox("💰 Платний контент")
        with col4: price = st.number_input("Ціна (USD)", min_value=0, value=0, step=1, disabled=not is_paid)
        submit_button = st.form_submit_button("➕ Додати посилання")
        if submit_button:
            current_plan = get_user_plan_status(st.session_state.user_id)
            if len(st.session_state.links_list) >= current_plan['links']:
                st.error(f"🔒 Ліміт тарифу {current_plan['name']}: максимум {current_plan['links']} посилань. Оновіть тариф!")
                st.stop()
            if new_title and new_url:
                st.session_state.links_list.append({"title": new_title, "url": new_url, "id": f"link_{len(st.session_state.links_list)}", "is_paid": is_paid, "price": price if is_paid else 0})
                st.success(f"✅ Додано: {new_title}")
                st.rerun()
            else:
                st.warning("⚠️ Заповни обидва поля!")
                
    if st.session_state.links_list:
        st.markdown("### 📋 Твої посилання:")
        for idx, link in enumerate(st.session_state.links_list):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                if link.get('is_paid'): st.write(f"💰 **{link['title']}** — ${link['price']}")
                else: st.write(f"**{link['title']}**")
                st.caption(link['url'])
            with col2: st.caption("💰 Платне" if link.get('is_paid') else "🆓 Безкоштовне")
            with col3: st.caption(f"#{idx + 1}")
            with col4:
                if st.button("🗑️", key=f"delete_{idx}"):
                    st.session_state.links_list.pop(idx)
                    st.rerun()
        st.markdown("---")

    if generate_button:
        if not st.session_state.links_list:
            st.warning("⚠️ Спочатку додай хоча б одне посилання!")
        else:
            generated_bio = generate_bio_from_links(st.session_state.links_list)
            st.success("✅ Опис згенеровано!")
            st.info(f"💡 **Згенерований опис:**\n\n{generated_bio}")
            st.session_state.generated_bio = generated_bio

    if st.button("✨ Згенерувати мій сайт", type="primary", key="generate_site_main"):
        if not name:
            st.error("Будь ласка, введи своє ім'я!")
        elif not st.session_state.links_list:
            st.error("Будь ласка, додай хоча б одне посилання!")
        else:
            with st.spinner("🚀 Публікуємо ваш сайт..."):
                # Зберігаємо все в базу даних
                save_config_to_supabase(st.session_state.user_id)
                
                final_bio = st.session_state.get('generated_bio', bio) if 'generated_bio' in st.session_state else bio
                
                # Генеруємо HTML для попереднього перегляду
                html_content = generate_full_html(
                    name=name, bio=final_bio, avatar_image_data_uri=avatar_image_data_uri,
                    links=st.session_state.links_list, theme_color=theme_color, theme_choice=theme_choice,
                    font_choice=font_choice, dark_mode=dark_mode, background_image_data_uri=background_image_data_uri,
                    faq_items=st.session_state.get('faq_items', []), countdown_date=st.session_state.get('countdown_date', ''),
                    countdown_title=st.session_state.get('countdown_title', 'До події залишилось'), custom_html=st.session_state.get('custom_html', ''),
                    gif_url=st.session_state.get('gif_url', ''), gif_caption=st.session_state.get('gif_caption', ''),
                    quote_text=st.session_state.get('quote_text', ''), quote_author=st.session_state.get('quote_author', ''),
                    features=st.session_state.get('features', []), gallery_images=st.session_state.get('gallery_images', []),
                    contact_title=st.session_state.get('contact_title', ''), contact_info=st.session_state.get('contact_info', ''),
                    products=st.session_state.get('products', []),
                    supabase_url=os.getenv('SUPABASE_URL', 'https://nwuijdpamsijypmviwra.supabase.co'),
                    supabase_anon_key=os.getenv('SUPABASE_KEY', ''),
                    profile_id=str(st.session_state.user_id)
                )
                
                # Формуємо справжнє публічне посилання
                # УВАГА: Якщо ваш додаток називається інакше, замініть 'smartlinks' на вашу реальну назву
                public_url = f"https://smartlinks.streamlit.app/?user={st.session_state.user_id}"
                
                st.balloons()
                st.success("✅ Ваш сайт успішно збережено та опубліковано в інтернеті!")
                
                st.markdown(f"""
                ### 🔗 Ваше публічне посилання:
                [{public_url}]({public_url})
                
                💡 *Скопіюйте це посилання та відкрийте його в новій вкладці (або на телефоні), щоб побачити, як ваш сайт виглядає для відвідувачів.*
                """)
                
                st.subheader("👀 Попередній перегляд:")
                st.components.v1.html(html_content, height=600, scrolling=True)

    # ========================================================================
    # ЕКСПОРТ / ІМПОРТ / ОЧИЩЕННЯ
    # ========================================================================
    st.markdown("---")
    st.subheader("💾 Збереження та завантаження")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📤 Експорт конфігурації**")
        st.caption("Збережіть усі налаштування у файл")
        config_json = export_config()
        st.download_button(
            label="📥 Завантажити конфігурацію (.json)",
            data=config_json,
            file_name=f"SmartLink_config_{name.replace(' ', '_') if name else 'project'}.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        st.markdown("**📥 Імпорт конфігурації**")
        st.caption("Завантажте раніше збережений файл")
        uploaded_config = st.file_uploader("Оберіть JSON файл", type=['json'], key="config_upload", label_visibility="collapsed")
        if uploaded_config is not None:
            try:
                json_content = uploaded_config.read().decode('utf-8')
                if import_config(json_content):
                    st.success("✅ Конфігурацію завантажено! Оновіть сторінку (F5)")
                    st.balloons()
            except Exception as e:
                st.error(f"❌ Помилка імпорту: {e}")

        st.markdown("---")
    col_c1, col_c2, col_c3 = st.columns([1, 2, 1])
    with col_c2:
        if st.button("🗑️ Очистити всі дані та почати знову", type="secondary", use_container_width=True, key="clear_all_btn"):
            # ⚠️ ВАЖЛИВО: Весь цей блок має бути з відступом всередині if st.button!
            if st.session_state.user_id:
                # Видаляємо дані з бази Supabase
                db.delete_profile(st.session_state.user_id)
                db.delete_links(st.session_state.user_id)
                db.delete_products(st.session_state.user_id)
                st.success("✅ Дані видалено з бази даних!")
            
            # Очищаємо локальні файли та сесію
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            
            st.session_state.clear()
            st.session_state.user_id = None
            st.session_state.config_loaded = False
            
            st.success("✅ Всі дані повністю очищено! Сторінка перезавантажиться...")
            st.rerun()

with tab2:
    st.header("🧩 Додаткові блоки")
    st.info("💡 Додайте додаткові блоки до вашого сайту")
    
    for key, default in [('faq_items', []), ('countdown_date', ''), ('countdown_title', 'До події залишилось'), ('custom_html', ''), ('gif_url', ''), ('gif_caption', ''), ('quote_text', ''), ('quote_author', ''), ('features', []), ('gallery_images', []), ('contact_title', ''), ('contact_info', ''), ('products', [])]:
        if key not in st.session_state: st.session_state[key] = default
    
    with st.expander("❓ FAQ (Часті питання)"):
        with st.form(key='faq_form'):
            col1, col2 = st.columns(2)
            with col1: faq_question = st.text_input("Питання")
            with col2: faq_answer = st.text_input("Відповідь")
            if st.form_submit_button("➕ Додати FAQ"):
                if faq_question and faq_answer:
                    st.session_state.faq_items.append({"question": faq_question, "answer": faq_answer})
                    st.rerun()
                else: st.warning("⚠️ Заповніть обидва поля!")
        if st.session_state.faq_items:
            for idx, item in enumerate(st.session_state.faq_items):
                col1, col2 = st.columns([4, 1])
                with col1: st.write(f"**{item['question']}**"); st.caption(item['answer'])
                with col2:
                    if st.button("🗑️", key=f"faq_del_{idx}"):
                        st.session_state.faq_items.pop(idx); st.rerun()
    
    with st.expander("⏰ Таймер зворотного відліку"):
        countdown_title = st.text_input("Заголовок таймера", value=st.session_state.countdown_title)
        st.session_state.countdown_title = countdown_title
        countdown_date = st.date_input("Дата події", value=None, min_value=datetime.now().date())
        countdown_time = st.time_input("Час", value=None)
        if countdown_date and countdown_time:
            dt = datetime.combine(countdown_date, countdown_time)
            st.session_state.countdown_date = dt.isoformat()
            st.success(f"✅ Таймер: {dt.strftime('%d.%m.%Y %H:%M')}")
        elif countdown_date:
            dt = datetime.combine(countdown_date, datetime.now().time())
            st.session_state.countdown_date = dt.isoformat()
            st.success(f"✅ Таймер: {dt.strftime('%d.%m.%Y')}")
    
    with st.expander("💬 Цитата"):
        quote_text = st.text_area("Текст цитати", value=st.session_state.quote_text, placeholder="Ваша натхненна цитата...")
        st.session_state.quote_text = quote_text
        quote_author = st.text_input("Автор (необов'язково)", value=st.session_state.quote_author, placeholder="Стів Джобс")
        st.session_state.quote_author = quote_author
    
    with st.expander("⭐ Переваги (картки)"):
        st.write("Додайте 3-4 переваги вашого продукту/послуги")
        with st.form(key='features_form'):
            col1, col2, col3 = st.columns(3)
            with col1: feat_icon = st.text_input("Іконка (емодзі)", value="✨", max_chars=2)
            with col2: feat_title = st.text_input("Назва", placeholder="Швидкість")
            with col3: feat_desc = st.text_input("Опис", placeholder="Блискавична робота")
            if st.form_submit_button("➕ Додати перевагу"):
                if feat_title and feat_desc:
                    st.session_state.features.append({"icon": feat_icon, "title": feat_title, "description": feat_desc})
                    st.rerun()
        if st.session_state.features:
            for idx, feat in enumerate(st.session_state.features):
                col1, col2 = st.columns([4, 1])
                with col1: st.write(f"{feat['icon']} **{feat['title']}** — {feat['description']}")
                with col2:
                    if st.button("🗑️", key=f"feat_del_{idx}"):
                        st.session_state.features.pop(idx); st.rerun()
    
    with st.expander("📸 Галерея зображень"):
        st.write("Додайте фотографії до галереї")
        current_plan = get_user_plan_status(st.session_state.user_id)
        
        # 1. Перевірка ліміту ПЕРЕД тим, як показувати форму
        if len(st.session_state.gallery_images) >= current_plan['gallery_limit'] and not current_plan['is_pro']:
            st.warning(f"🔒 Ліміт тарифу {current_plan['name']}: максимум {current_plan['gallery_limit']} фото в галереї. Оновіть тариф, щоб додати більше!")
        else:
            # 2. Форма додавання (об'єднана для зручності)
            gallery_option = st.radio("Як додати фото?", ["Завантажити файл", "Вставити посилання (URL)"], horizontal=True, key="gallery_option")
            with st.form(key='gallery_form'):
                if gallery_option == "Завантажити файл":
                    uploaded_gallery_img = st.file_uploader("Оберіть зображення", type=['png', 'jpg', 'jpeg', 'gif'], key="gallery_upload")
                    img_caption = st.text_input("Підпис (необов'язково)", key="cap_file")
                    img_url = ""
                else:
                    uploaded_gallery_img = None
                    img_url = st.text_input("URL зображення", placeholder="https://example.com/photo.jpg", key="gallery_url")
                    img_caption = st.text_input("Підпис (необов'язково)", key="cap_url")
                
                if st.form_submit_button("➕ Додати фото"):
                    if gallery_option == "Завантажити файл" and uploaded_gallery_img is not None:
                        st.session_state.gallery_images.append({"src": image_to_data_uri(uploaded_gallery_img), "caption": img_caption})
                        st.success("✅ Фото додано!")
                        st.rerun()
                    elif gallery_option == "Вставити посилання (URL)" and img_url:
                        st.session_state.gallery_images.append({"src": img_url, "caption": img_caption})
                        st.success("✅ Фото додано!")
                        st.rerun()
                    else:
                        st.warning("⚠️ Оберіть зображення або введіть URL!")
                        
        # 3. Відображення доданих фото
        if st.session_state.gallery_images:
            st.markdown("**Додані фото:**")
            for idx, img in enumerate(st.session_state.gallery_images):
                col1, col2 = st.columns([4, 1])
                with col1: 
                    st.image(img['src'], width=100, caption=img.get('caption', ''))
                with col2:
                    if st.button("🗑️", key=f"gal_del_{idx}"):
                        st.session_state.gallery_images.pop(idx)
                        st.rerun()    
    with st.expander("💬 Форма зворотного зв'язку"):
        contact_title = st.text_input("Заголовок форми", value=st.session_state.contact_title, placeholder="Зв'яжіться зі мною")
        st.session_state.contact_title = contact_title
        contact_info = st.text_input("Інформація для користувача", value=st.session_state.contact_info, placeholder="Відповім протягом 24 годин")
        st.session_state.contact_info = contact_info
        if contact_title: st.info("💡 Повідомлення зберігаються в localStorage браузера відвідувача")
    
    with st.expander("🛍️ Каталог товарів"):
        st.write("Додайте товари для продажу")
        product_img_option = st.radio("Як додати зображення товару?", ["Завантажити файл", "Вставити посилання (URL)", "Без зображення"], horizontal=True, key="product_img_option")
        with st.form(key='product_form'):
            col1, col2 = st.columns(2)
            with col1: prod_title = st.text_input("Назва товару")
            with col2: prod_price = st.number_input("Ціна (USD)", min_value=0, value=10, step=1)
            prod_desc = st.text_input("Опис (необов'язково)")
            prod_image = ""
            if product_img_option == "Завантажити файл":
                uploaded_prod_img = st.file_uploader("Оберіть зображення товару", type=['png', 'jpg', 'jpeg'], key="product_upload")
                if uploaded_prod_img is not None: prod_image = image_to_data_uri(uploaded_prod_img)
            elif product_img_option == "Вставити посилання (URL)":
                prod_image = st.text_input("URL зображення", placeholder="https://example.com/product.jpg")
            prod_link = st.text_input("Посилання для покупки (необов'язково)", placeholder="https://...")
            if st.form_submit_button("➕ Додати товар"):
                current_plan = get_user_plan_status(st.session_state.user_id)
                
                if not current_plan['is_pro'] and len(st.session_state.products) >= current_plan['products']:
                    st.error(f"🔒 Ліміт тарифу {current_plan['name']}: максимум {current_plan['products']} товарів.")
                elif prod_title:
                    st.session_state.products.append({"title": prod_title, "price": prod_price, "description": prod_desc, "image": prod_image, "buy_link": prod_link})
                    st.success(f"✅ Товар '{prod_title}' додано!")
                    st.rerun()
                else:
                    st.warning("⚠️ Введіть назву товару!")
        if st.session_state.products:
            st.markdown("**Додані товари:**")
            for idx, prod in enumerate(st.session_state.products):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{prod['title']}** — ${prod['price']}")
                    if prod.get('description'): st.caption(prod['description'])
                    if prod.get('image'): st.image(prod['image'], width=80)
                with col2:
                    if st.button("🗑️", key=f"prod_del_{idx}"):
                        st.session_state.products.pop(idx); st.rerun()
    
    with st.expander("💻 Власний HTML-код"):
        st.warning("⚠️ Будьте обережні!")
        custom_html = st.text_area("HTML код", value=st.session_state.custom_html, height=200)
        st.session_state.custom_html = custom_html
        if custom_html:
            st.markdown("**Прев'ю:**")
            st.components.v1.html(custom_html, height=200)
    
    with st.expander("🎞️ GIF анімація"):
        current_plan = get_user_plan_status(st.session_state.user_id)
        if not current_plan['has_gif']:
            st.warning("🔒 GIF-анімація доступна тільки на тарифі Pro. [Оновити тариф](#)")
        else:
            gif_url = st.text_input("URL GIF", value=st.session_state.gif_url, placeholder="https://media.giphy.com/...")
            st.session_state.gif_url = gif_url
            gif_caption = st.text_input("Підпис", value=st.session_state.gif_caption)
            st.session_state.gif_caption = gif_caption
            if gif_url: 
                st.image(gif_url, caption=gif_caption)
with tab3:
    st.header("📊 Статистика (демо)")
    st.info("💡 Статистика зберігається в браузері користувача.")
    demo_data = {"Instagram": 45, "Telegram": 32, "TikTok": 28, "YouTube": 15, "Сайт": 8}
    for link, clicks in demo_data.items():
        st.metric(label=link, value=f"{clicks} кліків")

with tab4:
    st.header("💰 Монетизація")
    st.info("💡 Імітація платного контенту")
    st.subheader("🎯 Як це працює:")
    st.markdown("""
    1. **Додай платне посилання** — познач чекбокс "💰 Платний контент"
    2. **На сайті** — золотий колір з 🔒
    3. **При кліку** — модальне вікно оплати
    4. **Після "оплати"** — зелений колір з 🔓
    5. **Збереження** — в localStorage
    """)

st.markdown("---")
st.markdown("Створено з ❤️ за допомогою Streamlit")