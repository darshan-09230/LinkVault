import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import unicodedata
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from collections import OrderedDict


class WebsiteDataExtractor:

    def __init__(self, url):
        self.url = url

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "AppleWebKit/537.36 "
                "Chrome/120 Safari/537.36"
            )
        }

        self.junk_phrases = [
            "view more", "explore now", "click here", "read more",
            "advertise with us", "hire with us", "cookie policy",
            "privacy policy", "terms of service", "sign up", "login",
            "accept cookies", "all rights reserved"
        ]

    # ================= FETCH =================
    def get_page(self):
        r = requests.get(self.url, headers=self.headers, timeout=15)
        r.raise_for_status()
        return r.text

    # ================= CLEAN =================
    def clean_text(self, text):
        if not text:
            return ""

        text = unicodedata.normalize("NFKC", text).lower()
        text = re.sub(r"http\S+", " ", text)
        text = re.sub(r"\S+@\S+", " ", text)
        text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text)

        return text.strip()

    def remove_stopwords(self, text):
        return " ".join([
            w for w in text.split()
            if w not in ENGLISH_STOP_WORDS
        ])

    def remove_junk(self, text):
        for j in self.junk_phrases:
            text = text.replace(j, " ")
        return text

    def dedupe_sentences(self, text):
        sentences = re.split(r'(?<=[.!?]) +', text)
        return " ".join(OrderedDict.fromkeys(sentences))

    # ================= TOKENS =================
    def tokenize_domain(self, domain):
        domain = domain.lower().replace("www.", "")
        domain = re.sub(r"\.(com|org|net|io|ai|app|dev|co|in)$", "", domain)
        domain = re.sub(r"[-_.]", " ", domain)
        return domain.strip()

    def tokenize_path(self, path):
        path = path.replace("/", " ")
        path = re.sub(r"[-_]", " ", path)
        path = re.sub(r"[^a-zA-Z0-9\s]", " ", path)
        return re.sub(r"\s+", " ", path).strip().lower()

    # ================= MAIN =================
    def extract(self):

        html = self.get_page()
        soup = BeautifulSoup(html, "html.parser")

        # remove noise
        for tag in soup(["script", "style", "noscript", "iframe",
                         "svg", "footer", "nav", "aside",
                         "form", "header", "button"]):
            tag.decompose()

        parsed = urlparse(self.url)

        domain_tokens = self.tokenize_domain(parsed.netloc)
        url_keywords = self.tokenize_path(parsed.path)

        title = self.clean_text(soup.title.get_text()) if soup.title else ""

        meta = soup.find("meta", attrs={"name": "description"}) or \
               soup.find("meta", attrs={"property": "og:description"})

        meta_description = self.clean_text(meta.get("content", "")) if meta else ""

        headings = " ".join([
            self.clean_text(h.get_text())
            for h in soup.find_all(["h1", "h2", "h3"])
        ])

        paragraphs = " ".join([
            self.clean_text(p.get_text())
            for p in soup.find_all("p")
            if 10 <= len(p.get_text().split()) <= 150
        ])

        combined = " ".join([
            domain_tokens,
            url_keywords,
            title,
            meta_description,
            headings,
            paragraphs
        ])

        # pipeline
        combined = self.remove_junk(combined)
        combined = self.dedupe_sentences(combined)
        combined = self.remove_stopwords(combined)
        combined = self.clean_text(combined)

        # FINAL CSV OUTPUT ONLY
        output = [
            self.url,
            parsed.netloc,
            domain_tokens,
            url_keywords,
            title,
            meta_description,
            combined
        ]

        return ",".join(str(x).replace(",", " ").strip() for x in output)


