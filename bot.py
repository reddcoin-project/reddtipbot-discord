import discord
from tipper.tipper import *

from pycoingecko import CoinGeckoAPI
# load CoinGecko API
cg = CoinGeckoAPI()

import qrcode
import io
import json

# load configs
with open("config.json") as json_data_file:
    config = json.load(json_data_file)
# set transaction fee
txfee = config['wallet']['txfee']

client = discord.Client()

prefix = config['commandPrefix']
botChannels = config['discord']['botChannelIds']
botChannelsStr = ''
for botChannel in botChannels:
    botChannelsStr += '<#' + botChannel + '> '

tipbotChannelMsg = 'Please use ' + botChannelsStr + 'channels for tipbot commands.'
helpmsg = """**/help** or **/commands** - display this message\n
**/register** - register to receive tip from rain\n
**/stats** - get ReddTipbot and ReddCoin network statistics\n
**/price** - get current price of ReddCoin from CoinGecko\n
**/deposit** or **/addr** - get address for your deposits\n
**/balance** - get your balance\n
**/balance unconf** - get your balance including unconfirmed balance\n
**/tip <@user> <amount>** - mention a user with @ and then the amount to tip them\n
**/withdraw <amount> <address>** - withdraw coins to specified address\n
**/rain <amount>** - tip all registered users\n
**/crowdfund <amount>** - help us get listed on more exchanges\n
**/donate <amount>** - donate to support charities"""

latestWalletLink = 'https://download.reddcoin.com/bin/'
reddExplorer = 'https://live.reddcoin.com/tx/'
crowdfundAddress = 'RqQ4qnJCAcqxPqsvMtyJx73eyVyWtpjN73'
crowdfundProgressLink = 'https://redd.love/funding/#crowdfund'
donationAddress = 'Recrcq8moZjbEHVoJx6JiQ2mfZkQnktvnf'
donationProgressLink = 'https://rdd.tokenview.com/en/address/Recrcq8moZjbEHVoJx6JiQ2mfZkQnktvnf'

@client.event
async def on_message(message):
    # make sure bot doesnt reply to itself
    if message.author == client.user:
        return
    
    # respond with reddcoin price
    if message.content.startswith(prefix + 'price'):
        if str(message.channel.id) in botChannels or message.channel.type is discord.ChannelType.private:
            price_response = cg.get_price(ids='reddcoin', vs_currencies='usd,btc')
            price = price_response['reddcoin']['usd']
            price_btc = price_response['reddcoin']['btc']
            embed = discord.Embed(title='**:chart_with_upwards_trend::money_with_wings: Reddcoin (RDD) Price - CoinGecko :money_with_wings::chart_with_upwards_trend:**', color=0xE31B23) #,color=Hex code
            embed.add_field(name='__BTC__', value='**' + "%.8f"%(price_btc) + '**', inline=False)
            embed.add_field(name='__USD__', value='**' + str(price) + '**', inline=False)
            return await message.channel.send(embed=embed)
        else:
            return await message.reply(tipbotChannelMsg)
    
    # respond with all the available commands 
    if message.content.startswith(prefix + 'help') or message.content.startswith(prefix + 'commands'):
        if str(message.channel.id) in botChannels or message.channel.type is discord.ChannelType.private:            
            embed = discord.Embed(title='**<:redd:757904864255672400>:robot: Reddcoin Tipbot :robot:<:redd:757904864255672400>**', color=0xE31B23) #,color=Hex code
            embed.add_field(name='__Commands__', value=helpmsg, inline=False)
            embed.add_field(name='__Withdrawal Fee__', value='**' + str(txfee) + ' RDD/kB**', inline=False)            
            return await message.channel.send(embed=embed)
        else:
            return await message.reply(tipbotChannelMsg)

    # respond with reddcoin statistics
    if message.content.startswith(prefix + 'stats'):
        if str(message.channel.id) in botChannels or message.channel.type is discord.ChannelType.private:
            stats = getStats()
            users = getUsers()
            embed = discord.Embed(title='**:bar_chart: Statistics :bar_chart:**', color=0xE31B23) #,color=Hex code
            embed.add_field(name='__Total @' + client.user.name + ' Users__', value='**' + str(len(users)) + '**', inline=False)
            embed.add_field(name='__Block Height__', value='**' + str(stats[0]) + '**', inline=False)
            embed.add_field(name='__PoSV v2 Staking Multiplier__', value='**' + str(stats[1]) + '**', inline=False)
            embed.add_field(name='____Latest Core Wallet Version____', value='**' + latestWalletLink + '**', inline=False)
            return await message.channel.send(embed=embed)
        else:
            return await message.reply(tipbotChannelMsg)

    # process deposit/addr/register command
    if message.content.startswith(prefix + 'deposit') or message.content.startswith(prefix + 'addr') or message.content.startswith(prefix + 'register'):
        if str(message.channel.id) in botChannels or message.channel.type is discord.ChannelType.private:
            account = str(message.author.id)
            accounts = getUsers()
            address = ''
            registerTitle = ''
            
            # get new address only if an account does not exit in the wallet
            if account in accounts:
                address = getAddress(account)
                registerTitle = '**:card_index::white_check_mark: You have already been registered! :white_check_mark::card_index:**'
            else:
                address = getNewAddress(account)
                registerTitle = '**:card_index::white_check_mark: Registered! :white_check_mark::card_index:**'

            if message.content.startswith(prefix + 'register'):
                embed = discord.Embed(title=registerTitle, color=0xE31B23) #,color=Hex code
                embed.add_field(name='__User__', value='<@' + account + '>', inline=False)
                return await message.reply(embed=embed)
            else:
                # generate qr code from deposit address
                qr = qrcode.make(address)
                # temporarily save qr in memory
                arr = io.BytesIO()
                qr.save(arr, format='PNG')
                arr.seek(0)

                file = discord.File(arr, filename='deposit-qr.png')
                embed = discord.Embed(title='**:bank::card_index::moneybag: Your Deposit Address :moneybag::card_index::bank:**', color=0xE31B23) #,color=Hex code
                embed.add_field(name='__User__', value='<@' + account + '>', inline=False)
                embed.add_field(name='__Address__', value='**' + address + '**', inline=False)
                embed.set_image(url="attachment://deposit-qr.png")
                # return await message.author.send(embed=embed) # reply with private message
                return await message.reply(file=file, embed=embed) # reply in channel
        else:
            return await message.reply(tipbotChannelMsg)

    # respond with balance including 0 confirmation
    if message.content.startswith(prefix + 'balance unconf'): # 0 conf. balance
        if str(message.channel.id) in botChannels or message.channel.type is discord.ChannelType.private:
            account = str(message.author.id)
            balance = getBalance(account,0)
            strBalance = str(balance if balance > 0 else 0)
            embed = discord.Embed(title='**:bank::money_with_wings::moneybag: Your Balance :moneybag::money_with_wings::bank:**', color=0xE31B23) #,color=Hex code
            embed.add_field(name='__User__', value='<@' + account + '>', inline=False)
            embed.add_field(name='__Balance (incl. 0 conf.)__', value='**' + strBalance + ' RDD**', inline=False)
            return await message.reply(embed=embed) # reply in channel
        else:
            return await message.reply(tipbotChannelMsg)

    # respond with available balance
    if message.content.startswith(prefix + 'balance'):
        if str(message.channel.id) in botChannels or message.channel.type is discord.ChannelType.private:
            account = str(message.author.id)
            balance = getBalance(account)
            strBalance = str(balance if balance > 0 else 0)
            embed = discord.Embed(title='**:bank::money_with_wings::moneybag: Your Balance :moneybag::money_with_wings::bank:**', color=0xE31B23) #,color=Hex code
            embed.add_field(name='__User__', value='<@' + account + '>', inline=False)
            embed.add_field(name='__Balance__', value='**' + strBalance + ' RDD**', inline=False)
            return await message.reply(embed=embed)
        else:
            return await message.reply(tipbotChannelMsg)

    # process tip command
    if message.content.startswith(prefix + 'tip '):
        if str(message.channel.id) in botChannels or message.channel.type is discord.ChannelType.private:
            tipper = str(message.author.id)
            content = message.content.split()[1:]
            toTipMention = content[0]
            toTip = toTipMention.replace('<@','').replace('>','') #remove <@> from ID
            amount = content[1]

            #catching errors
            if not toTipMention[:2]=='<@':
                return await message.reply("{0.author.mention}, invalid account.".format(message))
            try:
                amount = float(amount)
            except ValueError:
                return await message.reply("{0.author.mention}, invalid amount.".format(message))

            try:
                tip(tipper,toTip,amount)
                embed = discord.Embed(title=':money_with_wings::moneybag: Tip :moneybag::money_with_wings:', color=0xE31B23) #,color=Hex code
                embed.add_field(name='__Amount__', value='**' + str(amount) + ' RDD**', inline=False)
                embed.add_field(name='__Sender__', value='**<@' + tipper + '>**', inline=False)
                embed.add_field(name='__Receiver__', value='**' + toTipMention + '**', inline=False)
                return await message.channel.send(embed=embed)                
            except ValueError:
                return await message.reply("{0.author.mention}, insufficient balance.".format(message))
        else:
            return await message.reply(tipbotChannelMsg)

    # process withdraw and reply with transaction info
    if message.content.startswith(prefix + 'withdraw '):
        if str(message.channel.id) in botChannels or message.channel.type is discord.ChannelType.private:
            account = str(message.author.id)
            amount = message.content.split()[1]
            address = message.content.split()[2]
            
            #catching errors again
            if not validateAddress(address):
                return await message.reply("{0.author.mention}, invalid address.".format(message))
            
            try:
                amount = float(amount)
            except ValueError:
                return await message.reply("{0.author.mention}, invalid amount.".format(message))

            try:
                txid = withdraw(account,address,amount)
                embed = discord.Embed(title=':outbox_tray::moneybag: Withdrawal :moneybag::outbox_tray:', color=0xE31B23) #,color=Hex code
                embed.add_field(name='__Amount__', value='**' + str(amount) + ' RDD**', inline=False)
                embed.add_field(name='__User__', value='**<@' + account + '>**', inline=False)
                embed.add_field(name='__Receiving Address__', value='**' + address + '**', inline=False)
                embed.add_field(name='__Transaction__', value='**' + reddExplorer + txid + '**', inline=False)
                embed.add_field(name='__Fee__', value='**' + str(txfee) + ' RDD**', inline=False)
                return await message.reply(embed=embed)
            except ValueError:
                return await message.reply("{0.author.mention}, insufficient balance.".format(message))
        else:
            return await message.reply(tipbotChannelMsg)

    # process rain command
    if message.content.startswith(prefix + 'rain '):
        if str(message.channel.id) in botChannels or message.channel.type is discord.ChannelType.private:
            account = str(message.author.id)
            amount = float(message.content.split()[1])

            # minimum rain amount is 1 RDD
            if amount < 1:
                return await message.reply("{0.author.mention}, the amount must be bigger than 1 RDD.".format(message))
            # catching errors again
            try:
                amount = float(amount)
            except ValueError:
                return await message.reply("{0.author.mention}, invalid amount.".format(message))

            try:
                tippedUsers = ''
                # get all registered users from the wallet
                registeredUsers = getUsers()
                for key in registeredUsers:
                    if str(key) != account and str(key) != "":
                        tippedUsers += '<@' + str(key) + '> '
                eachtip = rain(account,amount) #the function returns each individual tip amount so this just makes it easier
                embed = discord.Embed(title=':cloud_rain::money_with_wings: Tipbot Rain :money_with_wings::cloud_rain:', color=0xE31B23) #,color=Hex code
                embed.add_field(name='__Amount__', value='**' + str(eachtip) + ' RDD**', inline=False)
                embed.add_field(name='__Sender__', value='**<@' + account + '>**', inline=False)
                embed.add_field(name='__Receivers__', value='**' + tippedUsers[0:400] + '...**', inline=False)
                embed.set_footer(text="**Please register (/register) if you would like to receive tip from rain.")
                return await message.channel.send(embed=embed)                
            except ValueError:
                return await message.reply("{0.author.mention}, insufficient balance.".format(message))
        else:
            return await message.reply(tipbotChannelMsg)

    # process crowdfund command - send donated amount to crowdfund address
    if message.content.startswith(prefix + 'crowdfund '):
        if str(message.channel.id) in botChannels or message.channel.type is discord.ChannelType.private:
            account = str(message.author.id)
            amount = float(message.content.split()[1])

            try:
                amount = float(amount)
            except ValueError:
                return await message.reply("{0.author.mention}, invalid amount.".format(message))

            try:
                txid = withdraw(account,crowdfundAddress,amount)
                embed = discord.Embed(title=':raised_hands::pray: Thank you for your support! :pray::raised_hands:', color=0xE31B23) #,color=Hex code
                embed.add_field(name='__Amount__', value='**' + str(amount) + ' RDD**', inline=False)
                embed.add_field(name='__Donor__', value='**<@' + account + '>**', inline=False)
                embed.add_field(name='__Crowdfund Address__', value='**' + crowdfundAddress + '**', inline=False)
                embed.add_field(name='__Transaction__', value='**' + reddExplorer + txid + '**', inline=False)
                embed.add_field(name='__Fee__', value='**' + str(txfee) + ' RDD**', inline=False)
                embed.add_field(name='__Crowdfund Progress__', value='**' + crowdfundProgressLink + '**', inline=False)
                return await message.reply(embed=embed)
            except ValueError:
                return await message.reply("{0.author.mention}, insufficient balance.".format(message))
        else:
            return await message.reply(tipbotChannelMsg)

    # process donate command - send donated amount to crowdfund address
    if message.content.startswith(prefix + 'donate '):
        if str(message.channel.id) in botChannels or message.channel.type is discord.ChannelType.private:
            account = str(message.author.id)
            amount = float(message.content.split()[1])

            try:
                amount = float(amount)
            except ValueError:
                return await message.reply("{0.author.mention}, invalid amount.".format(message))

            try:
                txid = withdraw(account,crowdfundAddress,amount)
                embed = discord.Embed(title=':raised_hands::pray: Thank you for your support! :pray::raised_hands:', color=0xE31B23) #,color=Hex code
                embed.add_field(name='__Amount__', value='**' + str(amount) + ' RDD**', inline=False)
                embed.add_field(name='__Donor__', value='**<@' + account + '>**', inline=False)
                embed.add_field(name='__Crowdfund Address__', value='**' + donationAddress + '**', inline=False)
                embed.add_field(name='__Transaction__', value='**' + reddExplorer + txid + '**', inline=False)
                embed.add_field(name='__Fee__', value='**' + str(txfee) + ' RDD**', inline=False)
                embed.add_field(name='__Donation Progress__', value='**' + donationProgressLink + '**', inline=False)
                return await message.reply(embed=embed)
            except ValueError:
                return await message.reply("{0.author.mention}, insufficient balance.".format(message))
        else:
            return await message.reply(tipbotChannelMsg)
    
    # test command
    # if message.content.startswith(prefix + 'test'):
    #     account = str(message.author.id)
    #     embed = discord.Embed(title=':cloud_rain::money_with_wings: Tipbot Rain :money_with_wings::cloud_rain:', color=0xE31B23) #,color=Hex code
    #     embed.add_field(name='', value='**<@' + account + '>**', inline=False)
    #     return await message.channel.send(embed=embed)
        
    
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Game(name="Redd"))

client.run(config['discord']['botToken'])

