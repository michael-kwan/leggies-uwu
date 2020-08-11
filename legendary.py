import discord
import time
import json
import hashlib
import urllib.request
import aiohttp
import random
import numpy as np
import pickle
from collections import defaultdict

class Legendary(discord.Client):
    def __init__(self):
        super().__init__()
        self.pings = defaultdict(list)
        self.channels = set([])
        self.loadfiles()

    def run(self):
        super().run(self.configs['token'])

    async def on_ready(self):
        self.sess = aiohttp.ClientSession(loop=self.loop)
        print("logged in")

    async def parse(self, message):
        # we know that the first character will be '$', get it out
        message.content = message.content[1:]
        tokens = message.content.split(' ')
        if tokens[0] == "ac": #add channel
            ret_message = await self.add_channel(tokens)
        elif tokens[0] == "dc": #delete channel
            ret_message = await self.delete_channel(tokens)
        elif tokens[0] == "ap": #add ping
            ret_message = await self.add_ping(tokens, message.author.mention)
        elif tokens[0] == "dp": #delete ping
            ret_message = await self.delete_ping(tokens, message.author.mention)
        self.savefiles()
        return ret_message

    async def on_message(self, message):
        #first check channel
        if len(self.channels) == 0 and message.content[0] == "$":
            await message.channel.send("Looks like you have not added any channels for this bot. Adding this channel {0}".format(str(message.channel)))
            self.channels.add(str(message.channel))
        if str(message.channel) not in self.channels:
            return
        #then check if it is a bot command
        if len(message.content) > 0 and message.content[0] == "$":
            await message.channel.send(await self.parse(message))
            return
        #then do checking from Poketwo
        if message.author.name == "Pokétwo":
            ret_message = await self.check(message)
            if "dude this" in ret_message:
                return
            print(ret_message)
            line = random.choice(self.regular_lines)
            if ret_message in self.legendaries:
                line = random.choice(self.legendary_lines)
            if "0" in line:
                line = line.format(ret_message.lower())
            await message.channel.send(line)
            #ping appropriate users
            for user in self.pings[ret_message.lower()]:
                await message.channel.send(user)

    async def add_channel(self, tokens):
        ret_message = "Added the following channels: "
        for idx in range(1, len(tokens)):
            self.channels.add(tokens[idx])
            ret_message += "#" + str(tokens[idx]) + " "
        return ret_message

    async def delete_channel(self, tokens):
        ret_message = "Removed watching the following channels: "
        for idx in range(1, len(tokens)):
            try:
                self.channels.remove(tokens[idx])
                ret_message += "#" + str(tokens[idx]) + " "
            except KeyError:
                continue
        return ret_message

    async def add_ping(self, tokens, user):
        #user = message.author.mention
        ret_message = "Added pings for player {0}: ".format(user)
        for idx in range(1, len(tokens)):
            self.pings[tokens[idx]].append(user)
            ret_message += tokens[idx] + " "
        return ret_message

    async def delete_ping(self, tokens, user):
        #user = message.author.mention
        ret_message = "Deleted pings for player {0}: ".format(user)
        for idx in range(1, len(tokens)):
            self.pings[tokens[idx]].remove(user)
            ret_message += tokens[idx] + " "
        return ret_message

    def savefiles(self):
        #save channels
        with open("channels.txt", "w") as filehandle:
            filehandle.writelines("%s\n" % channel for channel in self.channels)
        #save pings
        np.save('pings', np.array(dict(self.pings)))

    def loadfiles(self):
        #load config
        with open('./config.json') as f:
            self.configs = json.load(f)

        #load channels
        self.channels = set([])
        try:
            with open("channels.txt", "r") as filehandle:
                for line in filehandle:
                    self.channels.add(line.rstrip())
        except FileNotFoundError:
            pass
        #load pings
        self.pings = defaultdict(list)
        try:
            p = np.load('pings.npy')
            self.pings.update(p.item())
        except FileNotFoundError:
            pass
        #load pokemon
        with open('./new_poke.json') as f:
            self.pokenames = json.load(f)
        #load lines
        self.regular_lines = [line.rstrip('\n') for line in open("regular_lines.txt")]
        self.legendary_lines = [line.rstrip('\n') for line in open("legendary_lines.txt")]

        #load legendaries
        self.legendaries = set([
            'Arceus', 'Articuno', 'Azelf', 'Celebi', 'Cobalion', 'Cosmoem', 'Cosmog', 'Cresselia',
            'Darkrai', 'Deoxys', 'Dialga', 'Diancie', 'Entei', 'Genesect', 'Giratina', 'Groudon',
            'Heatran', 'Ho-Oh', 'Hoopa', 'Jirachi', 'Keldeo', 'Kyogre', 'Kyurem', 'Landorus',
            'Latias', 'Latios', 'Lugia', 'Lunala', 'Magearna', 'Manaphy', 'Marshadow', 'Meloetta',
            'Mesprit', 'Mew', 'Mewtwo', 'Moltres', 'Necrozma', 'Palkia', 'Phione', 'Raikou',
            'Rayquaza', 'Regice', 'Regigigas', 'Regirock', 'Registeel', 'Reshiram', 'Shaymin', 'Silvally',
            'Solgaleo', 'Suicune', 'Tapu Bulu', 'Tapu Fini', 'Tapu Koko', 'Tapu Lele', 'Terrakion', 'Thundurus',
            'Tornadus', 'Type: Null', 'Uxie', 'Victini', 'Virizion', 'Volcanion', 'Xerneas', 'Yveltal',
            'Zapdos', 'Zekrom', 'Zeraora', 'Zygarde'
        ])

    async def check(self, message):
        try:
            emb = message.embeds[0]
            embcheck = emb.title.startswith('A wild')
            if not embcheck:
                return "dude this cant be caught"
        except:
            return "dude this isnt a pokemon"

        name = await self.match(emb.image.url.split('?')[0])
        return name
    async def match(self, url):
        async with await self.sess.get(url) as resp:
            dat = await resp.content.read()
        m = hashlib.md5(dat).hexdigest()
        return self.pokenames[m]

bot = Legendary()
bot.run()

