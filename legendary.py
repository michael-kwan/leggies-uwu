import discord
import time
import json
import hashlib
import urllib.request
import aiohttp
import random

class Legendary(discord.Client):
    def __init__(self):
        super().__init__()
        with open('./config.json') as f:
            self.configs = json.load(f)
        self.channels = set(["script-spam","wngl-kpanda-yuthegreat","jfang-no-sniping","all-hail-kpanda","6-hr-ban","the-rest-of-us"])
        with open('./new_poke.json') as f:
            self.pokenames = json.load(f)
        self.hexhash = []
        self.regular_lines = [line.rstrip('\n') for line in open("regular_lines.txt")]
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
        self.legendary_lines = [line.rstrip('\n') for line in open("legendary_lines.txt")]
    def run(self):
        super().run(self.configs['token'])

    async def on_ready(self):
        self.sess = aiohttp.ClientSession(loop=self.loop)
        print("logged in")

    async def on_message(self, message):
        if str(message.channel) not in self.channels:
            return
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

    def savefile(self, l, name):
        with open(name, 'w') as filehandle:
            filehandle.writelines("%s\n" % ' '.join(line) for line in l)

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

