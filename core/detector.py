# detector.py

import requests
import time
from urllib.parse import urlparse, urlunparse
from payloads.test.python import jinja2_test, django_test
from payloads.test.PHP import twig_test

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
import subprocess

def detect(url, points, param=None, proxy=None, timeout=5, delay=0.0, cookies=None, user_agent=None):
    engines = {
        "jinja2": jinja2_test.test_payloads,
        "django": django_test.test_payloads,
        "twig": twig_test.test_payloads,
    }

    headers = {
        "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html",
    }

    proxies = {"http": proxy, "https": proxy} if proxy else None
    results = {engine: 0 for engine in engines}

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging", "enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")
    if user_agent:
        chrome_options.add_argument(f"--user-agent={user_agent}")

    service = ChromeService()
    service.creationflags = subprocess.CREATE_NO_WINDOW
    service.stdout = subprocess.DEVNULL
    service.stderr = subprocess.DEVNULL

    for engine_name, payloads in engines.items():
        for payload_entry in payloads:
            payload = payload_entry.get("payload")
            expected = payload_entry.get("expected")
            declared_engine = payload_entry.get("engine")

            if not payload or not expected or declared_engine.lower() != engine_name:
                continue

            for point in points:
                method = (point.get("method") or point.get("form_method") or "GET").upper()
                point_type = point.get("type")
                target_url = point.get("url") or point.get("action") or url
                param_name = point.get("name")
                response_text = ""

                try:
                    if point_type == "form_field":
                        data = {param_name: payload}
                        if method == "POST":
                            response = requests.post(target_url, data=data, headers=headers,
                                                     proxies=proxies, timeout=timeout, cookies=cookies)
                        else:
                            response = requests.get(target_url, params=data, headers=headers,
                                                    proxies=proxies, timeout=timeout, cookies=cookies)
                        if response.status_code == 503 or not response.text.strip():
                            raise Exception("Use Selenium")
                        response_text = response.text

                    elif point_type == "url_param":
                        parsed = urlparse(target_url)
                        clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
                        response = requests.get(clean_url, params={param_name: payload}, headers=headers,
                                                proxies=proxies, timeout=timeout, cookies=cookies)
                        if response.status_code == 503 or not response.text.strip():
                            raise Exception("Use Selenium")
                        response_text = response.text

                    else:
                        continue

                except:
                    try:
                        driver = webdriver.Chrome(service=service, options=chrome_options)
                        driver.get(target_url)
                        if cookies:
                            for k, v in cookies.items():
                                driver.add_cookie({"name": k, "value": v})
                            driver.refresh()

                        if point_type == "form_field":
                            time.sleep(1)
                            field = driver.find_element(By.NAME, param_name)
                            field.clear()
                            field.send_keys(payload)
                            submit = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
                            submit.click()
                            time.sleep(1)
                            response_text = driver.page_source
                        elif point_type == "url_param":
                            parsed = urlparse(target_url)
                            clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
                            final_url = f"{clean_url}?{param_name}={payload}"
                            driver.get(final_url)
                            time.sleep(1)
                            response_text = driver.page_source
                    except:
                        response_text = ""
                    finally:
                        try:
                            driver.quit()
                        except:
                            pass

                if expected in response_text:
                    results[engine_name] += 1

                if delay > 0:
                    time.sleep(delay)

    best_engine = max(results, key=results.get)
    return best_engine if results[best_engine] > 0 else None
