import logging
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)

if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)


def get_ai_advice(comparison_data, transactions_list):
    if not settings.GOOGLE_API_KEY:
        logger.error("GOOGLE_API_KEY is not configured in settings.")
        return "AI service is not configured."

    logger.info(f"Preparing AI prompt with {len(transactions_list)} transactions...")

    trends_lines = []
    for cat, data in comparison_data.items():
        curr = data['current']
        prev = data['previous']
        diff = data['diff_percent']
        sign = "+" if diff > 0 else ""
        trends_lines.append(f"- Category '{cat}': {curr} (prev: {prev}, change: {sign}{diff:.1f}%)")

    trends_block = "\n".join(trends_lines)

    details_lines = []
    for t in transactions_list[:150]:
        date = t.get('date', 'N/A')
        amount = t.get('amount', 0)
        cat = t.get('category_name', 'Other')
        desc = t.get('description', '')
        details_lines.append(f"[{date}] {amount} ({cat}): {desc}")

    details_block = "\n".join(details_lines)

    prompt = f"""
    You are a professional financial advisor. Analyze the user's expenses for the last 30 days.

    ### 1. GENERAL TRENDS (Current vs Previous Month):
    {trends_block}

    ### 2. DETAILED TRANSACTION LOG (Recent):
    {details_block}

    ### YOUR TASK:
    1. Analyze the **Trends**: Identify where spending has increased significantly.
    2. Analyze the **Transaction Log**: Look for specific patterns,
    recurring unnecessary expenses (e.g., daily coffee, subscriptions, impulse buys).
    3. Provide **3 specific, actionable, and constructive tips** on how to save money based on data.

    Do not use generic advice like "make a budget". Be specific, e.g.,
    "You spent 500 on coffee, try brewing at home."
    Response must be in **English**. Keep it friendly but professional.
    """

    try:
        logger.info("Sending request to Gemini model...")
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)

        logger.info("Received response from AI successfully.")
        return response.text

    except Exception as e:
        logger.error(f"Failed to generate AI advice: {e}", exc_info=True)
        return None
