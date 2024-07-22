import os
import requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import shutil
import sys
import time
from datetime import datetime
from urllib.parse import urlparse


PROXY = "alpha.premium.stellaproxies.com:5181"
PROXY_AUTH = "m0vF7ujT:aOEEslR7"

def update_proxy_in_script(proxy, proxy_auth):
    script_path = sys.argv[0]
    with open(script_path, 'r') as file:
        lines = file.readlines()

    for i, line in enumerate(lines):
        if line.startswith("PROXY = "):
            lines[i] = f'PROXY = "{proxy}"\n'
        elif line.startswith("PROXY_AUTH = "):
            lines[i] = f'PROXY_AUTH = "{proxy_auth}"\n'

    with open(script_path, 'w') as file:
        file.writelines(lines)

def rerun():
    python = sys.executable
    os.execv(python, [python] + sys.argv)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

def extract_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def remove_duplicates_by_domain(urls):
    unique_domains = set()
    unique_urls = []

    for url in urls:
        domain = extract_domain(url)
        if domain not in unique_domains:
            unique_domains.add(domain)
            unique_urls.append(url)

    return unique_urls

def read_urls_from_file(filename):
    with open(filename, 'r') as f:
        urls = [line.strip() for line in f.readlines()]
    return urls

def write_urls_to_file(filename, unique_urls):
    with open(filename, 'w') as f:
        for url in unique_urls:
            f.write(url + '\n')

def remove_duplicates():
    filename = input("Enter the filename (e.g., 1.txt): ")
    urls = read_urls_from_file(filename)
    unique_urls = remove_duplicates_by_domain(urls)
    write_urls_to_file(filename, unique_urls)
    print(f"Removed duplicates. {len(urls) - len(unique_urls)} duplicates found.")
    sys.exit(0)

def configure_proxy():
    clear_screen()
    input_proxy = input("Input proxy (format proxy:port): ")
    input_proxy_auth = input("Input proxy auth (format user:pass): ")

    update_proxy_in_script(input_proxy, input_proxy_auth)

    print("Proxy configuration saved successfully.")
    sys.exit(0)

def get_links(value):
    global PROXY, PROXY_AUTH
    proxies = {
        'http': f'http://{PROXY}',
        'https': f'http://{PROXY}'
    }
    auth = requests.auth.HTTPProxyAuth(*PROXY_AUTH.split(':')[0:2])
    query = f"{dork} {value}"
    google_search_url = f"http://www.google.com/search?q={query}&num=100"
    headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.119 Mobile Safari/537.36'}
    try:
        response = requests.get(google_search_url, proxies=proxies, auth=auth, timeout=15)
        status_code = response.status_code

        if status_code != 200:
            with open(error_file, "a") as input_to:
                input_to.write(value + "\n")
            return f"Error Code: {status_code}"
        soup = BeautifulSoup(response.content, 'html.parser')
        links = soup.find_all('a')

        urls = []
        for link in links:
            href = link.get('href')
            if href and href.startswith('/url?q=') and not 'webcache' in href:
                actual_url = href.split('?q=')[1].split('&sa=U')[0]
                if 'google.com' not in actual_url and not actual_url.startswith('/search'):
                    urls.append(actual_url)

        if urls:
            total_urls = len(urls)
            with open(output_file, "a") as input_to:
                for url in urls:
                    input_to.write(url + "\n")
            return((f"Total: {total_urls}"))
        else:
            return((f"Total: 0"))
    except requests.exceptions.RequestException as e:
        return ""

def save_line_number(line_number):
    with open(counter_file, 'w') as file:
        file.write(str(line_number))

def save_err_link(url):
    with open(error_file, 'a') as file:
        file.write(url + '\n')

def process_url(url, line_number):
    global counter
    counter += 1
    if counter % 100 == 0:
        clear_screen()
    if url.strip():
        output = get_links(url)
        if output != "skip":
            print(f"{counter}: {url} => {output}")
        save_line_number(line_number)
        return line_number
    return None

def start_processing():
    global counter
    start_line = 1
    if os.path.exists(counter_file):
        with open(counter_file, 'r') as file:
            start_line = int(file.read().strip())
    urls_list = read_urls_from_file(word_file)[start_line - 1:]

    batch_size = 10
    for i in range(0, len(urls_list), batch_size):
        batch_urls = urls_list[i:i + batch_size]
        start_time = time.time()
        all_results = []
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            results = executor.map(process_url, batch_urls, range(start_line + i, start_line + i + len(batch_urls)))
        for result in results:
            all_results.append(result)
        if None not in all_results:
            largest_number = max(all_results)
            with open(backup_file, 'w') as file:
                file.write(str(largest_number))
    sys.exit(0)

if __name__ == "__main__":
    print("Welcome Pro, select an option:")
    print("1. Google Dork")
    print("2. Remove Duplicate (domain based)")
    print("3. Reset/Input Proxy")
    print("4. Exit")
    choice = input("Enter your choice (1, 2, 3, or 4): ")

    if choice == '1':
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        output_file = "url.txt"
        main_wordlist = f"data/word_list_{timestamp}.txt"
        word_file = f"data/word_{timestamp}.txt"
        counter_file = f"data/counter_{timestamp}.txt"
        backup_file = f"data/backup_{timestamp}.txt"
        error_file = f"data/error_{timestamp}.txt"
        dork_file = f"data/dork_{timestamp}.txt"

        counter = 0

        clear_screen()

        os.makedirs("data", exist_ok=True)

        if not os.path.exists(main_wordlist):
            hash_url = 'http://hashphil-siete.com//word_list/word.txt'
            git_url = 'https://raw.githubusercontent.com/hitprh/word/main/words.txt'
            response = requests.get(hash_url) if requests.get(hash_url).status_code == 200 else requests.get(git_url)
            open(main_wordlist, 'wb').write(response.content)

        if os.path.exists(counter_file) and os.path.getsize(counter_file) == 0:
            if os.path.exists(backup_file):
                shutil.copy(backup_file, counter_file)
                remove_file(backup_file)

        if os.path.exists(counter_file) and os.path.getsize(counter_file) > 0:
            response = input("Press 'Enter' to continue the progress\nType 'Reset' to reset everything\nType 'Dork' to reset dork and wordlist: ")
            if response.lower() == 'reset':
                clear_screen()
                response = input("All files in the data folder will be deleted. Type Y to continue: ")
                if response.lower() == 'y':
                    files_to_remove = [f"data/{filename}" for filename in os.listdir("data") if timestamp in filename]
                    for file_to_remove in files_to_remove:
                        remove_file(file_to_remove)
                    rerun()
            elif response.lower() == 'dork':
                clear_screen()
                response = input("Dork, Wordlist, Error and Counter files in the data folder will be deleted. Type Y to continue: ")
                if response.lower() == 'y':
                    files_to_remove = [f"data/{filename}" for filename in os.listdir("data") if timestamp in filename]
                    for file_to_remove in files_to_remove:
                        remove_file(file_to_remove)
                    rerun()

        if not os.path.exists(dork_file) or os.path.getsize(dork_file) == 0:
            input_dork = input("Enter dork (inurl:hatdog): ")
            if input_dork.strip():
                with open(dork_file, 'w') as f:
                    f.write(input_dork)
            else:
                print("Dork cannot be empty. Please enter a valid dork.")
                time.sleep(2.5)
                rerun()

        with open(dork_file, 'r') as file:
            dork = file.read()
            if not dork:
                os.remove(dork_file)
                rerun()

        if not os.path.exists(word_file):
            if os.path.exists(main_wordlist):
                shutil.copy(main_wordlist, word_file)
                print("File copied successfully.")
            else:
                print("Source word file not found.")
                time.sleep(1)
                rerun()

        start_processing()

        files_to_remove = [
            main_wordlist,
            word_file,
            counter_file,
            backup_file,
            error_file,
            dork_file
        ]

    elif choice == '2':
        remove_duplicates()

        files_to_remove = [
            'data/word_list.txt',  
            'data/word.txt',       
            'data/counter.txt',    
            'data/backup.txt',     
            'data/error.txt',      
            'data/dork.txt'        
        ]

    elif choice == '3':
        configure_proxy()

    elif choice == '4':
        print("Exiting program.")
        sys.exit(0)

    else:
        print("Invalid choice. Please enter 1, 2, 3, or 4.")
        sys.exit(1)

    # Clean up data files
    for file_to_remove in files_to_remove:
        remove_file(file_to_remove)
