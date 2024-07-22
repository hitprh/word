import os
import requests
import re
import time

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN' 
CHAT_ID = 'YOUR_CHAT_ID'  
FILES_FOLDER = '.' 
BASE_URL = f'https://api.telegram.org/bot{TOKEN}/'

if not os.path.exists(FILES_FOLDER):
    os.makedirs(FILES_FOLDER)

def send_message(chat_id, text):
    url = f'{BASE_URL}sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    requests.post(url, data=payload)

def get_updates(offset=None):
    url = f'{BASE_URL}getUpdates'
    params = {'timeout': 100, 'offset': offset}
    response = requests.get(url, params=params)
    return response.json()

def download_file(file_id, file_name):
    file_info_url = f'{BASE_URL}getFile?file_id={file_id}'
    file_info = requests.get(file_info_url).json()
    
    if 'result' not in file_info:
        print(f'Error retrieving file info for file_id {file_id}')
        return
    
    file_path = file_info['result']['file_path']
    file_url = f'https://api.telegram.org/file/bot{TOKEN}/{file_path}'

    # Streaming the file download
    with requests.get(file_url, stream=True) as r:
        r.raise_for_status()
        with open(os.path.join(FILES_FOLDER, file_name), 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)

    print(f'File saved as {file_name}')

def update_script(variable, value):
    script_path = __file__
    with open(script_path, 'r') as file:
        script = file.read()
    
    script = re.sub(f'{variable} = \'.*\'', f'{variable} = \'{value}\'', script)
    
    with open(script_path, 'w') as file:
        file.write(script)

def handle_updates(updates):
    for update in updates['result']:
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']

            if 'text' in message:
                text = message['text']
                if text.startswith('/start'):
                    send_message(chat_id, 'Send me any file and I will save it to the server.')
                    print(f'Start message sent to {chat_id}')
                elif text.startswith('/change_token'):
                    global TOKEN, BASE_URL
                    TOKEN = text.split()[1]
                    BASE_URL = f'https://api.telegram.org/bot{TOKEN}/'
                    update_script('TOKEN', TOKEN)
                    send_message(chat_id, 'Telegram bot token updated.')
                    print('Telegram bot token updated.')
                elif text.startswith('/change_chat_id'):
                    global CHAT_ID
                    CHAT_ID = text.split()[1]
                    update_script('CHAT_ID', CHAT_ID)
                    send_message(chat_id, 'Telegram chat ID updated.')
                    print('Telegram chat ID updated.')
            if 'document' in message:
                file_id = message['document']['file_id']
                file_name = message['document']['file_name']
                download_file(file_id, file_name)
                send_message(chat_id, f'File saved as {file_name}.')
            elif 'photo' in message:
                file_id = message['photo'][-1]['file_id']
                file_name = f'{file_id}.jpg'
                download_file(file_id, file_name)
                send_message(chat_id, f'Photo saved as {file_name}.')
            elif 'video' in message:
                file_id = message['video']['file_id']
                file_name = message['video'].get('file_name', f'{file_id}.mp4')
                download_file(file_id, file_name)
                send_message(chat_id, f'Video saved as {file_name}.')
            elif 'forward_from' in message:
                if 'document' in message:
                    file_id = message['document']['file_id']
                    file_name = message['document']['file_name']
                    download_file(file_id, file_name)
                    send_message(chat_id, f'Forwarded file saved as {file_name}.')
                    print(f'Forwarded file {file_name} saved.')
                elif 'photo' in message:
                    file_id = message['photo'][-1]['file_id']
                    file_name = f'{file_id}.jpg'
                    download_file(file_id, file_name)
                    send_message(chat_id, f'Forwarded photo saved as {file_name}.')
                    print(f'Forwarded photo {file_name} saved.')
                elif 'video' in message:
                    file_id = message['video']['file_id']
                    file_name = message['video'].get('file_name', f'{file_id}.mp4')
                    download_file(file_id, file_name)
                    send_message(chat_id, f'Forwarded video saved as {file_name}.')
                    print(f'Forwarded video {file_name} saved.')

def send_file_to_server():
    offset = None
    try:
        while True:
            updates = get_updates(offset)
            if 'result' in updates and len(updates['result']) > 0:
                handle_updates(updates)
                offset = updates['result'][-1]['update_id'] + 1
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")

def change_token():
    global TOKEN, BASE_URL
    TOKEN = input('Enter new Telegram bot token: ')
    BASE_URL = f'https://api.telegram.org/bot{TOKEN}/'
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
        print("1. Send file to server")
        print("2. Change Telegram bot token")
        print("3. Change Telegram chat ID")
        print("4. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            send_file_to_server()
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
