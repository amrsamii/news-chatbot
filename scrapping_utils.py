from typing import List

import requests
from bs4 import BeautifulSoup


def fetch_articles(url: str, category: str, article_selector: str, paragraph_selector: str) -> List[str]:
    """
    Fetch articles from a given URL using specified selectors for articles and paragraphs.

    Args:
    ----
        url: The URL to fetch articles from.
        category: The category to search for.
        article_selector: The CSS selector to find article links.
        paragraph_selector: The CSS selector to find article paragraphs.

    Returns:
    -------
        A list of articles with their content.

    """
    returned_articles = []
    seen = set()

    try:
        response = requests.get(f"{url}/{category}")
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.select(article_selector, limit=10)

        for article in articles:
            article_url = article["href"]
            if article_url in seen:
                continue
            seen.add(article_url)
            if not article_url.startswith("http"):
                article_url = f"{url}{article_url}"
            article_content = fetch_article_content(article_url, paragraph_selector)
            returned_articles.append(article_content)

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

    return returned_articles


def fetch_article_content(article_url: str, paragraph_selector: str) -> str:
    """
    Fetch the content of a single article.

    Args:
    ----
        article_url: The URL of the article.
        paragraph_selector: The CSS selector to find article paragraphs.

    Returns:
    -------
        The content of the article as a string.

    """
    try:
        article_response = requests.get(article_url)
        article_response.raise_for_status()
        article_soup = BeautifulSoup(article_response.text, "html.parser")
        paragraphs = article_soup.select(paragraph_selector)
        return "\n".join(paragraph.get_text() for paragraph in paragraphs)
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return ""
