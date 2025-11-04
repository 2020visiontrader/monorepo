"""
Competitor site parser (heuristic)
"""
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Optional


def parse_competitor_site(base_url: str, max_pages: int = 10) -> tuple[Dict, List[Dict]]:
    """
    Heuristic parser for competitor sites.
    Prefers sitemap.xml; falls back to shallow nav crawl.
    """
    parsed_url = urlparse(base_url)
    base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    # Try sitemap first
    sitemap_url = urljoin(base_url, '/sitemap.xml')
    pages = []
    navigation = []
    sections = []
    taxonomy = {}
    
    try:
        response = httpx.get(sitemap_url, timeout=10, follow_redirects=True)
        if response.status_code == 200:
            # Parse sitemap (simplified - would need proper XML parsing)
            soup = BeautifulSoup(response.text, 'xml')
            urls = [loc.text for loc in soup.find_all('loc')][:max_pages]
        else:
            urls = crawl_navigation(base_url, max_pages)
    except:
        urls = crawl_navigation(base_url, max_pages)
    
    # Crawl pages
    for url in urls[:max_pages]:
        try:
            page_data = parse_page(url)
            if page_data:
                pages.append(page_data)
                if page_data['page_type'] == 'homepage':
                    navigation = extract_navigation(page_data['soup'])
                    sections = extract_sections(page_data['soup'])
        except Exception as e:
            continue
    
    ia_data = {
        'navigation': navigation,
        'sections': sections,
        'taxonomy': taxonomy,
    }
    
    return ia_data, pages


def crawl_navigation(base_url: str, max_pages: int) -> List[str]:
    """Shallow navigation crawl (depth <= 2)"""
    visited = set()
    to_visit = [(base_url, 0)]
    urls = []
    
    while to_visit and len(urls) < max_pages:
        url, depth = to_visit.pop(0)
        if url in visited or depth > 2:
            continue
        
        visited.add(url)
        urls.append(url)
        
        try:
            response = httpx.get(url, timeout=10, follow_redirects=True)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find navigation links
            for link in soup.find_all('a', href=True)[:10]:
                href = link.get('href')
                absolute_url = urljoin(base_url, href)
                if urlparse(absolute_url).netloc == urlparse(base_url).netloc:
                    if absolute_url not in visited:
                        to_visit.append((absolute_url, depth + 1))
        except:
            continue
    
    return urls


def parse_page(url: str) -> Optional[Dict]:
    """Parse a single page"""
    try:
        response = httpx.get(url, timeout=10, follow_redirects=True)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        title = soup.find('title')
        title_text = title.text if title else ''
        
        # Determine page type
        page_type = 'other'
        if url.rstrip('/') == urlparse(url).scheme + '://' + urlparse(url).netloc:
            page_type = 'homepage'
        elif 'product' in url.lower() or 'item' in url.lower():
            page_type = 'product'
        elif 'category' in url.lower() or 'collection' in url.lower():
            page_type = 'category'
        
        # Extract text
        extracted_text = soup.get_text(separator=' ', strip=True)[:5000]
        
        # Extract metadata
        h1 = soup.find('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        
        metadata = {
            'h1': h1.text if h1 else '',
            'h2': [h.text for h in h2_tags[:5]],
            'h3': [h.text for h in h3_tags[:5]],
            'meta_description': meta_desc.get('content', '') if meta_desc else '',
        }
        
        return {
            'url': url,
            'title': title_text,
            'page_type': page_type,
            'depth': url.count('/') - 2,
            'raw_html': str(soup)[:50000],  # Limit size
            'extracted_text': extracted_text,
            'metadata': metadata,
            'soup': soup,
        }
    except Exception as e:
        return None


def extract_navigation(soup: BeautifulSoup) -> List[Dict]:
    """Extract navigation structure"""
    nav_items = []
    nav = soup.find('nav') or soup.find('ul', class_=lambda x: x and 'nav' in x.lower())
    if nav:
        for link in nav.find_all('a', href=True)[:10]:
            nav_items.append({
                'label': link.text.strip(),
                'url': link.get('href'),
            })
    return nav_items


def extract_sections(soup: BeautifulSoup) -> List[Dict]:
    """Extract page sections"""
    sections = []
    for section in soup.find_all(['section', 'div'], class_=lambda x: x and 'section' in str(x).lower())[:10]:
        title = section.find(['h1', 'h2', 'h3'])
        sections.append({
            'type': 'generic',
            'title': title.text if title else '',
            'content_sample': section.get_text()[:200],
        })
    return sections

