"""
Text extraction and cleaning utilities.
"""

import re
from typing import Optional
from bs4 import BeautifulSoup, Tag, NavigableString


def extract_text(element: Tag, strip: bool = True) -> str:
    """
    Extract text content from a BeautifulSoup element.
    
    Args:
        element: BeautifulSoup element
        strip: Whether to strip whitespace
    
    Returns:
        Extracted text
    """
    if element is None:
        return ""
    
    text = element.get_text(separator=" ", strip=strip)
    return clean_text(text) if strip else text


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and normalizing.
    
    Args:
        text: Raw text to clean
    
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Replace multiple whitespace with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading/trailing whitespace
    text = text.strip()
    return text


def remove_script_and_style(soup: BeautifulSoup) -> BeautifulSoup:
    """
    Remove script and style elements from soup.
    
    Args:
        soup: BeautifulSoup object
    
    Returns:
        Modified soup (mutated in place, but returned for convenience)
    """
    for script in soup(["script", "style", "noscript"]):
        script.decompose()
    return soup


def extract_main_content(soup: BeautifulSoup, selectors: Optional[list] = None) -> Optional[Tag]:
    """
    Extract main content area from HTML, removing navigation, headers, footers.
    
    Args:
        soup: BeautifulSoup object
        selectors: List of CSS selectors to try for main content
    
    Returns:
        Main content element or None
    """
    if selectors:
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element
    
    # Fallback: try common content selectors
    common_selectors = [
        "main",
        "article",
        ".content",
        "#content",
        ".main-content",
        "#main-content",
        ".post",
        ".entry"
    ]
    
    for selector in common_selectors:
        element = soup.select_one(selector)
        if element:
            return element
    
    # If nothing found, return body
    return soup.find("body")


def find_links_by_keywords(soup: BeautifulSoup, keywords: list) -> list[dict]:
    """
    Find links containing specific keywords.
    
    Args:
        soup: BeautifulSoup object
        keywords: List of keywords to search for
    
    Returns:
        List of dicts with 'url' and 'text' keys
    """
    links = []
    for link in soup.find_all("a", href=True):
        link_text = extract_text(link, strip=True).lower()
        href = link.get("href", "")
        
        for keyword in keywords:
            if keyword.lower() in link_text or keyword.lower() in href.lower():
                links.append({
                    "url": href,
                    "text": extract_text(link, strip=True)
                })
                break
    
    return links


def find_text_by_keywords(soup: BeautifulSoup, keywords: list, context_length: int = 100) -> list[dict]:
    """
    Find text containing specific keywords with context.
    
    Args:
        soup: BeautifulSoup object
        keywords: List of keywords to search for
        context_length: Number of characters of context to include
    
    Returns:
        List of dicts with 'text' and 'keyword' keys
    """
    results = []
    text_content = soup.get_text()
    
    for keyword in keywords:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        matches = pattern.finditer(text_content)
        
        for match in matches:
            start = max(0, match.start() - context_length)
            end = min(len(text_content), match.end() + context_length)
            context = text_content[start:end].strip()
            
            results.append({
                "keyword": keyword,
                "text": context
            })
    
    return results

