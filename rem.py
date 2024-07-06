from urllib.parse import urlparse

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

def main():
    filename = input("Enter the filename (e.g., 1.txt): ")

    urls = read_urls_from_file(filename)

    # Remove duplicates based on domain
    unique_urls = remove_duplicates_by_domain(urls)

    
    write_urls_to_file(filename, unique_urls)

if __name__ == "__main__":
    main()
