import os
import requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import shutil
import sys
import time
from datetime import datetime

# Function to restart script
def rerun():
    python = sys.executable
    os.execv(python, [python] + sys.argv)

# Function to clear console screen
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Function to remove duplicate lines from a file
def remove_duplicate_lines(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            lines = file.readlines()
        lines = list(dict.fromkeys(lines))
        with open(filename, 'w') as file:
            file.writelines(lines)

# Function to remove a file
def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

# Generate timestamp for filenames
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

# Define file paths
output_file = f"url.txt"
main_wordlist = f"data/word_list_{timestamp}.txt"
word_file = f"data/word_{timestamp}.txt"
counter_file = f"data/counter_{timestamp}.txt"
backup_file = f"data/backup_{timestamp}.txt"
error_file = f"data/error_{timestamp}.txt"
dork_file = f"data/dork_{timestamp}.txt"
proxy_file = f"data/proxy_{timestamp}.txt"
bot_telegram_file = f"data/bot_telegram_{timestamp}.txt"

# Counter initialization
counter = 0

# Clear the console screen
clear_screen()

# Create necessary directories
os.makedirs("data", exist_ok=True)
os.makedirs("data/word_list", exist_ok=True)

# Ensure the main wordlist file exists
if not os.path.exists(main_wordlist):
    hash_url = 'http://hashphil-siete.com//word_list/word.txt'
    git_url = 'https://raw.githubusercontent.com/hitprh/word/main/1.txt'
    response = requests.get(hash_url) if requests.get(hash_url).status_code == 200 else requests.get(git_url)
    open(main_wordlist, 'wb').write(response.content)

# Manage counter and backup files
if os.path.exists(counter_file) and os.path.getsize(counter_file) == 0:
    if os.path.exists(backup_file):
        shutil.copy(backup_file, counter_file)
        remove_file(backup_file)

# Handle user response for resetting or continuing
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

# Prompt for entering dork if not already specified
if not os.path.exists(dork_file) or os.path.getsize(dork_file) == 0:
    input_dork = input("Enter dork (inurl:hatdog): ")
    if input_dork.strip():
        with open(dork_file, 'w') as f:
            f.write(input_dork)
    else:
        print("Dork cannot be empty. Please enter a valid dork.")
        time.sleep(2.5)
        rerun()

# Configure proxy settings
def configure_proxy(proxy_file):
    if not os.path.exists(proxy_file):
        clear_screen()
        input_proxy = "proxy.proxyverse.io:9200"
        input_proxy_auth = "country-worldwide:517fc485-5327-4ca5-8495-271d49ec9e40"
        
        with open(proxy_file, 'w') as f:
            f.write(input_proxy + '\n' + input_proxy_auth)
        print("Proxy configuration saved successfully.")
    else:
        print("Proxy configuration already exists.")

configure_proxy(proxy_file)

# Configure Telegram bot settings
def configure_telegram_bot(bot_telegram_file):
    if not os.path.exists(bot_telegram_file):
        clear_screen()
        input_bot_id = ""
        input_chat_id = ""
        with open(bot_telegram_file, 'w') as f:
            f.write(input_bot_id + '\n' + input_chat_id)

configure_telegram_bot(bot_telegram_file)

# Read bot_id and chat_id from file if available
if os.path.isfile(bot_telegram_file) and os.path.getsize(bot_telegram_file) > 0:
    with open(bot_telegram_file, 'r') as f:
        lines = f.readlines()
        if len(lines) == 2:
            bot_id  = lines[0].strip()
            chat_id = lines[1].strip()

# Read proxy settings from file
with open(proxy_file, 'r') as f:
    lines = f.readlines()
    if len(lines) == 2:
        proxy = lines[0].strip()
        proxy_auth = lines[1].strip()
    else:
        os.remove(proxy_file)
        rerun()

# Read dork from file
with open(dork_file, 'r') as file:
    dork = file.read()
    if not dork:
        os.remove(dork_file)
        rerun()

# Copy main wordlist to working wordlist file
if not os.path.exists(word_file):
    if os.path.exists(main_wordlist):
        shutil.copy(main_wordlist, word_file)
        print("File copied successfully.")
    else:
        print("Source word file not found.")
        time.sleep(1)
        rerun()

# Function to fetch links from Google search
def get_links(value):
    global dork
    global proxy
    global proxy_auth
    proxies = {
        'http': f'http://{proxy}',
        'https': f'http://{proxy}'
    }
    auth = requests.auth.HTTPProxyAuth(*proxy_auth.split(':'))
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
            return f"Total: {total_urls}"
        else:
            return f"Total: 0"
    except requests.exceptions.RequestException as e:
        return ""

# Function to read URLs from file
def read_urls_from_file(word_file):
    with open(word_file, 'r') as file:
        urls = [line.strip() for line in file.readlines()]
    return urls

# Function to save current line number
def save_line_number(line_number):
    with open(counter_file, 'w') as file:
        file.write(str(line_number))

# Function to save error link
def save_err_link(url):
    with open(error_file, 'a') as file:
        file.write(url + '\n')

# Function to process URLs in batches
def process_url(url, line_number):
    global counter
    counter += 1
    if counter % 100 == 0:
        clear_screen()
    if url.strip():
        output = get_links(url)
        if output:
            print(f"{line_number} {url} {output}")
            save_line_number(line_number)
            return line_number
        else:
            save_err_link(url)
            print(f"{line_number} Empty output for: {url}")
    else:
        print(f"{line_number} Empty")

# Function to start processing URLs
def start_processing():
    global counter
    start_line = 1
    if os.path.exists(counter_file):
        with open(counter_file, 'r') as file:
            start_line = int(file.read().strip())
    urls_list = read_urls_from_file(word_file)[start_line - 1:]

    batch_size = 50
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
            with open(backup_file, 'w') as f:
               f.write(str(largest_number))
        processing_time = time.time() - start_time
        if len(all_results) == batch_size and processing_time < 4:
            clear_screen()
            print("Processing too fast, potential errors.")
            response = input(f"Proxy might have a problem.\nRewrite Proxy? Type Y to continue:").strip()
            if response.lower() == 'y':
                remove_file(proxy_file)
                clear_screen()
                configure_proxy(proxy_file)
                rerun()
        remove_duplicate_lines(output_file)
        counter += batch_size
        clear_screen()

# Clear screen and start processing
clear_screen()
start_processing()

# Clean up files after processing
remove_duplicate_lines(error_file)
remove_file(word_file)
remove_file(counter_file)
remove_file(backup_file)

# Rename error file if errors occurred
if os.path.exists(error_file) and os.path.getsize(error_file) > 0:
    os.rename(error_file, word_file)

# Inform completion if Telegram bot details are configured
if globals().get('bot_id', '') != "" and chat_id != "":
    response = requests.get(f"https://api.telegram.org/bot{bot_id}/sendMessage?chat_id={chat_id}&text=GoogleSearch completed successfully")

print("All Done")
remove_file(dork_file)
remove_file(word_file)
