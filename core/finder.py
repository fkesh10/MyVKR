# finder.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service as ChromeService
from urllib.parse import urlparse, parse_qs, urlencode
import time
import subprocess

def parse_cookies(cookie_string):
    cookies = []
    if cookie_string:
        parts = cookie_string.split(";")
        for part in parts:
            if "=" in part:
                name, value = part.strip().split("=", 1)
                cookies.append({"name": name.strip(), "value": value.strip()})
    return cookies

def find(url, method="BOTH", proxy=None, headers=None, cookies=None):
    points = []
    test_value = "SSTI_TEST_HERE"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    if proxy:
        chrome_options.add_argument(f'--proxy-server={proxy}')

    service = ChromeService()
    service.creationflags = subprocess.CREATE_NO_WINDOW

    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(10)

    try:
        driver.get("about:blank")

        if cookies:
            driver.get(url)
            for cookie in parse_cookies(cookies):
                try:
                    driver.add_cookie(cookie)
                except Exception:
                    continue

        driver.get(url)
        time.sleep(1)

        # === 1. Обработка форм ===
        forms = driver.find_elements(By.TAG_NAME, "form")
        for form in forms:
            try:
                form_method = form.get_attribute("method") or "GET"
                form_method = form_method.strip().upper()
                action = form.get_attribute("action") or driver.current_url
                action_url = driver.execute_script("return new URL(arguments[0], window.location.href).href;", action)

                input_elements = form.find_elements(By.TAG_NAME, "input") + form.find_elements(By.TAG_NAME, "textarea")
                field_names = []

                for field in input_elements:
                    name = field.get_attribute("name")
                    if name:
                        try:
                            field.clear()
                            field.send_keys(test_value)
                            field_names.append(name)
                        except:
                            continue

                if not field_names:
                    continue

                try:
                    submit_button = form.find_element(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
                    submit_button.click()
                    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    time.sleep(0.5)
                except:
                    continue

                final_url = driver.current_url
                body_text = driver.page_source

                if form_method == "GET":
                    parsed = urlparse(final_url)
                    query = parse_qs(parsed.query)
                    for param in query:
                        if test_value in query[param]:
                            points.append({
                                "type": "url_param",
                                "method": "GET",
                                "name": param,
                                "url": f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{param}="
                            })

                elif form_method == "POST":
                    try:
                        visible_text = driver.find_element(By.TAG_NAME, "body").text
                    except:
                        visible_text = body_text

                    if test_value.lower() in visible_text.lower():
                        for name in field_names:
                            points.append({
                                "type": "form_field",
                                "form_method": "POST",
                                "name": name,
                                "action": action_url
                            })

                driver.get(url)
                time.sleep(0.5)

            except Exception:
                continue

        # === 2. Дополнительная проверка параметров в исходном URL ===
                # === 2. Проверка параметров даже без значений ===
        parsed = urlparse(url)
        raw_params = parsed.query.split("&")
        param_names = [p.split("=")[0] for p in raw_params if p]

        for param in param_names:
            try:
                test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{param}=SSTI_TEST_HERE"
                driver.get(test_url)
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(0.5)
                body_text = driver.find_element(By.TAG_NAME, "body").text
                if "SSTI_TEST_HERE" in body_text:
                    points.append({
                        "type": "url_param",
                        "method": "GET",
                        "name": param,
                        "url": f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{param}="
                    })
            except Exception:
                continue


    finally:
        driver.quit()

    return points
