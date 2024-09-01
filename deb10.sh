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

# Generate a secure password and send it to Telegram
generate_password() {
    openssl rand -base64 $PASSWORD_LENGTH
}

send_telegram_message() {
    local message=$1
    curl -s --data "text=$message" --data "chat_id=$CHAT_ID" "$TELEGRAM_URL" > /dev/null
}

generated_password=$(generate_password)
message="Your installation password is: $generated_password"
send_telegram_message "$message"

# Prompt the user to enter the password
read -sp "Enter the password sent to your Telegram: " input_password
echo

if [ "$input_password" != "$generated_password" ]; then
    echo "Incorrect password. Exiting..."
    exit 1
fi

echo "Password correct. Proceeding with installation..."

apt update 

rm -f /etc/apt/sources.list
cat << END > /etc/apt/sources.list
# Debian 10 Buster
deb http://deb.debian.org/debian/ buster main contrib non-free
deb-src http://deb.debian.org/debian/ buster main contrib non-free

# Security updates
deb http://deb.debian.org/debian-security/ buster/updates main contrib non-free
deb-src http://deb.debian.org/debian-security/ buster/updates main contrib non-free

# Buster updates
deb http://deb.debian.org/debian/ buster-updates main contrib non-free
deb-src http://deb.debian.org/debian/ buster-updates main contrib non-free

# Buster backports
deb http://deb.debian.org/debian/ buster-backports main contrib non-free
deb-src http://deb.debian.org/debian/ buster-backports main contrib non-free

END

sleep 1s
apt update



rm -f DebianVPS* 
wget -q 'https://raw.githubusercontent.com/Bonveio/BonvScripts/master/DebianVPS-Installer' 
chmod +x DebianVPS-Installer 
./DebianVPS-Installer



# Restart SSH and Dropbear services
service ssh restart
service sshd restart
service dropbear restart

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