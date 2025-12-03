import re
from datetime import datetime


def clean_amount(text: str) -> float:
    try:
        text = re.sub(r'\s+', '', text)

        clean = re.sub(r'[^\d.,]', '', text)
        if not clean:
            return 0.0

        if ',' in clean and '.' in clean:
            if clean.find(',') < clean.find('.'):
                clean = clean.replace(',', '')
            else:
                clean = clean.replace('.', '').replace(',', '.')
        elif ',' in clean:
            parts = clean.split(',')
            if len(parts) > 1 and len(parts[-1]) == 2:
                clean = clean.replace(',', '.')
            else:
                clean = clean.replace(',', '')

        return float(clean)
    except Exception:
        return 0.0


def find_total_amount(text):
    text_lower = text.lower()
    keyword_pattern = (r'(?:total|sum|amount|due|balance|всього|сума|разом)'
                       r'.{0,150}?(\d{1,3}(?:[.,\s]\d{3})*(?:[.,]\d{2}))')

    matches = re.finditer(keyword_pattern, text_lower, re.DOTALL)

    candidates = []
    for m in matches:
        captured_span = m.group(0)

        if "cash" in captured_span or "change" in captured_span or "tender" in captured_span:
            continue

        val = clean_amount(m.group(1))
        if 0.0 < val < 1000000:
            candidates.append(val)

    if candidates:
        return max(candidates)

    money_pattern = r'\b\d{1,3}(?:[.,\s]\d{3})*(?:[.,]\d{2})\b'
    all_price_matches = re.finditer(money_pattern, text_lower)

    valid_prices = []
    for m in all_price_matches:
        val = clean_amount(m.group(0))
        if val <= 0.0 or val > 1000000:
            continue

        start_idx = max(0, m.start() - 20)
        context_before = text_lower[start_idx:m.start()]

        if any(bad in context_before for bad in ["cash", "change", "tel", "phone"]):
            continue

        valid_prices.append(val)

    if valid_prices:
        return max(valid_prices)

    return 0.0


def try_parse_date(date_str):
    if not date_str:
        return None

    norm_date = date_str.replace('.', '-').replace('/', '-').replace(' ', '-').strip()

    formats = [
        "%d-%m-%Y",
        "%d-%m-%y",
        "%Y-%m-%d",
        "%y-%m-%d",
        "%d-%b-%Y",
        "%d-%B-%Y",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(norm_date, fmt)
            current_year = datetime.now().year
            if 2010 <= dt.year <= current_year + 1:
                return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def clean_date(text):
    patterns = [
        r'(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})',
        r'(\d{4}[./-]\d{1,2}[./-]\d{1,2})',
    ]
    for p in patterns:
        match = re.search(p, text)
        if match:
            parsed = try_parse_date(match.group(1))
            if parsed:
                return parsed
    return None


def find_date_in_text(text):
    patterns = [
        r'\b(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})\b',
        r'\b(\d{4}[./-]\d{1,2}[./-]\d{1,2})\b',
        r'\b(\d{1,2}\s(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s\d{2,4})\b'
    ]
    for p in patterns:
        matches = re.findall(p, text, re.IGNORECASE)
        for m in matches:
            parsed = try_parse_date(m)
            if parsed:
                return parsed
    return None
