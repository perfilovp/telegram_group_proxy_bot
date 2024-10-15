

# Simple proxy telegram bot 
 [ USER <- private chat -> bot ] <= sync => [ private group ]

## Functionality: 
1. Bot is open for communication with multiple end-users
2. Bot is forwarding every end-user message to the group chat. Every message contains end-user name and id. 
3. Users in the group chat could forward messages via bot by specifying id of the end user. Message should look like this "%12312312319249% response", where 12312312319249 is id of the user. 
4. To add user into black list, type in group: `block_user%01231231231%`, user would be saved into blocket_users.txt 

## Installation: 
clone the project: `git clone .`

### as a service 
Script would create the environment and deploy telegram-bot.service to systemd: 
`sudo ./install.sh TOKEN GROUP_ID` , where TOKEN is your bot token, and GROUP_ID is your group id

like `sudo ./install.sh 123123123:asdfasdfaasdfasdfasdfasdf -01231231231`

### one-off run 
`/opt/telegram-bot/venv/bin/python /opt/telegram-bot/run.py --TOKEN 123123123:asdfasdfaasdfasdfasdfasdf --GROUP_ID -01231231231`

## Status 
`systemctl status telegram-bot.service`

## Troubleshooting
`journalctl -xeu telegram-bot.service`

## Uninstall 
```
systemctl disable telegram-bot 
rm -rf /opt/telegram-bot
```



