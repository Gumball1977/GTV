import discord
from discord import Option
from discord.ext import commands
from discord.ext.commands import cooldown, CommandOnCooldown
from discord.ext.commands import BucketType
import random
import json
import asyncio

client = commands.Bot(command_prefix='!', intents = discord.Intents.all())
client.remove_command('help')

dev_id = 693053906913067029
server_value = 'Жит'
prefix = '!'

#каналы

logs_channel = 1070090524087816263 #поменять
question_channel = 0 #поменять

#ФУНКЦИИ
 
economy_columns = []

async def economy_set(ctx):
	with open('economy.json','r') as f:
		money = json.load(f)
	if not str(ctx.author.id) in money:
		money[str(ctx.author.id)] = {}
		money[str(ctx.author.id)]['Money'] = 10000
		money[str(ctx.author.id)]['Level'] = 1
		money[str(ctx.author.id)]['Exp'] = 0
		money[str(ctx.author.id)]['Invites'] = 0
		money[str(ctx.author.id)]['Inviter_id'] = 0
		money[str(ctx.author.id)]['Inventory'] = []

	for i in await ctx.guild.invites():
		if i.inviter == ctx.author:
			money[str(ctx.author.id)]['Invites'] == i.uses

	with open('economy.json','w') as f:
		json.dump(money,f)

def casino_space(number:int):
	with open('server.json','r') as f:
		server_json = json.load(f)
	server_json['Casino']['Number'] = number

	if number != 0:
		black_numbers=[2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]
		if number%2==0:
			server_json['Casino']['Parity'] = 'Чётное'
		if number%2==1:
			server_json['Casino']['Parity'] = 'Нечётное'

		if number < 13:
			server_json['Casino']['Dozen'] = '1-12'
		if 12 < number < 25:
			server_json['Casino']['Dozen'] = '13-24'
		if 24 < number:
			server_json['Casino']['Dozen'] = '25-36'

		if ((number+3)-1)%3==0:
			server_json['Casino']['Column'] = 'Нижняя линия'
		if ((number+3)-2)%3==0:
			server_json['Casino']['Column'] = 'Средняя линия'
		if number%3==0:
			server_json['Casino']['Column'] = 'Верхняя линия'

		if number < 19:
			server_json['Casino']['Half'] = '1-18'
		if number > 18:
			server_json['Casino']['Half'] = '19-36'

		if number in black_numbers:
			server_json['Casino']['Colour'] = 'Чёрное'
		if not number in black_numbers:
			server_json['Casino']['Colour'] = 'Красное'

		with open('server.json','w') as f:
			json.dump(server_json,f)

	elif number == 0:
		server_json['Casino']['Parity'] = '0'
		server_json['Casino']['Dozen'] = '0'
		server_json['Casino']['Column'] = '0'
		server_json['Casino']['Half'] = '0'
		server_json['Casino']['Colour'] = 'Зелёное'

		with open('server.json','w') as f:
			json.dump(server_json,f)

def casino_gif(number):
	pass #Тут гифка

#ИВЕНТЫ

@client.event
async def on_member_join(member: discord.Member):
	with open('economy.json','r') as f:
		money = json.load(f)

	if not str(member.id) in money:
		money[str(member.id)] = {}
		money[str(member.id)]['Money'] = 10000
		money[str(member.id)]['Level'] = 1
		money[str(member.id)]['Exp'] = 0
		money[str(member.id)]['Invites'] = 0
		money[str(member.id)]['Inviter_id'] = 0
		money[str(member.id)]['Inventory'] = []

	logs = client.get_channel(int(logs_channel))
	eme = f"{member.mention} только что зашёл на сервер."
	try:
		invi = discord.Invite.inviter
		eme = eme + "\n" + f"Приглашен {invi.name}"
		money[str(invi.id)]['Invites'] += 1
	except:
	    pass
	with open('economy.json','w') as f:
		json.dump(money,f)
	await logs.send(embed = discord.Embed(description = eme))

@client.event
async def on_ready(): #Оформить казино
	print('Бот присоединился')
	with open('server.json','r') as f:
		server_json = json.load(f)
	casino_cooldown = 0

	while server_json['Casino']['Status'] == 1:
		if casino_cooldown == 0:

			server_json["Casino"]["Total_players"] = 0
			server_json["Casino"]["Players_list"] = []
			server_json["Casino"]["Players_space"] = []
			server_json["Casino"]["Players_bet"] = []
			server_json["Casino"]["Players_reward"] = []
			server_json["Casino"]["Players"] = []

			casino_chat = client.get_channel(908973520321663000)
			await casino_chat.send('**Делайте ваши ставки, господа.**', delete_after=30)
			with open('economy.json','r') as f:
				money = json.load(f)
			casino_cooldown = 1
			server_json['Casino']['Cooldown'] = 1
			with open('server.json','w') as f:
				json.dump(server_json,f)

			await asyncio.sleep(30)

			casino_cooldown = 2
			server_json['Casino']['Cooldown'] = 2
			await casino_chat.send('**Ставки больше не принимаются.**', delete_after=5)

			await asyncio.sleep(5)

			number = random.randint(0,36)
			casino_space(number)
			casino_gif(number)

			with open('server.json','r') as f:
				server_json = json.load(f)

			winers = (f"**Выигранные ставки:**")
			winers = winers + "\n" + ""
			
			if server_json["Casino"]["Total_players"] > 0:
				for i in range(0, server_json["Casino"]["Total_players"]):
					player_space = server_json["Casino"]["Players_space"][i]
					player_id = server_json["Casino"]["Players_list"][i]
					if player_space == server_json['Casino']['Parity'] or player_space == server_json['Casino']['Dozen'] or player_space == server_json['Casino']['Column'] or player_space == server_json['Casino']['Half'] or player_space == server_json['Casino']['Colour'] or player_space == server_json['Casino']['Number']:
						m = int(server_json["Casino"]["Players_bet"][i]) * int(server_json["Casino"]["Players_reward"][i])
						money[str(player_id)]['Money'] += m
						winers = winers + "\n" + f'{i+1}) {server_json["Casino"]["Players"][i]} - {m}'
						with open('economy.json','w') as f:
							json.dump(money,f)

			await casino_chat.send(f'Шар остановился на числе **{number} {server_json["Casino"]["Colour"]}**', delete_after=32)
			await asyncio.sleep(2)
			await casino_chat.send(embed = discord.Embed(description = f'{winers}'), delete_after=30.0)

			await asyncio.sleep(3)

			casino_cooldown = 0
			server_json['Casino']['Cooldown'] = 0
			with open('server.json','w') as f:
				json.dump(server_json,f)

#КОМАНДЫ МОДЕРАЦИИ

@client.slash_command(name='say', description='Отправить Embed сообщение от имени бота.') #доделать
@commands.has_permissions(administrator=True)
async def say(ctx, msg:Option(str,description='Текст сообщения.',required=True), colour:Option(str,description='Выбрать цвет сообщения.')):
    await ctx.delete()
    await ctx.send(embed=discord.Embed(description=f"""{msg}"""))

@client.slash_command(name='clear', description='Очистка чата.') #Сделано
@commands.has_permissions(administrator=True)
async def clear(ctx, amount:Option(str,description='Количество сообщений.',required=True)):
    await ctx.channel.purge(limit=amount)

#ДОПОЛНИТЕЛЬНЫЕ

@client.command() #доделать
async def __question(ctx, *, content:None):
	await economy_set(ctx)
	if content is None:
		await ctx.add_reaction('❌')
	else:
		await ctx.send(f'Ваш вопрос был успешно отправлен. В скором времени вам на него ответят.', delete_after=60)
		await ctx.add_reaction('✅')
		await ctx.message.delete()
		question_content = (f"{ctx.author.mention} задал вопрос:")
		question_content = question_content + "\n" + ""
		question_content = question_content + "\n" + f"{content}"
		rose = await channel.send(embed = discord.Embed(description = f'{question_content}'))

#ОСНОВНЫЕ КОМАНДЫ

@client.slash_command(name='bet',description='Сделать ставку.') #готово
async def roulette(ctx, bet:Option(int, description='Ставка.', required=True, min_value=100), space:Option(str, description='Зона ставки.', required=True, choices=['Чётное','Нечётное','1-18','19-36','Чёрное','Красное','1-12','13-24','25-36'])):
	with open('server.json','r') as f:
		server_json = json.load(f)
	with open('economy.json','r') as f:	
		money = json.load(f)
	await economy_set(ctx)
	if ctx.author.id in server_json["Casino"]["Players_list"]:
		await ctx.send(f'Вы уже сделали ставку', delete_after=30)
	elif money[str(ctx.author.id)]["Money"] < bet:
		await ctx.send('У вас недостаточно денег.', delete_after=30)
	elif server_json['Casino']['Cooldown'] != 1:
		await ctx.add_reaction('Ставки больше не принимаются.', delete_after=30)
	else:
		bets1=['Чётное','Нечётное','1-18','19-36','Чёрное','Красное']
		bets2=['Нижняя линия','Средняя линия','Верхняя линия','1-12','13-24','25-36']
		if space in bets1:
			server_json["Casino"]["Total_players"] += 1
			server_json["Casino"]["Players_list"].append(ctx.author.id)
			server_json["Casino"]["Players_space"].append(space)
			server_json["Casino"]["Players_bet"].append(bet)
			server_json["Casino"]["Players_reward"].append(2)
			server_json["Casino"]["Players"].append(ctx.author.mention)
			money[str(ctx.author.id)]["Money"] -= bet
			await ctx.add_reaction('✅')
		elif space in bets2:
			server_json["Casino"]["Total_players"] += 1
			server_json["Casino"]["Players_list"].append(ctx.author.id)
			server_json["Casino"]["Players_space"].append(space)
			server_json["Casino"]["Players_bet"].append(bet)
			server_json["Casino"]["Players_reward"].append(3)
			server_json["Casino"]["Players"].append(ctx.author.mention)
			money[str(ctx.author.id)]["Money"] -= bet
			await ctx.add_reaction('✅')
		else:
			await ctx.add_reaction('❌')
	with open('economy.json','w') as f:
		json.dump(money,f)
	with open('server.json','w') as f:
		json.dump(server_json,f)
	await asyncio.sleep(10)
	await ctx.delete()

@client.slash_command(name='reward', description='Забрать свою награду.') #готово
@cooldown(1, 3600, BucketType.user)
async def reward(ctx):
	await economy_set(ctx)
	with open('economy.json','r') as f:
		money = json.load(f)

	mp = 1 + (money[str(ctx.author.id)]['Invites'] * 0.1)//1
	randomka = random.randint(0,500*mp)
	money[str(ctx.author.id)]['Money'] += int(2000 * mp + randomka)
	await ctx.send(f'Вы забрали свою награду.', delete_after=30)

	with open('economy.json','w') as f:
		json.dump(money,f)

@client.slash_command(name='me',description='Узнать свою информацию на сервере.') #доделать
async def balance(ctx):
	await economy_set(ctx)
	with open('economy.json','r') as f:
		money = json.load(f)

	pinfo = f"{ctx.author.mention}:"
	pinfo = pinfo + "\n" + f"Жит: **{money[str(ctx.author.id)]['Money']}**"
	pinfo = pinfo + "\n" + f"Уровень: **{money[str(ctx.author.id)]['Level']}**"
	await ctx.send(embed = discord.Embed(description = f'{pinfo}'))

@client.command(aliases=['stat','stats','my-stats','my-statistics']) #доделать
async def statistics(ctx):
	await economy_set(ctx)
	with open('economy.json','r') as f:
		money = json.load(f)
	pinfo = f"{ctx.author.mention}:"
	pinfo = pinfo + "\n" + f"Приведено душ: **{money[str(ctx.author.id)]['Invites']}**"

#ДУШИ

@client.command() #Оформить
async def __balance(ctx):
	economy_set(ctx)
	with open('economy.json','r') as f:
		money = json.load(f)
	pinfo = f"{ctx.author.mention}:"
	pinfo = pinfo + "\n" + f"Душа: **{money[str(ctx.author.id)]['Soul']}**"
	pinfo = pinfo + "\n" + f"Уровень: **{money[str(ctx.author.id)]['Level']}**"
	pinfo = pinfo + "\n" + f"Баланс: **{money[str(ctx.author.id)]['Money']} {server_value}**"
	pinfo = pinfo + "\n" + f"Хранилище душ: **{money[str(ctx.author.id)]['SStock']}/{money[str(ctx.author.id)]['Max_souls']}**"
	await ctx.send(embed = discord.Embed(description = f'{pinfo}'))

@client.command()
async def __office(ctx, action=None, postact=None):
	economy_set(ctx.author.id)
	with open('economy.json','r') as f:
		money = json.load(f)
	act = action.lower()
	if act is None:
		souls(ctx)
	elif act == 'expand':
		if money[str(author)]['Money'] >= money[str(author)]['SStock_cost']:
			money[str(author)]['Money'] -= money[str(author)]['SStock_cost']
			money[str(author)]['SStock_lvl'] += 1
			money[str(author)]['Max_souls'] += 5
			money[str(author)]['SStock_cost'] = (money[str(author)]['SStock_cost'] * 1.1)//1
			await ctx.message.add_reaction('✅')
	elif act == 'upgrade':
		pass

@client.command() #Доработать
@cooldown(1,3600,BucketType.user)
async def __income(ctx):
	economy_set(ctx.author.id)
	with open('economy.json','r') as f:
		money = json.load(f)

	n = 0
	for i in range(money[str(author)]['SStock']):
		rare = money[str(ctx.author.id)]['Souls']
		if rare == 'Leg':
			inc = random.randint(500)
			si = (1000 + inc)*5
			n += si


	plr = random.randint(500)
	soul_income = 1000 + plr + n

	if money[str(ctx.author.id)]['Soul'] == "Свободна":
		soul_income *= 2 
	money[str(ctx.author.id)]['Money'] += soul_income

	with open('economy.json','w') as f:
		json.dump(money,f)

@client.command()
async def __souls(ctx):
	with open('server.json','r') as f:
		server_json = json.load(f)
	with open('economy.json','r') as f:
		money = json.load(f)
	economy_set(ctx.author.id)
	soul_storage = f"**Хранилище душ ({money[str(ctx.author.id)]['SStock_lvl']} уровень):**"
	soul_storage = soul_storage + "\n" + f""
	g=1
	f = money[str(ctx.author.id)]['Souls']
	for i in money[str(ctx.author.id)]['Souls']:
		soul_storage = soul_storage + "\n" + f"{g}) {i[0]}|**{i[1]} душа** ({i[3]} уровень)"
		g+=1
	await ctx.send(embed = discord.Embed(description = f'{soul_storage}'))

@client.command()
async def __create_soul(ctx, rare_png, rare, owner_id:int, lvl):
	economy_set(ctx.author.id)
	with open('economy.json','r') as f:
		money = json.load(f)
	if ctx.author.id == dev_id:
		money[str(ctx.author.id)]['Souls'].append([])
		money[str(ctx.author.id)]['Souls'][-1] += rare_png, rare, owner_id, lvl

		with open('economy.json','w') as f:
			json.dump(money,f)

#карточная игра

@client.command()
async def __damon(ctx, action = None):
	economy_set(ctx.author.id)
	with open('damon.json','r') as f:
		damon_json = json.load(f)
	if not str(ctx.author.id) in damon_json:
		damon_json[str(ctx.author.id)]['Cons'] = 100
		damon_json[str(ctx.author.id)]['Dems'] = 0
		damon_json[str(ctx.author.id)]['Power'] = 0
		damon_json[str(ctx.author.id)]['Deck'] = []
		damon_json[str(ctx.author.id)]['Cards'] = []
		damon_json[str(ctx.author.id)]['Cases'] = []
		damon_json[str(ctx.author.id)]['Inventory'] = []

	act = action.lower()
	if act is None:
		pass

	with open('damon.json','w') as f:
		json.dump(damon_json,f)

@client.slash_command(name='test', description='Тестовая команда')
async def test(ctx, msg:Option(str,description='Что-то',required=True)):
    await ctx.delete()
    await ctx.send(msg)

bot_token = 'OTA4OTcxNDk5NDA5NTE4NjIy.G9HMm7.vTkhMJfT01idaTi0_7PmsQ2-qxIV17NmasriGY'
client.run(bot_token)