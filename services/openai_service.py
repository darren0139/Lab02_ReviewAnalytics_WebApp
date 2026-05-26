"""
services/openai_service.py

Infrastructure/API layer.
Handles OpenAI client setup, prompt instructions, response parsing,
rating extraction, and category classification.
"""

from openai import OpenAI

from config import OPENAI_API_KEY


client = OpenAI(api_key=OPENAI_API_KEY)


def classify_rating(rating: int) -> str:
    """
    helper to convert a numerical rating into a sentiment category.

    Good    = 8 to 10
    Average = 4 to 7
    Bad     = 0 to 3
    """

    if 8 <= rating <= 10:
        return "Good"

    if 4 <= rating <= 7:
        return "Average"

    return "Bad"


def extract_rating(raw_output: str) -> tuple[str, int]:
    """
    Extract the FINAL_RATING value from the model output.

    Returns:
        clean_summary: The summary without the FINAL_RATING line.
        rating: Integer rating from 0 to 10.
    """

    rating = 5
    clean_summary = raw_output

    if "FINAL_RATING:" in raw_output:
        parts = raw_output.split("FINAL_RATING:")
        clean_summary = parts[0].strip()

        try:
            rating_text = "".join(filter(str.isdigit, parts[1]))
            rating = int(rating_text)
        except ValueError:
            rating = 5

    rating = max(0, min(10, rating))

    return clean_summary, rating

def analyze_review_sentiment(review_content: str, model_name: str) -> tuple[str, int, str]:
    """
    analyze customer review text using OpenAI.

    Args:
        review_content: Text content from the uploaded review file.

    Returns:
        clean_summary: AI-generated review summary.
        rating: Numerical score from 0 to 10.
        category: Good, Average, or Bad.
    """

    system_prompt = """
You are a database-integrated text processing utility.

Analyze the user review text.

You MUST output your response in this exact structure:

1. A bulleted summary synthesized from the reviews.
2. A standalone final line exactly like this:
FINAL_RATING: X

Where X is an integer score from 0 to 10.

Rating guide:
- 8 to 10 = Good
- 4 to 7 = Average
- 0 to 3 = Bad

Keep your response analytical and professional.
"""

    response = client.responses.create(
        model= model_name,
        instructions=system_prompt,
        input=review_content,
    )

    raw_output = response.output_text

    clean_summary, rating = extract_rating(raw_output)
    category = classify_rating(rating)

    return clean_summary, rating, category