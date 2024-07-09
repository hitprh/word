import subprocess
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import signal
import sys

def fetch_urls_from_file():
    filename = input("Enter the target .txt file containing URLs (e.g., urls.txt): ")
    if filename.endswith('.txt') and os.path.exists(filename):
        try:
            with open(filename, 'r', buffering=1024*1024) as file: 
                content = file.read()
            return content.splitlines()
        except Exception as e:
            print(f"Error occurred while reading '{filename}': {e}")
            return []
    else:
        print(f"Error: '{filename}' is either not a .txt file or does not exist.")
        return []


base_start_url = "https://red.scbphil.com/woo?site="

def fetch_data(url):
    full_url = base_start_url + url
    curl_command = ['curl', '-s', '-w', '%{http_code}', '-o', '-', full_url]
    try:
        process = subprocess.Popen(curl_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        status_code = stdout[-3:]  
        content = stdout[:-3]  

        if process.returncode == 0:
            try:
                data = json.loads(content)
                if data.get('success'):
                    result = f"{data.get('url', 'N/A')}, Captcha: {data.get('captcha', 'N/A')}, Gateway: {data.get('gateway', 'N/A')}, Quality: {data.get('quality', 'N/A')}\n"
                    captcha_status = data.get('captcha', 'N/A')
                    return status_code, captcha_status, result
                else:
                    return status_code, None, None
            except json.JSONDecodeError:
                return status_code, None, None
        else:
            return status_code, None, None
    except subprocess.CalledProcessError:
        return "000", None, None 
    except Exception:
        return "000", None, None 


def write_result(result, filename):
    if result: 
        try:
            with open(filename, 'a') as result_file:
                result_file.write(result)
        except Exception as e:
            print(f"Error writing result to {filename}: {e}")


def signal_handler(sig, frame):
    print("\nProcess interrupted! Shutting down gracefully...")
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


if __name__ == '__main__':
    url_list = fetch_urls_from_file()
    if not url_list:
        print("No valid URLs found. Exiting.")
        sys.exit(1)

    no_captcha_file = 'no_captcha.txt'
    captcha_file = 'captcha.txt'

    for filename in [no_captcha_file, captcha_file]:
        if not os.path.exists(filename):
            try:
                open(filename, 'w').close()
            except Exception as e:
                print(f"Error creating {filename}: {e}")
                exit()

    total_urls = len(url_list)
    print(f"Total URLs to process: {total_urls}")

    processed_count = 0

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(fetch_data, url) for url in url_list]

        try:
            for future in as_completed(futures):
                status_code, captcha_status, result = future.result()
                processed_count += 1
                print(f"Processed {processed_count}/{total_urls} URLs, Status: {status_code}", end='\r')
                if result:
                    if captcha_status == "No Captcha":
                        write_result(result, no_captcha_file)
                    else:
                        write_result(result, captcha_file)
        except KeyboardInterrupt:
            signal_handler(None, None)

    print("\nChecking done.")
