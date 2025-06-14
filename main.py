# main.py

import argparse
import json
import os
from datetime import datetime
from core import finder, detector, confirmer, injector
from utils import cli_output, json_output

def save_lasy_all(data_list, launch_args):
    os.makedirs("results", exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    args_line = " ".join(
        [f"--{k} {v}" for k, v in launch_args.items() if v is not None and not isinstance(v, bool)] +
        [f"--{k}" for k, v in launch_args.items() if isinstance(v, bool) and v]
    )
    with open("results/lasy_test.json", "w", encoding="utf-8") as f:
        f.write(f"// Last scan: {timestamp}\n")
        f.write(f"// Launch args: {args_line}\n")
        json.dump(data_list, f, indent=4, ensure_ascii=False)
    cli_output.print_info("Saved full confirmer results to lasy_test.json")

def load_lasy():
    try:
        with open("results/lasy_test.json", "r", encoding="utf-8") as f:
            lines = f.readlines()
            json_data = "".join(line for line in lines if not line.strip().startswith("//"))
            return json.loads(json_data)
    except Exception as e:
        cli_output.print_warning(f"Cannot load lasy_test.json: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="SSTI Penetration Testing Framework")

    parser.add_argument("--url", help="Целевая URL")
    parser.add_argument("--urls_list", help="Путь до *.txt файла для сканирование нескольких URL")

    parser.add_argument("--method", choices=["GET", "POST", "BOTH"], default="BOTH", help="HTTP метод для тестов")
    parser.add_argument("--param", help="Единичная полезная нагрузка (пример: {{5*5}} (только с injcetion))")
    parser.add_argument("--list_of_params", help="Путь до файла *.txt для запуска множественной полезной нагрузки (только с injcetion)")
    parser.add_argument("--delay", type=float, default=0.0, help="Задержка между ответами от сервера (в секундах)")
    parser.add_argument("--timeout", type=int, default=5, help="Максимальное время ожидания ответа от сервера")
    parser.add_argument("--proxy", help="ПРокси сервер (пример: http://127.0.0.1:8080)")
    parser.add_argument("--verbose", action="store_true", help="Включить подробный отчет")
    parser.add_argument("--user_agent", help="Путь до файла для кастомного Юзер-Агента")
    parser.add_argument("--cookie", help="Путь до файла с cookie")


    parser.add_argument("--finder", action="store_true", help="Запустить посик только для потенциальных точек уязвимости")
    parser.add_argument("--low_test", action="store_true", help="Запустить в режиме безопасного сканирования")
    parser.add_argument("--hard_test", action="store_true", help="Запустить в режиме не безопасного сканирования")
    parser.add_argument("--injection", action="store_true", help="Запустить модуль эксплуатации (необходимо указать нагрузку или путь до файла с нагрузкой)")

    args = parser.parse_args()
    launch_args = vars(args)
    user_agent = None
    cookie_string = None
    cookies = None
    if args.user_agent:
        try:
            with open(args.user_agent, "r", encoding="utf-8") as f:
                user_agent = f.read().strip()
                cli_output.print_info(f"Using custom User-Agent: {user_agent}")
        except Exception as e:
            cli_output.print_warning(f"Failed to read User-Agent file: {e}")
    if args.cookie:
        try:
            with open(args.cookie, "r", encoding="utf-8") as f:
                cookie_string = f.read().strip()
                cookies = dict(pair.strip().split("=", 1) for pair in cookie_string.split(";") if "=" in pair)
                cli_output.print_info(f"Using cookies: {cookies}")
        except Exception as e:
            cli_output.print_warning(f"Failed to read cookie file: {e}")
    
    if not args.url and not args.urls_list:
        parser.error("You must specify either --url or --urls_list")

    if args.delay < 0:
        args.delay = 0.0

    targets = []
    if args.urls_list:
        try:
            with open(args.urls_list, "r", encoding="utf-8") as f:
                targets = [line.strip() for line in f if line.strip()]
        except Exception as e:
            cli_output.print_warning(f"Cannot load URL list: {e}")
            return
    else:
        targets = [args.url]

    cli_output.print_banner()
    batch_verbose_results = []
    batch_mode = bool(args.urls_list and args.verbose)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_filename = f"results/verbose_batch_{timestamp}.json"

    if args.injection:
        cli_output.print_info("Running injector using lasy_test.json...")
        all_entries = load_lasy()
        if not isinstance(all_entries, list):
            cli_output.print_warning("lasy_test.json must contain a list of objects.")
            return
        
        cli_output.print_info("Available confirmed entries from lasy_test.json:")
        for idx, entry in enumerate(all_entries, 1):
            cli_output.print_info(f"{idx}. {entry.get('url')} (engine: {entry.get('engine')})")
        
        try:
            selection = int(input("Select entry to test (1-N): ").strip())
            if not (1 <= selection <= len(all_entries)):
                cli_output.print_warning("Invalid selection.")
                return
        except Exception:
            cli_output.print_warning("Invalid input.")
            return
        
        data = all_entries[selection - 1]
        url = data.get("url")
        engine = data.get("engine")
        all_points = data.get("validated_points", [])
        
        if not all_points:
            cli_output.print_warning("No validated points in lasy_test.json")
            return

        cli_output.print_info("Select a point to test with payloads:")
        for idx, pt in enumerate(all_points, 1):
            t = pt.get("type", "unknown")
            m = pt.get("method") or pt.get("form_method", "GET")
            name = pt.get("name", "?")
            target = pt.get("url") or pt.get("action")
            cli_output.print_info(f"{idx}. type={t} | method={m} | name={name} | target={target}")

        cli_output.print_info("Enter number to use a specific point or 0 to use all:")
        try:
            selection = int(input("Your choice: ").strip())
            if selection == 0:
                points = all_points
            elif 1 <= selection <= len(all_points):
                points = [all_points[selection - 1]]
            else:
                cli_output.print_warning("Invalid selection. Aborting.")
                return
        except Exception:
            cli_output.print_warning("Invalid input. Aborting.")
            return

        if not (url and engine and points):
            cli_output.print_warning("Missing required data in lasy_test.json")
            return
        result = injector.exploit(
            url=url,
            points=points,
            engine=engine,
            proxy=args.proxy,
            timeout=args.timeout,
            delay=args.delay,
            custom_payloads_path=args.list_of_params,
            param=args.param
        )
        cli_output.print_info("Injection results:")
        for i, entry in enumerate(result, 1):
            cli_output.print_info(f"[{i}] {entry['payload']}")
            # cli_output.print_info(f"     → {entry.get('status')}")
            # if 'error' in entry:
                # cli_output.print_warning(f"     ⚠ {entry['error']}")
            # elif 'response_snippet' in entry:
                # cli_output.print_info(f"     ← {entry['response_snippet']}")
        
        return

    run_all = not any([args.finder, args.low_test, args.hard_test])
    lasy_confirm_all = []
    for target_url in targets:
        cli_output.print_info(f"Scanning: {target_url}")
        results = {
            "url": target_url,
            "method": args.method,
            "param": args.param,
            "config": {
                "delay": args.delay,
                "timeout": args.timeout,
                "proxy": args.proxy,
                "custom_payloads_path": args.list_of_params
            },
            "steps": {}
        }

        if run_all or args.finder or args.low_test or args.hard_test:
            cli_output.print_info("Running finder...")
            points = finder.find(target_url, args.method, proxy=args.proxy)
            results["steps"]["finder"] = points
            if not points:
                cli_output.print_warning("No injection points found.")
                if args.verbose:
                    cli_output.print_verbose(results)
                    json_output.save(results)
                continue
            for i, p in enumerate(points, 1):
                field_type = p.get('type') or p.get('field_type') or 'unknown'
                method = p.get('method') or p.get('form_method') or 'GET'
                name = p.get('name', '—')
                target = p.get('url') or p.get('action') or '—'
                cli_output.print_info(f"[{i}] type={field_type} | method={method} | name={name} | target={target}")
        else:
            points = []

        if run_all or args.low_test or args.hard_test:
            cli_output.print_info("Running detector...")
            engine = detector.detect(
                url=target_url,
                points=points,
                param=args.param,
                proxy=args.proxy,
                timeout=args.timeout,
                delay=args.delay
            )
            results["steps"]["detector"] = {"engine": engine}
            if not engine:
                cli_output.print_warning("No template engine detected.")
                if args.verbose:
                    cli_output.print_verbose(results)
                    json_output.save(results)
                continue
            cli_output.print_info(f"Detected engine: {engine}?")
        else:
            engine = None

        if run_all or args.low_test or args.hard_test:
            confirm_mode = "low" if args.low_test else "hard" if args.hard_test else "low"
            cli_output.print_info("Running confirmer...")
            confirmed = confirmer.confirm(
                url=target_url,
                points=points,
                engine=engine,
                proxy=args.proxy,
                timeout=args.timeout,
                delay=args.delay,
                mode=confirm_mode
            )
            cli_output.print_success(f"Confirmed engine (by confirmer): {confirmed.get('engine', engine)}")
            lasy_data = {
                "url": target_url,
                "engine": confirmed.get("engine", engine),
                "validated_points": confirmed.get("validated_points", []),
                "tests": confirmed.get("tests", [])
            }
            if args.verbose:
                for test in lasy_data["tests"]:
                    cli_output.print_info(f"Payload: {test['payload']} | Expected: {test['expected']} | Success: {test['success']} | Actual: {test['actual'][:100].replace(chr(10), ' ')}")
            lasy_confirm_all.append(lasy_data)

        if args.verbose:
            cli_output.print_verbose(results)
            if batch_mode:
                batch_verbose_results.append(results)
            else:
                json_output.save(results)

        cli_output.print_success("Scan complete.\n")

    if batch_mode and batch_verbose_results:
        os.makedirs("results", exist_ok=True)
        timestamp_line = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        args_line = " ".join(
            [f"--{k} {v}" for k, v in launch_args.items() if v is not None and not isinstance(v, bool)] +
            [f"--{k}" for k, v in launch_args.items() if isinstance(v, bool) and v]
        )
        with open(batch_filename, "w", encoding="utf-8") as f:
            f.write(f"// Last scan: {timestamp_line}\n")
            f.write(f"// Launch args: {args_line}\n")
            json.dump(batch_verbose_results, f, indent=4, ensure_ascii=False)
        cli_output.print_info(f"Saved combined verbose results to {batch_filename}")

    if (run_all or args.low_test or args.hard_test) and lasy_confirm_all:
        save_lasy_all(lasy_confirm_all, launch_args)

if __name__ == "__main__":
    main()
