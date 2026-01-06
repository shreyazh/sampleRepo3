import requests
import csv
import json
import threading
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from urllib.robotparser import RobotFileParser

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Advanced Internal Link Auditor)"
}

MAX_THREADS = 10
TIMEOUT = 10
ALLOWED_EXTENSIONS = ("", ".html", ".php", ".htm", "/")

lock = threading.Lock()


def normalize_url(url):
    url, _ = urldefrag(url)
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}{parsed.path}".rstrip("/")


def is_valid_page(url):
    parsed = urlparse(url)
    return parsed.path.endswith(ALLOWED_EXTENSIONS)


def load_robots_txt(base_url):
    rp = RobotFileParser()
    robots_url = urljoin(base_url, "/robots.txt")
    try:
        rp.set_url(robots_url)
        rp.read()
    except:
        pass
    return rp


def fetch_links(url, domain, robots, results, visited, max_depth, depth):
    if depth > max_depth:
        return

    with lock:
        if url in visited:
            return
        visited.add(url)

    if not robots.can_fetch(HEADERS["User-Agent"], url):
        return

    try:
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        status = response.status_code
    except requests.RequestException:
        with lock:
            results[url] = "ERROR"
        return

    with lock:
        results[url] = status

    if status != 200:
        return

    soup = BeautifulSoup(response.text, "html.parser")

    for link in soup.find_all("a", href=True):
        href = link.get("href")
        absolute = normalize_url(urljoin(url, href))
        parsed = urlparse(absolute)

        if parsed.netloc != domain:
            continue

        if not is_valid_page(absolute):
            continue

        fetch_links(
            absolute,
            domain,
            robots,
            results,
            visited,
            max_depth,
            depth + 1
        )


def crawl_site(start_url, max_depth=3):
    start_url = normalize_url(start_url)
    domain = urlparse(start_url).netloc

    robots = load_robots_txt(start_url)
    visited = set()
    results = {}

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        executor.submit(
            fetch_links,
            start_url,
            domain,
            robots,
            results,
            visited,
            max_depth,
            0
        )

    return results


def export_csv(data, filename="internal_links_report.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "Status"])
        for url, status in sorted(data.items()):
            writer.writerow([url, status])


def export_json(data, filename="internal_links_report.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    site = input("Enter website URL (https://example.com): ").strip()
    depth = int(input("Enter crawl depth (recommended 2–4): ").strip())

    print("\nCrawling site...\n")
    results = crawl_site(site, max_depth=depth)

    broken = {u: s for u, s in results.items() if s != 200}

    export_csv(results)
    export_json(results)

    print(f"Total internal pages found: {len(results)}")
    print(f"Broken / error pages found: {len(broken)}")
    print("\nReports generated:")
    print("- internal_links_report.csv")
    print("- internal_links_report.json")
