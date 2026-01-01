"""
HTML parsing utilities using BeautifulSoup.
Supports both class-based and pattern-based extraction.
"""

from typing import Optional, Dict, List, Any
from bs4 import BeautifulSoup
from .text_extractor import extract_text, clean_text, remove_script_and_style, extract_main_content
from .date_parser import extract_deadline


class HTMLParser:
    """HTML parser with support for class-based and pattern-based extraction."""
    
    def __init__(self, html: str, parser: str = "lxml"):
        """
        Initialize HTML parser.
        
        Args:
            html: HTML content as string
            parser: Parser to use ('lxml', 'html.parser', etc.)
        """
        self.soup = BeautifulSoup(html, parser)
        remove_script_and_style(self.soup)
    
    def select_one(self, selector: str) -> Optional[str]:
        """
        Select single element by CSS selector and return text.
        
        Args:
            selector: CSS selector
        
        Returns:
            Text content or None
        """
        element = self.soup.select_one(selector)
        return extract_text(element) if element else None
    
    def select_all(self, selector: str) -> List[str]:
        """
        Select all elements by CSS selector and return text list.
        
        Args:
            selector: CSS selector
        
        Returns:
            List of text content
        """
        elements = self.soup.select(selector)
        return [extract_text(element) for element in elements]
    
    def find_by_class(self, class_name: str, tag: Optional[str] = None) -> List[str]:
        """
        Find elements by class name.
        
        Args:
            class_name: CSS class name
            tag: Optional HTML tag name
        
        Returns:
            List of text content
        """
        if tag:
            elements = self.soup.find_all(tag, class_=class_name)
        else:
            elements = self.soup.find_all(class_=class_name)
        return [extract_text(element) for element in elements]
    
    def extract_links(self, keywords: Optional[List[str]] = None) -> List[Dict[str, str]]:
        """
        Extract links from HTML, optionally filtering by keywords.
        
        Args:
            keywords: Optional list of keywords to filter links
        
        Returns:
            List of dicts with 'url' and 'text' keys
        """
        links = []
        for link in self.soup.find_all("a", href=True):
            href = link.get("href", "")
            text = extract_text(link)
            
            if keywords:
                link_lower = (text + " " + href).lower()
                if any(keyword.lower() in link_lower for keyword in keywords):
                    links.append({"url": href, "text": text})
            else:
                links.append({"url": href, "text": text})
        
        return links
    
    def extract_deadline(self, text: Optional[str] = None, keywords: Optional[List[str]] = None) -> Optional[str]:
        """
        Extract deadline from HTML content.
        
        Args:
            text: Optional text to search (if None, uses full HTML text)
            keywords: Optional keywords to search for
        
        Returns:
            Parsed date in YYYY-MM-DD format or None
        """
        if text is None:
            text = self.soup.get_text()
        
        return extract_deadline(text, keywords)
    
    def get_main_content(self, selectors: Optional[List[str]] = None) -> Optional[str]:
        """
        Extract main content area.
        
        Args:
            selectors: Optional list of CSS selectors to try
        
        Returns:
            Main content text or None
        """
        content_element = extract_main_content(self.soup, selectors)
        return extract_text(content_element) if content_element else None
    
    def get_full_text(self) -> str:
        """Get full text content from HTML."""
        return clean_text(self.soup.get_text())
    
    def get_soup(self) -> BeautifulSoup:
        """Get the underlying BeautifulSoup object for advanced operations."""
        return self.soup

