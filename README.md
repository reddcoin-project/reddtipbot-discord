# [ReddTipbot](https://discord.gg/XKpMjdrR7w) - ReddCoin Discord Tipbot

Commands:
- **/help** or **/commands** - display this message
- **/price** - get current price of Reddcoin from CoinGecko
- **/deposit** or **/addr** - get reddcoin address for your deposits and receive tip from rain
- **/balance** - get your balance
- **/balance unconf** - get your balance including unconfirmed balance
- **/tip <@user> <amount>** - mention a user with @ and then the amount to tip them
- **/withdraw <amount> <address>** - withdraw coins to specified address
- **/rain <amount>** - tip all registered users (/deposit to register)
- **/crowdfund <amount>** - crowdfund to help us get listed on more exchanges
- **/donate <amount>** - donate to support charities

## Bot Setup

1) Create a bot and get the bots Token and Client ID: https://discordapp.com/developers/applications/me

    1) After going to the link above click “new application”. Give it a name, picture, and description.

    2) On the side bar navigation menu click "Bot" Click “Add Bot” and click “Yes, Do It!” when the dialog pops up.

    3) Copy down the token used on this page to login and Client ID on the general info page to invite your new bot to your discord server.

2) invite the bot to your server using the link below and entering the Client ID or generate your own [Here:link:](https://discordapi.com/permissions.html)

```
https://discordapp.com/oauth2/authorize?client_id=INSERT_CLIENT_ID_HERE&scope=bot&permissions=27648
```

## Edit Files

1) Edit and rename `config.json.example` to `config.json`. You will use the same info in the next step.

    ```
    {
        "wallet":{
            "host":"127.0.0.1",
            "user":"RPC-USERNAME",
            "password":"RPC-PASSWORD",
            "port":45443,
            "txfee":0.002
        },
        "discord":{
            "botToken":"DISCORD-BOT-TOKEN",
            "botChannelIds": ["DISCORD-BOT-CHANNEL1", "DISCORD-BOT-CHANNEL2"]
        },
        "commandPrefix": "/"
    }
    ```

2) Set up wallet's config file

    1) In most cases, your wallets data folder can be found in 
      - Windows: `%appdata%`

        (default Roaming Folder), `e.g. C:\Users\USER\AppData\Roaming\reddcoin`
      - Linux: /home/user/.reddcoin

    2) Edit or create your `COIN.conf` file (Where "COIN" is the coin name) to include the following:

        ```
        server=1
        par=1
        rpcbind=127.0.0.1
        rpcallowip=127.0.0.1
        rpcport=45443
        rpcuser=<Same-as-you-set-in-config.json>
        rpcpassword=<Same-as-you-set-in-config.json>
        ```

        1) NOTE: for `paytxfee` to actually work properly use the console or rpc command `settxfee number` number being the fee of course.

        2) NOTE: Disable staking if not supporting

          ```
          staking=0
          enableaccounts=1
          ```

## Development

### Install

Dependencies:
- pip3 install discord.py
- pip3 install requests
- pip3 install python-bitcoinrpc
- pip3 install pycoingecko
- pip3 install qrcode

### Run

```
python3 bot.py
```

## Credits

https://github.com/nicolespin/tipbot_digibyte_discord