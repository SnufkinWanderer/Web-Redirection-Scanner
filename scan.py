import re
import time
import random
import requests
from urllib.parse import urljoin, urlencode
from bs4 import BeautifulSoup

TARGET_DOMAIN = "https://www.ovh.com"
EXTERNAL_URL = "https://evil.com"
visited_urls = set()
max_retries = 5
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

REDIRECT_PARAMS = [
    "url", "redirect", "next", "return", "to", "continue", "redirect_uri", "target", 
    "destination", "goto", "next_url", "post_login_redirect", "continue_url", 
    "after_login", "forward_to", "landing", "next_page", "path", "jump", 
    "ref", "redir", "callback", "referred_by", "from", "link", "return"
]

session = requests.Session()

def get_random_user_agent():
    """Retourne un user-agent aléatoire pour chaque requête."""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
    ]
    return random.choice(user_agents)

def request_with_retry(url, retries=5, backoff_factor=2):
    """Effectue une requête avec une gestion des erreurs 429 (Too Many Requests)."""
    attempt = 0
    while attempt < retries:
        try:
            response = session.get(url, timeout=5, headers={'User-Agent': get_random_user_agent()})
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After')
                if retry_after:
                    wait_time = int(retry_after)
                else:
                    wait_time = backoff_factor * (2 ** attempt)
                print(f"[⚠️ 429 erreur] Attente de {wait_time} secondes avant de réessayer...")
                time.sleep(wait_time)
                attempt += 1
            else:
                return response
        except requests.exceptions.RequestException as e:
            print(f"[❌ Erreur de requête] {e}")
            break
    return None

def get_all_links(url):
    """Récupère tous les liens internes d'une page"""
    try:
        response = request_with_retry(url)
        if not response:
            return []
        soup = BeautifulSoup(response.text, "html.parser")
        links = [a['href'] for a in soup.find_all('a', href=True)]
        return links
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du chargement de {url}: {e}")
        return []

def get_js_redirects(url):
    """Recherche les redirections JavaScript sur une page"""
    try:
        response = request_with_retry(url)
        if not response:
            return []
        js_redirects = []
        # Recherche de redirections dans le JavaScript
        regex = r"(window\.location\.href|location\.replace)\s*\(\s*['\"]([^'\"]+)['\"]"
        matches = re.findall(regex, response.text)
        for match in matches:
            js_redirects.append(match[1])
        return js_redirects
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'analyse du JavaScript sur {url}: {e}")
        return []

def is_open_redirect(test_url):
    """Vérifie si un URL redirige vers l'EXTERNAL_URL"""
    try:
        response = request_with_retry(test_url, retries=3)
        if response and 300 <= response.status_code < 400:
            location = response.headers.get("Location")
            if location and EXTERNAL_URL in location:
                return True
    except requests.exceptions.RequestException:
        return False
    return False

def scan_page_for_redirects(page_url):
    """Scanne une page pour des URL de redirection ouvertes"""
    links = get_all_links(page_url)
    for link in links:
        if link.startswith('http') and TARGET_DOMAIN in link:
            for param in REDIRECT_PARAMS:
                full_url = f"{link}?{urlencode({param: EXTERNAL_URL})}"
                if is_open_redirect(full_url):
                    print(f"[⚠️ VULNÉRABLE] {full_url} redirige vers {EXTERNAL_URL}")
                else:
                    print(f"[✔️ SÛR] {full_url}")

            js_redirects = get_js_redirects(link)
            for js_url in js_redirects:
                if js_url.startswith(TARGET_DOMAIN) and is_open_redirect(js_url):
                    print(f"[⚠️ VULNÉRABLE] JavaScript redirige vers {EXTERNAL_URL} depuis {link}")
                    
def scan_form_for_redirects(page_url):
    """Scanne un formulaire pour détecter des redirections ouvertes après soumission"""
    try:
        response = request_with_retry(page_url)
        if not response:
            return
        soup = BeautifulSoup(response.text, "html.parser")

        for form in soup.find_all("form"):
            action = form.get("action")
            if action:
                full_action = urljoin(page_url, action)
                data = {input_tag.get("name"): input_tag.get("value") for input_tag in form.find_all("input") if input_tag.get("name")}
                data["redirect"] = EXTERNAL_URL
                
                response = request_with_retry(full_action, retries=3)
                if response and is_open_redirect(response.url):
                    print(f"[⚠️ VULNÉRABLE] Formulaire {full_action} redirige vers {EXTERNAL_URL}")
                else:
                    print(f"[✔️ SÛR] Formulaire {full_action} sécurisé")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors du scan du formulaire sur {page_url}: {e}")

def crawl_and_scan(domain):
    """Fait un crawl complet du site pour scanner toutes les pages"""
    urls_to_visit = [domain]
    while urls_to_visit:
        current_url = urls_to_visit.pop()
        if current_url not in visited_urls:
            visited_urls.add(current_url)
            print(f"Scanning {current_url}")
            
            scan_page_for_redirects(current_url)
            
            scan_form_for_redirects(current_url)
            
            links = get_all_links(current_url)
            for link in links:
                full_link = urljoin(current_url, link)
                if TARGET_DOMAIN in full_link and full_link not in visited_urls:
                    urls_to_visit.append(full_link)
            
            time.sleep(random.uniform(2, 5))

print(f"🔍 Scan complet du site {TARGET_DOMAIN} pour détecter les redirections ouvertes...\n")
crawl_and_scan(TARGET_DOMAIN)
