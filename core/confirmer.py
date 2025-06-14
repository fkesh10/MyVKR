# confirmer.py

import requests
import time
import subprocess
from copy import deepcopy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService

from payloads.test.python import jinja2_test, django_test
from payloads.test.PHP import twig_test
from payloads.ubi.python import jinja2_ubi, django_ubi
from payloads.ubi.PHP import twig_ubi


def confirm(url, points, engine, proxy=None, timeout=5, delay=0.0, mode="low", user_agent=None, cookies=None):
    engine_payloads = {
        "low": {
            "jinja2": jinja2_test.test_payloads,
            "django": django_test.test_payloads,
            "twig": twig_test.test_payloads
        },
        "hard": {
            "jinja2": jinja2_ubi.ubi_payloads,
            "django": django_ubi.ubi_payloads,
            "twig": twig_ubi.ubi_payloads
        }
    }

    if mode not in engine_payloads:
        return {"error": f"Unknown confirm mode: {mode}", "validated_points": [], "engine": engine, "tests": []}

    proxies = {"http": proxy, "https": proxy} if proxy else None
    headers = {
        "User-Agent": user_agent or "Mozilla/5.0",
        "Accept": "text/html",
    }

    validated_points = []
    engine_hits = {e: 0 for e in engine_payloads[mode].keys()}
    point_hits = {}
    detailed_results = []

    for point in points:
        original_point = deepcopy(point)
        name = point.get("name")
        methods = ["form_field", "url_param"]
        confirmed = False

        for method_type in methods:
            test_point = deepcopy(original_point)
            test_point["type"] = method_type
            point_type = test_point["type"]
            method = (test_point.get("method") or test_point.get("form_method") or "GET").upper()
            target_url = test_point.get("url") or test_point.get("action") or url

            for e_type, payloads in engine_payloads[mode].items():
                for test in payloads:
                    payload = test.get("payload")
                    expected = test.get("expected") or payload.strip("{}")
                    response_text = ""
                    success = False

                    try:
                        session = requests.Session()
                        if cookies:
                            session.headers.update({"Cookie": cookies})
                        session.headers.update(headers)

                        if point_type == "form_field":
                            data = {name: payload}
                            if method == "POST":
                                response = session.post(target_url, data=data,
                                                        proxies=proxies, timeout=timeout)
                            else:
                                response = session.get(target_url, params=data,
                                                       proxies=proxies, timeout=timeout)
                            response_text = response.text

                        elif point_type == "url_param":
                            try:
                                response = session.get(target_url, params={name: payload},
                                                       proxies=proxies, timeout=timeout)
                                if response.status_code == 503 or not response.text.strip():
                                    raise Exception("Fallback to Selenium")
                                response_text = response.text
                            except:
                                chrome_options = Options()
                                chrome_options.add_argument("--headless")
                                chrome_options.add_argument("--disable-gpu")
                                chrome_options.add_argument("--no-sandbox")
                                chrome_options.add_argument("--log-level=3")
                                chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
                                if user_agent:
                                    chrome_options.add_argument(f"user-agent={user_agent}")
                                if proxy:
                                    chrome_options.add_argument(f"--proxy-server={proxy}")

                                service = ChromeService()
                                service.creationflags = subprocess.CREATE_NO_WINDOW
                                driver = webdriver.Chrome(service=service, options=chrome_options)
                                try:
                                    driver.get(f"{target_url}?{name}={payload}")
                                    if cookies:
                                        for pair in cookies.split(";"):
                                            if "=" in pair:
                                                k, v = pair.strip().split("=", 1)
                                                driver.add_cookie({"name": k, "value": v})
                                        driver.refresh()
                                    time.sleep(1)
                                    response_text = driver.page_source
                                finally:
                                    driver.quit()
                        else:
                            continue

                        if expected in response_text:
                            engine_hits[e_type] += 1
                            point_hits.setdefault(name, {"form_field": 0, "url_param": 0})
                            point_hits[name][method_type] += 1
                            success = True
                            if not confirmed:
                                test_point["engine_confirmed"] = e_type
                                validated_points.append(test_point)
                                confirmed = True
                            break

                    except Exception as e:
                        response_text = f"EXCEPTION: {str(e)}"

                    detailed_results.append({
                        "payload": payload,
                        "expected": expected,
                        "actual": response_text[:300],
                        "success": success,
                        "engine_tested": e_type,
                        "point": test_point
                    })

                    if delay > 0:
                        time.sleep(delay)

    # Эвристика определения движка на основе шаблонных признаков
    engine_weights = engine_hits.copy()

    django_indicators = ["admin", "polls", "csrfmiddlewaretoken", "super-secret", "/index"]
    if any(ind in url.lower() for ind in django_indicators):
        engine_weights["django"] += 2

    for test in detailed_results:
        actual = test.get("actual", "").lower()
        if "django.template" in actual or "templatesyntaxerror" in actual:
            engine_weights["django"] += 3
        if "jinja2.exceptions" in actual:
            engine_weights["jinja2"] += 3

    best_engine = max(engine_weights, key=engine_weights.get)
    if engine_hits[best_engine] > 0 and best_engine != engine:
        engine = best_engine

    for pt in validated_points:
        name = pt["name"]
        if name in point_hits:
            stats = point_hits[name]
            if stats["form_field"] > stats["url_param"]:
                pt["type"] = "form_field"
            elif stats["url_param"] > stats["form_field"]:
                pt["type"] = "url_param"

    return {
        "validated_points": validated_points,
        "engine": engine,
        "tests": detailed_results
    }
