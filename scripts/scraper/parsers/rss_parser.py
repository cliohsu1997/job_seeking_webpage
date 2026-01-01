"""
RSS/XML feed parser for job listings.
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from datetime import datetime


def parse_rss_feed(xml_content: str) -> List[Dict[str, any]]:
    """
    Parse RSS feed XML and extract job listings.
    
    Args:
        xml_content: RSS/XML feed content as string
    
    Returns:
        List of job listing dicts
    """
    try:
        root = ET.fromstring(xml_content)
        items = []
        
        # Handle RSS 2.0 format
        for item in root.findall(".//item"):
            listing = {}
            
            # Extract common RSS fields
            title = item.find("title")
            if title is not None:
                listing["title"] = title.text or ""
            
            link = item.find("link")
            if link is not None:
                listing["url"] = link.text or ""
            
            description = item.find("description")
            if description is not None:
                listing["description"] = description.text or ""
            
            pub_date = item.find("pubDate")
            if pub_date is not None:
                listing["published_date"] = pub_date.text or ""
            
            # Extract any additional fields
            for child in item:
                tag = child.tag
                if tag not in ["title", "link", "description", "pubDate"]:
                    listing[tag] = child.text or ""
            
            if listing:
                items.append(listing)
        
        return items
    
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse RSS/XML feed: {e}")


def parse_atom_feed(xml_content: str) -> List[Dict[str, any]]:
    """
    Parse Atom feed XML and extract job listings.
    
    Args:
        xml_content: Atom XML feed content as string
    
    Returns:
        List of job listing dicts
    """
    try:
        root = ET.fromstring(xml_content)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        items = []
        
        for entry in root.findall(".//atom:entry", namespace):
            listing = {}
            
            title = entry.find("atom:title", namespace)
            if title is not None:
                listing["title"] = title.text or ""
            
            link = entry.find("atom:link", namespace)
            if link is not None:
                listing["url"] = link.get("href", "")
            
            summary = entry.find("atom:summary", namespace)
            if summary is not None:
                listing["description"] = summary.text or ""
            
            published = entry.find("atom:published", namespace)
            if published is not None:
                listing["published_date"] = published.text or ""
            
            if listing:
                items.append(listing)
        
        return items
    
    except ET.ParseError as e:
        raise ValueError(f"Failed to parse Atom feed: {e}")


def detect_feed_type(xml_content: str) -> Optional[str]:
    """
    Detect the type of XML feed (RSS or Atom).
    
    Args:
        xml_content: XML feed content as string
    
    Returns:
        'rss', 'atom', or None if unknown
    """
    try:
        root = ET.fromstring(xml_content)
        tag = root.tag.lower()
        
        if "rss" in tag:
            return "rss"
        elif "feed" in tag:
            return "atom"
        else:
            return None
    except ET.ParseError:
        return None


def parse_feed(xml_content: str) -> List[Dict[str, any]]:
    """
    Parse RSS or Atom feed automatically.
    
    Args:
        xml_content: XML feed content as string
    
    Returns:
        List of job listing dicts
    """
    feed_type = detect_feed_type(xml_content)
    
    if feed_type == "rss":
        return parse_rss_feed(xml_content)
    elif feed_type == "atom":
        return parse_atom_feed(xml_content)
    else:
        # Try RSS first as fallback
        try:
            return parse_rss_feed(xml_content)
        except ValueError:
            try:
                return parse_atom_feed(xml_content)
            except ValueError:
                raise ValueError("Unable to parse feed as RSS or Atom")

