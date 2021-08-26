#https://discord.com/api/oauth2/authorize?client_id=860714308659839007&permissions=2218131009&scope=bot
import discord
from discord.ext import commands
from urllib.request import Request, urlopen
import json
from discord_components import *
import datetime
import aiohttp

with open('config.json') as config:
    keys = json.load(config)



client = commands.Bot(command_prefix = '!', case_insensitive=True, help_command=None)
types = ['user', 'description', 'subject']
imageoftheday = f'http://astrobin.com/api/v1/imageoftheday/?limit=1&api_key={keys["AstrobinAPIKey"]}&api_secret={keys["AstrobinAPISecret"]}&format=json'
@client.event
async def on_ready():
    print('Bot started')
    DiscordComponents(client)
    async with aiohttp.ClientSession() as session:
        payload = {'request-json': json.dumps({"apikey": keys["Astrometry APIKey"]})}
        async with session.post('http://nova.astrometry.net/api/login', data=payload) as resp:
            print(await resp.text())
            response = json.loads(await resp.text())
            global astrometryses
            astrometryses = response["session"]




@client.command(aliases=['Image of the day'])
async def iotd(ctx):
    req = Request(imageoftheday,headers={'User-Agent': 'Mozilla/5.0'})
    data = urlopen(req).read()
    data_json = json.loads(str(data, 'utf-8'))
    path = data_json["objects"][0]["image"]
    print(path)

    image = 'http://astrobin.com{}'.format(path.split('/api/v1/image', 1)[1])
    await ctx.send(image)

@client.command(aliases=['astronomy picture of the day'])
async def apod(ctx):
    data = urlopen(f'https://api.nasa.gov/planetary/apod?api_key={keys["NASA Api Key"]}')
    json_data = json.loads(str(data.read(), 'utf-8'))
    embed = discord.Embed(
        title = json_data['title'],
        description = json_data['explanation'],
        colour = discord.Colour.blue()
    )

    embed.set_image(url=json_data['url'])
    embed.set_thumbnail(url='https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo-web-rgb.png')
    embed.add_field(name='Date', value=json_data['date'], inline=False)
    await ctx.send(embed=embed)

@client.command(aliases=['marble', 'earth'])
async def globe(ctx):
    data = urlopen(f'https://api.nasa.gov/EPIC/api/natural?api_key={keys["NASA Api Key"]}')
    json_data = json.loads(str(data.read(), 'utf-8'))
    date = json_data[0]["date"].split(None, 1)[0].replace('-', '/')
    embed = discord.Embed(
        title = 'DSCVR\'s view of planet earth',
        description = 'This what planet earth looks like from the DSCVR spacecraft from its lagrange point.',
        colour = discord.Colour.blue()
    )
    embed.set_image(url=f'https://epic.gsfc.nasa.gov/archive/natural/{date}/png/{json_data[0]["image"]}.png')
    embed.set_thumbnail(url='https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo-web-rgb.png')
    embed.add_field(name='Date', value=json_data[0]['date'], inline=False)
    await ctx.send(embed=embed)

@client.command()
async def help(ctx, function=None):
    if function == None:
        embed = discord.Embed(
            title = "Androbot's Functions",
            description = 'Androbot is a discord bot dedicated to Astronomy',
            color = discord.Colour.purple()
        )
        with open('help.json') as json_file:
            funcs = json.load(json_file)
            for i in funcs.keys():
                embed.add_field(name=funcs[i]["title"], value=funcs[i]['description'], inline=True)
    else:
        with open('help.json') as json_file:
            funcs = json.load(json_file)
            embed = discord.Embed(
                title = funcs[function.lower()]["title"],
                description = funcs[function.lower()]["description"],
                colour = discord.Colour.red()
            )
            if funcs[function.lower()]["syntax"] != None:
                embed.add_field(name='Syntax: ', value=funcs[function.lower()]["syntax"], inline=False)
            if funcs[function.lower()]["aliases"] != None:
                embed.add_field(name='Aliases: ', value=funcs[function.lower()]["aliases"], inline=False)
    await ctx.send(embed=embed)


@client.command()
async def platesolve(ctx):
    await ctx.send(content=astrometryses)
    attachment = (ctx.message.attachments[0].url)
    async with aiohttp.ClientSession as session:
        async with session.get('http://nova.astrometry.net/api/url_upload', data=f'{"session": {astrometryses}, "url": {attachment}}') as resp:
            response = json.loads(resp)
            if resp["status"] == "success":
                await ctx.send(content=f'Your submission was successful! Please see https://http://nova.astrometry.net/status/{response["subid"]}')

@client.command()
async def search(ctx, *, query):
    type = query.split(" ")

    if len(type) > 1:
        query = query.split(" ")[1]
    else:
        query = type[0]
    print(type[0])
    print(query)
    if type[0] in types and len(type) > 1:
        if type[0] == 'subject':
            subtype = 'subjects'

        else:
            subtype = type[0]

        if type[0] == 'description':
            subtype = 'descriptioncontains'

    else:
        subtype = 'subjects'




    m = await ctx.send(content='Loading...')
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://astrobin.com/api/v1/image/?{subtype}={query}&api_key={keys["AstrobinAPIKey"]}&api_secret={keys["AstrobinAPISecret"]}&format=json', headers={'User-Agent': 'Mozilla/5.0'}) as req:
            print(f'http://astrobin.com/api/v1/image/?{subtype}={query}&api_key={keys["AstrobinAPIKey"]}&api_secret={keys["AstrobinAPISecret"]}&format=json')
            data = await req.json()
            json_data = json.loads(json.dumps(data))
            print(json_data)
            embeds = []
            if len(json_data['objects']) > 0:
                for i in range(len(json_data['objects'])):
                    objects = len(json_data['objects'])
                    current = 0
                    embed = discord.Embed(
                        title = json_data['objects'][i]['title'],
                        description = json_data['objects'][i]['description'],
                        url = f'''https://www.astrobin.com/{json_data['objects'][i]['hash']}/'''
                    )
                    embed.set_image(url=json_data['objects'][i]["url_hd"])
                    embed.set_author(name=json_data['objects'][i]['user'])
                    embed.set_thumbnail(url=json_data['objects'][i]['url_histogram'])
                    embed.add_field(name='Views', value=json_data['objects'][i]['views'], inline=True)
                    embed.add_field(name='Likes', value=json_data['objects'][i]['likes'], inline=True)
                    embeds.append(embed)

                timeout = datetime.datetime.utcnow() + datetime.timedelta(minutes=5)
                await m.edit(
                    content = f'Result {current + 1} / {objects + 1}',
                    embed=embeds[current],
                    components = [
                        [
                            Button(label = '<', style=1),
                            Button(label = '>', style=1)
                        ]
                    ]
                )
                while m.created_at < timeout:
                    res = await client.wait_for('button_click')

                    if res.component.label == '>' and current < objects and res.message == m:
                        current += 1
                        await res.respond(
                            type=7,
                            content = f'Result {current + 1} / {objects + 1}',
                            embed=embeds[current]
                        )

                    if res.component.label == '<' and current > 0 and res.message == m:
                        current += -1
                        await res.respond(
                            type=7,
                            content = f'Result {current + 1} / {objects + 1}',
                            embed=embeds[current]
                        )


                    await m.edit(
                        embed=embeds[current],
                        content=f'Result {current + 1} / {objects + 1}'
                    )
            else:
                await m.edit(content='No results found')



client.run(keys["Bot Token"])
