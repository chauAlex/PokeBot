import collections
import random
from turtle import color
from urllib import request
import discord
from discord.ext import commands
import requests
import json
import pymongo
from pymongo import MongoClient
import urllib.parse
from Config import passw

class PokeCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        cluster = MongoClient('mongodb+srv://cookieCons:' + urllib.parse.quote_plus(passw) + '@pokebotcluster.hjcsz1b.mongodb.net/test')
        db = cluster['UserCatchData']
        self.collection = db['CatchData']
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.send('Pong!')

    @commands.command(aliases = ['about'])
    async def help(self, ctx):
        embed = discord.Embed(title = 'Commands', description = 'These are the commands that can be used for this bot.', color= discord.Color.dark_purple())
        embed.add_field(name='!ping', value='This command responds with pong.')
        embed.add_field(name='!generate', value='This command catches a random pokemon and sends it to your PC.')
        embed.add_field(name='!ranch', value='This command lists out the pokemon in your PC.')
        embed.add_field(name='!dex', value='This command can be used to look up and pokemon in the dex.')
        await ctx.send(embed = embed)
    
    @commands.command()
    async def generate(self, ctx):
        pokeNum = random.randint(1, 802)
        poke_url = 'https://pokeapi.co/api/v2/pokemon/{}/'.format(pokeNum)
        poke_json = requests.get(poke_url).json()

        name = poke_json['name'].title()
        spriteurl = poke_json['sprites']['front_default']

        pokeEmbed = discord.Embed(title = 'Catch of the Day', description = f'You caught a {name}!', color= discord.Color.random())
        pokeEmbed.set_image(url=spriteurl)

        query = {'_id': ctx.author.id}
        if self.collection.count_documents(query) == 0:
            self.collection.insert_one({'_id':ctx.author.id, 'Pokemon': [name]})
        else:
            if self.collection.find_one({'_id': ctx.author.id, 'Pokemon': name}):
                await ctx.send('This has already been caught!')
            else:
                self.collection.update_one({'_id':ctx.author.id}, {'$push': {'Pokemon': name}})
        
        await ctx.send(embed=pokeEmbed)
    
    @commands.command()
    async def ranch(self, ctx):
        if self.collection.find_one({'_id': ctx.author.id}):
            pokeList = self.collection.find_one({'_id': ctx.author.id})['Pokemon']
            pokeStr = ''
            for i in range(0, len(pokeList)):
                pokeStr += pokeList[i]
                if i < len(pokeList)-1:
                    pokeStr += '\n'
            ranchEmbed = discord.Embed(title='Pokemon Ranch', description = pokeStr, color= discord.Color.random())
            ranchEmbed.set_thumbnail(url='http://lavacutcontent.com/wp-content/uploads/2020/01/Hayley.png')
            await ctx.send(embed=ranchEmbed)
        else:
            await ctx.send('Try catching some more Pokemon!')

    @commands.command()
    async def dex(self, ctx, arg):
        arg = arg.lower()
        search_url = 'https://pokeapi.co/api/v2/pokemon/{}/'.format(arg)
        req = requests.get(search_url)
        if(req.status_code >= 400):
            await ctx.send('ERR: Not Found')
            return
        poke_json = req.json()

        name = poke_json['name'].title()
        spriteurl = poke_json['sprites']['front_default']
        abils = poke_json['abilities']
        abilityList = []
        for ability in abils:
            abilityList.append(ability['ability']['name'])
        
        def makeAbsPrint(abilityList):
            abilityStr = ''
            for ability in abilityList:
                recased = ability[0].upper() + ability[1:]
                abilityStr += recased + ','
            #remove extra ,
            return abilityStr[:-1]

        ownStatus = self.collection.find_one({'_id': ctx.author.id, 'Pokemon': name})
        if ownStatus:
            ownStatus = 'Caught'
        else:
            ownStatus = 'Not Caught'

        pokeEmbed = discord.Embed(title = f'{name}', color= discord.Color.random())
        pokeEmbed.add_field(name=f'{ownStatus}', value=f'This pokemon can have the following abilities: {makeAbsPrint(abilityList)}')
        pokeEmbed.set_image(url=spriteurl)

        await ctx.send(embed=pokeEmbed)

async def setup(bot):
    await bot.add_cog(PokeCog(bot))