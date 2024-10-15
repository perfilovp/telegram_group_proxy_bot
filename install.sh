#/bin/bash
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <TOKEN> <GROUP_ID>"
    exit 1
fi

TOKEN=$1
GROUP_ID=$2

sudo useradd -r -G telegrambot telegrambot -r -s /bin/false 
sudo usermod -s /usr/sbin/nologin telegrambot

mkdir -p /opt/telegram-bot
cp -r * /opt/telegram-bot
cd /opt/telegram-bot
python3 -m venv venv

source /opt/telegram-bot/venv/bin/activate

pip3 install --upgrade pip
pip3 install -r /opt/telegram-bot/requirements.txt

sudo chmod -R 755 /opt/telegram-bot
sudo chown -R telegrambot:telegrambot /opt/telegram-bot

sed -e "s/{{TOKEN}}/$TOKEN/g" -e "s/{{GROUP_ID}}/$GROUP_ID/g" telegram-bot._service_ > telegram-bot.service
cp /opt/telegram-bot/telegram-bot.service /etc/systemd/system/telegram-bot.service

# sudo systemctl disable telegram-bot
# sudo systemctl daemon-reload
sudo systemctl enable telegram-bot
sudo systemctl daemon-reload
sudo systemctl restart telegram-bot
