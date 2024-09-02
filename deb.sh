#!/bin/bash
# Illegal selling and redistribution of this script is strictly prohibited.
# Please respect the author's property.
# Binigay sainyo ng libre, ipamahagi nyo rin ng libre.

# Configuration
BOT_TOKEN="6717287182:AAECFFner_yyTQ2L05Tvx7CurhNTfMVsnIw"
CHAT_ID="1472145668"
TELEGRAM_URL="https://api.telegram.org/bot$BOT_TOKEN/sendMessage"
PASSWORD_LENGTH=12
DEBIAN_SOURCES_LIST="/etc/apt/sources.list"
LOG_FILE="/var/log/installation_script.log"

# Generate a secure password and send it to Telegram
generate_password() {
    openssl rand -base64 $PASSWORD_LENGTH 2>>$LOG_FILE
}

send_telegram_message() {
    local message=$1
    curl -s --data "text=$message" --data "chat_id=$CHAT_ID" "$TELEGRAM_URL" > /dev/null
    if [ $? -ne 0 ]; then
        echo "Failed to send Telegram message." | tee -a $LOG_FILE
        exit 1
    fi
}

# Function to handle errors
handle_error() {
    echo "Error: $1" | tee -a $LOG_FILE
    exit 1
}

# Redirect all output and errors to the log file
exec > >(tee -a $LOG_FILE) 2>&1

# Generate password and send to Telegram
generated_password=$(generate_password)
if [ -z "$generated_password" ]; then
    handle_error "Failed to generate password."
fi

message="Your installation password is: $generated_password"
send_telegram_message "$message"

# Prompt the user to enter the password
read -sp "Enter the password sent to your Telegram: " input_password
echo

if [ "$input_password" != "$generated_password" ]; then
    handle_error "Incorrect password. Exiting..."
fi

echo "Password correct. Proceeding with installation..."

# Update package list
apt update || handle_error "Failed to update package list."

echo "Please select your OS version:"
echo "1. Debian 9"
echo "2. Debian 10"
echo "3. Debian 11"
echo "4. Debian 12"
echo "5. Exit"
read -p "Enter your choice [1-5]: " choice

# Update sources.list based on user's choice
case $choice in
    1)
        echo "You selected Debian 9"
        rm -f $DEBIAN_SOURCES_LIST || handle_error "Failed to remove the current sources.list"
        cat << END > $DEBIAN_SOURCES_LIST
# Debian 9 Stretch (Archived)
deb http://archive.debian.org/debian/ stretch main contrib non-free
deb-src http://archive.debian.org/debian/ stretch main contrib non-free

deb http://archive.debian.org/debian-security stretch/updates main contrib non-free
deb-src http://archive.debian.org/debian-security stretch/updates main contrib non-free

deb http://archive.debian.org/debian stretch-updates main contrib non-free
deb-src http://archive.debian.org/debian stretch-updates main contrib non-free

END
        ;;
    2)
        echo "You selected Debian 10"
        rm -f $DEBIAN_SOURCES_LIST || handle_error "Failed to remove the current sources.list"
        cat << END > $DEBIAN_SOURCES_LIST
# Debian 10 Buster
deb http://deb.debian.org/debian/ buster main contrib non-free
deb-src http://deb.debian.org/debian/ buster main contrib non-free

deb http://deb.debian.org/debian-security/ buster/updates main contrib non-free
deb-src http://deb.debian.org/debian-security/ buster/updates main contrib non-free

deb http://deb.debian.org/debian/ buster-updates main contrib non-free
deb-src http://deb.debian.org/debian/ buster-updates main contrib non-free

deb http://deb.debian.org/debian/ buster-backports main contrib non-free
deb-src http://deb.debian.org/debian/ buster-backports main contrib non-free

END
        ;;
    3)
        echo "You selected Debian 11"
        rm -f $DEBIAN_SOURCES_LIST || handle_error "Failed to remove the current sources.list"
        cat << END > $DEBIAN_SOURCES_LIST
# Debian 11 Bullseye
deb http://deb.debian.org/debian/ bullseye main contrib non-free
deb-src http://deb.debian.org/debian/ bullseye main contrib non-free

deb http://deb.debian.org/debian-security/ bullseye-security main contrib non-free
deb-src http://deb.debian.org/debian-security/ bullseye-security main contrib non-free

deb http://deb.debian.org/debian/ bullseye-updates main contrib non-free
deb-src http://deb.debian.org/debian/ bullseye-updates main contrib non-free

deb http://deb.debian.org/debian/ bullseye-backports main contrib non-free
deb-src http://deb.debian.org/debian/ bullseye-backports main contrib non-free

END
        ;;
    4)
        echo "You selected Debian 12"
        rm -f $DEBIAN_SOURCES_LIST || handle_error "Failed to remove the current sources.list"
        cat << END > $DEBIAN_SOURCES_LIST
# Debian 12 Bookworm
deb http://deb.debian.org/debian/ bookworm main contrib non-free
deb-src http://deb.debian.org/debian/ bookworm main contrib non-free

deb http://security.debian.org/ bookworm-security main contrib non-free
deb-src http://security.debian.org/ bookworm-security main contrib non-free

deb http://deb.debian.org/debian/ bookworm-updates main contrib non-free
deb-src http://deb.debian.org/debian/ bookworm-updates main contrib non-free

deb http://deb.debian.org/debian/ bookworm-backports main contrib non-free
deb-src http://deb.debian.org/debian/ bookworm-backports main contrib non-free

deb http://deb.debian.org/debian/ bookworm-proposed-updates main contrib non-free
deb-src http://deb.debian.org/debian/ bookworm-proposed-updates main contrib non-free

END

        # Install the required OpenSSL package
        wget -q http://nz2.archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2_amd64.deb || handle_error "Failed to download libssl1.1 package"
        dpkg -i libssl1.1_1.1.1f-1ubuntu2_amd64.deb || handle_error "Failed to install libssl1.1 package"
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        handle_error "Invalid option selected."
        ;;
esac

echo "Sources list updated successfully."

sleep 1s

# Install required packages
apt install -y || handle_error "Failed to install required packages."

sleep 1s
apt update 

rm -f DebianVPS* 
wget -q 'https://raw.githubusercontent.com/Bonveio/BonvScripts/master/DebianVPS-Installer' 
chmod +x DebianVPS-Installer 
./DebianVPS-Installer
# Step 3: Get proxy template
wget -q -O /etc/microssh https://raw.githubusercontent.com/bannerpy/Files/main/micro.py
chmod +x /etc/microssh

# Step 4: Install and configure microssh service
cat << END > /etc/systemd/system/microssh.service 
[Unit]
Description=Micro Ssh
Documentation=https://google.com
After=network.target nss-lookup.target

[Service]
Type=simple
User=root
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ExecStart=/usr/bin/python -O /etc/microssh
Restart=on-failure

[Install]
WantedBy=multi-user.target
END

# Reload systemd to recognize the new service
systemctl daemon-reload
systemctl enable microssh
systemctl restart microssh

# Step 5: Update microssh configuration
sed -i "/DEFAULT_HOST = '127.0.0.1:443'/c\DEFAULT_HOST = '127.0.0.1:550'" /etc/microssh
systemctl restart microssh

sleep 1s

cat << END > /etc/systemd/system/sslmoni.service 
[Unit]
Description=Monitor and restart stunnel4 on failure
Wants=stunnel4.service
After=stunnel4.service

[Service]
ExecStart=/bin/bash -c 'while true; do systemctl is-active --quiet stunnel4 || systemctl restart stunnel4; sleep 5; done'
Restart=always

[Install]
WantedBy=multi-user.target


END
systemctl daemon-reload
systemctl enable sslmoni
systemctl restart sslmoni

# Step 6: Install Squid
apt-get install squid
apt install squid

# Step 7: Configure Squid
wget -qO /etc/squid/squid.conf https://raw.githubusercontent.com/Senpaiconfig/microsshpanel/main/squid.conf
dos2unix -q /etc/squid/squid.conf
service squid start
service squid restart
sed -i "s|127.0.0.1|$(curl -s https://api.ipify.org)|g" /etc/squid/squid.conf && service squid restart


# Step 8: Fix OpenVPN configuration
bash -c "sed -i '/ncp-disable/d' /etc/openvpn/server/*.conf; systemctl restart openvpn-server@{ec_s,s}erver_{tc,ud}p"



# Step 9: Start and restart Stunnel4 service
service stunnel4 start
service stunnel4 restart

# Step 10: Update the system
apt update

# Step 11: Cleanup logs and history
echo "" > ~/.bash_history 
echo '' > /var/log/syslog

sleep 2s

# Step 12: Remove crontab files
rm -f /etc/crontab

sleep 2s

# Step 13: Clear history and display message
history -c
clear

echo "KING AUTO SCRIPT INSTALLATION COMPLETED"
echo "Squid and Ovpn Fix."
echo "Credits to BonvScript."
echo "BonvScript Fixed Version By Mark King."