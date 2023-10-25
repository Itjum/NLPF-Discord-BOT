from discord.ext import commands
import http.client
import json
import discord
import random

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(
    command_prefix="!",  # Change to desired prefix
    case_insensitive=True, # Commands aren't case-sensitive
    intents = intents # Set up basic permissions
)

bot.author_id = 0000000000  # Change to your discord id

@bot.event
async def on_ready():  # When the bot is readyw
    print("I'm in")
    print(bot.user)  # Prints the bot's username and identifier

@bot.command()
async def pong(ctx):
    await ctx.send('pong')

@bot.command()
async def name(ctx):
    owner = bot.get_user(bot.author_id)
    # Check if the owner is found
    if owner is not None:
        await ctx.send(owner.name)

@bot.command()
async def d6(ctx):
    number = random.randint(1,6)
    await ctx.send(number)

@bot.event
async def on_message(message):
    # Si le message est bon, on envoie le message
    if message.content == "Salut tout le monde":
        await message.channel.send(f"Salut tout seul {message.author.mention}")
    await bot.process_commands(message)

@bot.command()
async def admin(ctx, member: discord.Member):
    # Verif si le role admin existe deja
    admin_role = discord.utils.get(ctx.guild.roles, name="Admin")
    if not admin_role:
        admin_role = await ctx.guild.create_role(name="Admin", permissions=discord.Permissions.all())

    # Ajout du role admin au membre discord
    await member.add_roles(admin_role)


catch_phrase_list = [
    "Hasta la vista, baby.",
    "I AM YOUR FATHER",
    "GOLLUM ! GOLLUM !",
    "VOUS NE PASSEREZ PAAAAAAS"
]

@bot.command()
async def ban(ctx, member: discord.Member, *, reason=""):
    # Verifier si l'utilisateur a le droit de banir un membre
    if not ctx.author.guild_permissions.ban_members:
        await ctx.send("Vous avez pas la permission de banir")
        return

    # Il ne faut pas pouvoir se banir soit-meme
    if member == ctx.author:
        await ctx.send("Euh c'est toi ?")
        return

    # Si aucune raison n'a ete fournit, on donne une catchphrase super stylé
    if not reason or reason == "":
        index = random.randint(0,3)
        reason = catch_phrase_list[index]

    # BANNAGE
    await ctx.guild.ban(member, reason=reason)
    await ctx.send(f"{member.mention} has been banned. Reason: {reason}")

# Les variables qui vont servir a definir le nombre de messages
# limite et l'interval avant la suppression de la restrcition
flood_monitoring_enabled = False
flood_warning_threshold = 5
flood_time_interval = 10

@bot.command()
async def flood(ctx, action: str = "status"):
    global flood_monitoring_enabled

    if action.lower() == "start":
        flood_monitoring_enabled = True
        await ctx.send("Flood monitoring has been activated.")
    elif action.lower() == "stop":
        flood_monitoring_enabled = False
        await ctx.send("Flood monitoring has been deactivated.")
    elif action.lower() == "status":
        status = "active" if flood_monitoring_enabled else "inactive"
        await ctx.send(f"Flood monitoring is currently {status}.")
    else:
        await ctx.send("Invalid action. Use `!flood start` to activate, `!flood stop` to deactivate, or `!flood status` to check the status.")

@bot.event
async def on_message(message):
    if flood_monitoring_enabled and not message.author.bot:

        author_messages = [msg async for msg in message.channel.history(limit=None) if msg.author == message.author]

        # filtrer les messages
        recent_messages = [msg for msg in author_messages if (message.created_at - msg.created_at).total_seconds() <= flood_time_interval]

        if len(recent_messages) > flood_warning_threshold:
            await message.channel.send(f"{message.author.mention}, please avoid spamming the chat!")

    await bot.process_commands(message)

@bot.command()
async def xkcd(ctx):
    # Genere un nombre sur le nombre de comique pour choisir un comic au hasard
    # PS : J'ai regarde en avance le nombre de comics qu'il y avait
    current_comic_number = 2480
    random_comic_number = random.randint(1, current_comic_number)

    # Recuperer la le comic en json
    conn = http.client.HTTPSConnection("xkcd.com")
    conn.request("GET", f"/{random_comic_number}/info.0.json")
    response = conn.getresponse()

    # Si c'est bon, on charge la donnee du json dans une variable
    if response.status == 200:
        data = json.loads(response.read().decode("utf-8"))

        if "img" in data and "title" in data:
            img_url = data["img"]
            title = data["title"]

            # Envoie de l'image
            await ctx.send(f"Random XKCD Comic: {title}\n{img_url}")
        else:
            await ctx.send("Failed to fetch a random XKCD comic")
    else:
        await ctx.send("Failed to access XKCD website")

    conn.close()

@bot.command()
async def poll(ctx, *, question=""):
    # Creation du poll avec la question
    poll_message = await ctx.send(f"@here {question}")

    # Ajout de plusieurs reactions
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

token = "Enter token"
bot.run(token)  # Starts the bot
