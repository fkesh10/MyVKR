# injector.py

import json
import time
import os
import requests
import subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService

def save_results_to_file(results):
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"results/injector_output_{timestamp}.txt"
    with open(path, "w", encoding="utf-8") as f:
        for i, r in enumerate(results, 1):
            f.write(f"[{i}] Payload: {r.get('payload')}\n")
            f.write(f"    Target: {r['point'].get('action') or r['point'].get('url')}\n")
            f.write(f"    Method: {r['point'].get('form_method') or r['point'].get('method', 'GET')}\n")
            f.write(f"    Status: {r.get('status')}\n")
            f.write(f"    Error: {r.get('error', '')}\n")
            f.write(f"    Response (preview):\n{r.get('actual', '')}\n")
            if r.get("full_actual"):
                f.write(f"    Full HTML:\n{r['full_actual']}\n")
            f.write("=" * 60 + "\n")
    print(f"[INFO] Injector output saved to {path}")

def load_payloads(param, custom_payloads_path):
    payloads = []
    if param:
        payloads = [param]
    elif custom_payloads_path:
        try:
            if custom_payloads_path.endswith(".txt"):
                with open(custom_payloads_path, "r", encoding="utf-8") as f:
                    payloads = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            else:
                with open(custom_payloads_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    payloads = [d["payload"] if isinstance(d, dict) else d for d in data]
        except Exception as e:
            return [], f"Failed to load payloads: {e}"
    return payloads, None

def exploit(url=None, points=None, engine=None, proxy=None, timeout=5, delay=0.0,
            custom_payloads_path=None, param=None, cookie=None, user_agent=None):

    payloads, error = load_payloads(param, custom_payloads_path)
    if error:
        return [{"error": error}]
    if not payloads:
        return [{"error": "No payloads provided."}]

    if not (url and points):
        try:
            with open("results/lasy_test.json", "r", encoding="utf-8") as f:
                lines = [line for line in f if not line.strip().startswith("//")]
                data = json.loads("".join(lines))[0]
                url = data["url"]
                points = data["validated_points"]
        except Exception as e:
            return [{"error": f"Failed to load lasy_test.json: {e}"}]

    headers = {
        "User-Agent": user_agent or "Mozilla/5.0",
        "Accept": "text/html",
    }

    cookies = {}
    if cookie:
        try:
            cookies = dict(pair.strip().split("=", 1) for pair in cookie.split(";") if "=" in pair)
        except:
            pass

    proxies = {"http": proxy, "https": proxy} if proxy else None

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    if proxy:
        chrome_options.add_argument(f"--proxy-server={proxy}")
    if user_agent:
        chrome_options.add_argument(f"--user-agent={user_agent}")
    service = ChromeService()
    service.creationflags = subprocess.CREATE_NO_WINDOW

    results = []

    for payload in payloads:
        for point in points:
            field_name = point.get("name")
            target_url = point.get("action") or point.get("url") or url
            method = (point.get("form_method") or point.get("method") or "GET").upper()

            result_entry = {
                "payload": payload,
                "point": point,
                "status": "not executed",
                "actual": "",
                "full_actual": "",
                "error": ""
            }

            try:
                if method == "POST":
                    response = requests.post(
                        target_url,
                        data={field_name: payload},
                        headers=headers,
                        cookies=cookies,
                        proxies=proxies,
                        timeout=timeout
                    )
                else:
                    response = requests.get(
                        target_url,
                        params={field_name: payload},
                        headers=headers,
                        cookies=cookies,
                        proxies=proxies,
                        timeout=timeout
                    )
                result_entry["status"] = f"{response.status_code}"
                result_entry["actual"] = response.text[:500]
                result_entry["full_actual"] = response.text

                if response.status_code == 503 or not response.text.strip():
                    raise Exception("Trigger Selenium fallback")

            except Exception as e:
                try:
                    driver = webdriver.Chrome(service=service, options=chrome_options)
                    driver.get(target_url)
                    time.sleep(0.5)
                    if cookie:
                        for pair in cookie.split(";"):
                            if "=" in pair:
                                k, v = pair.strip().split("=", 1)
                                driver.add_cookie({"name": k.strip(), "value": v.strip()})
                        driver.refresh()
                        time.sleep(0.5)
                    field = driver.find_element(By.NAME, field_name)
                    field.clear()
                    field.send_keys(payload)
                    submit = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
                    submit.click()
                    time.sleep(1)
                    page = driver.page_source
                    result_entry["status"] = "selenium fallback"
                    result_entry["actual"] = page[:500]
                    result_entry["full_actual"] = page
                except Exception as se:
                    result_entry["status"] = "selenium failed"
                    result_entry["error"] = str(se)
                finally:
                    try:
                        driver.quit()
                    except:
                        pass

            results.append(result_entry)
            if delay > 0:
                time.sleep(delay)

    save_results_to_file(results)
    return results
