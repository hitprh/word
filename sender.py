import os
import requests
import re

FILES_FOLDER = '.'  
BASE_URL = 'https://api.telegram.org/bot'

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'  
CHAT_ID = 'YOUR_CHAT_ID' 

def list_files():
    files = sorted(os.listdir(FILES_FOLDER))
    if not files:
        print('No files found.')
        return []

    for i, file in enumerate(files):
        print(f'{i+1}. {file}')
    return files

def send_message(text):
    url = f'{BASE_URL}{TOKEN}/sendMessage'
    payload = {'chat_id': CHAT_ID, 'text': text}
    requests.post(url, data=payload)

def send_document(file_path):
    url = f'{BASE_URL}{TOKEN}/sendDocument'
    files = {'document': open(file_path, 'rb')}
    data = {'chat_id': CHAT_ID}
    requests.post(url, files=files, data=data)

def get_file():
    files = list_files()
    if not files:
        return

    try:
        file_index = int(input('Enter the file number to send: ')) - 1
        if file_index < 0 or file_index >= len(files):
            print('Invalid file number.')
            return
        
        file_path = os.path.join(FILES_FOLDER, files[file_index])
        send_document(file_path)
        send_message(f'')
    except (IndexError, ValueError):
        print('Invalid input.')

def update_script(variable, value):
    script_path = __file__
    with open(script_path, 'r') as file:
        script = file.read()
    
    script = re.sub(f'{variable} = \'.*\'', f'{variable} = \'{value}\'', script)
    
    with open(script_path, 'w') as file:
        file.write(script)

def change_token():
    global TOKEN
    TOKEN = input('Enter new Telegram bot token: ')
    update_script('TOKEN', TOKEN)
    print('Telegram bot token updated.')

def change_chat_id():
    global CHAT_ID
    CHAT_ID = input('Enter new Telegram chat ID: ')
    update_script('CHAT_ID', CHAT_ID)
    print('Telegram chat ID updated.')

def main():
    while True:
        print("\nMenu:")
        print("1. Get file")
        print("2. Change Telegram bot token")
        print("3. Change Telegram chat ID")
        print("4. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            get_file()
        elif choice == '2':
            change_token()
        elif choice == '3':
            change_chat_id()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
