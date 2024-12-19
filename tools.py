from typing import List

from scrapping_utils import fetch_articles


def search_bbc(category: str) -> List[str]:
    """
    Search for a category on bbc.com and returns the first 10 articles.

    Args:
    ----
        category: The category to search for.

    Returns:
    -------
        A list of the first 10 articles.

    """
    url = "https://www.bbc.com"
    article_selector = 'a[class*="/article/"], a[href*="/articles/"]'
    paragraph_selector = 'div[data-component="text-block"] p'
    return fetch_articles(url, category, article_selector, paragraph_selector)


def search_guardian(category: str) -> List[str]:
    """
    Search for a category on theguardian.com and returns the first 10 articles.

    Args:
    ----
        category: The category to search for.

    Returns:
    -------
        A list of the first 10 articles.

    """
    url = "https://www.theguardian.com"
    article_selector = 'a[class="dcr-ezvrjj"]'
    paragraph_selector = 'p[class="dcr-s3ycb2"]'
    return fetch_articles(url, category, article_selector, paragraph_selector)
