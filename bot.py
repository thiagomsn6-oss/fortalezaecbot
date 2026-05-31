import discord
from discord import app_commands
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="+", intents=intents)

# ========== BANCO DE DADOS LOCAL ==========
def carregar(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r") as f:
            return json.load(f)
    return {}

def salvar(arquivo, dados):
    with open(arquivo, "w") as f:
        json.dump(dados, f, indent=2)

# ========== +ssver ==========
@bot.command(name="ssver")
async def ssver(ctx):
    emoji = "<:Fortaleza_Esporte_Clube_logo:1509696400408182945>"
    jogadores = [
        "thzsawr",
        "SGKBJM2",
        "Juan_domorro0",
        "NuMbBrAtZx",
        "brchatgui",
        "Sonic3536381",
        "ratodabamor",
        "GrilloKKJ067",
        "killiaenmbappe",
        "Lobo_10tiba",
        "gbezziny75",
        "ed_bahia",
        "Juan_domorro0",
        "26swxzs",
    ]
    lista = "\n".join(f"{emoji} {j}" for j in jogadores)
    embed = discord.Embed(title="📋 SQUADSHEET", description=lista, color=0xC8102E)
    await ctx.send(embed=embed)


# ========== /lf ==========
class LFModal(discord.ui.Modal, title="Looking For — Abrir Sala"):
    nick = discord.ui.TextInput(label="Nick do Host", placeholder="Ex: Thiaguim.FZ")
    link = discord.ui.TextInput(label="Link da Sala", placeholder="Cole o link aqui")

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🟢 HOST ABERTO", color=0x00FF88)
        embed.add_field(name="👤 Host", value=self.nick.value, inline=True)
        embed.add_field(name="🔗 Link", value=self.link.value, inline=True)
        embed.set_footer(text=f"Aberta por {interaction.user.display_name}")
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="lf", description="Abrir sala e divulgar no canal")
async def lf(interaction: discord.Interaction):
    await interaction.response.send_modal(LFModal())


# ========== /kit ==========
@bot.tree.command(name="kit", description="Ver o kit pelo ID")
@app_commands.describe(id="ID do kit")
async def kit(interaction: discord.Interaction, id: str):
    kits = carregar("kits.json")
    if id not in kits:
        await interaction.response.send_message(f"❌ Kit `{id}` não encontrado. Use `/kit_add` para cadastrar.", ephemeral=True)
        return

    k = kits[id]
    embed = discord.Embed(title=f"👕 KIT — ID: {id}", description=k.get("descricao", ""), color=0x1a1aff)
    if k.get("imagem"):
        embed.set_image(url=k["imagem"])
    await interaction.response.send_message(embed=embed)

class KitAddModal(discord.ui.Modal, title="Cadastrar Kit"):
    kit_id = discord.ui.TextInput(label="ID do Kit", placeholder="Ex: kit01")
    descricao = discord.ui.TextInput(label="Descrição", placeholder="Ex: Kit titular 2025", required=False)
    imagem = discord.ui.TextInput(label="URL da imagem", placeholder="Cole o link direto da imagem")

    async def on_submit(self, interaction: discord.Interaction):
        kits = carregar("kits.json")
        kits[self.kit_id.value] = {
            "descricao": self.descricao.value,
            "imagem": self.imagem.value
        }
        salvar("kits.json", kits)
        await interaction.response.send_message(f"✅ Kit `{self.kit_id.value}` cadastrado!", ephemeral=True)

@bot.tree.command(name="kit_add", description="[ADMIN] Cadastrar um kit com imagem")
async def kit_add(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return
    await interaction.response.send_modal(KitAddModal())


# ========== /sobrenos ==========
@bot.tree.command(name="sobrenos", description="Conheça o Fortaleza EC")
async def sobrenos(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🔵🔴 Fortaleza Esporte Clube",
        description=(
            "O **Fortaleza Esporte Clube** é um time de futebol virtual fundado em **2026**, "
            "com o propósito de reunir jogadores apaixonados pelo esporte em um ambiente competitivo, "
            "respeitoso e, acima de tudo, divertido.\n\n"
            "Nossa missão é proporcionar experiências memoráveis dentro e fora dos campos virtuais, "
            "cultivando uma comunidade sólida onde o companheirismo e a dedicação são os pilares fundamentais.\n\n"
            "**Seja bem-vindo ao Fortaleza EC — onde a diversão é levada a sério.**"
        ),
        color=0xC8102E
    )
    embed.set_footer(text="Fortaleza EC • Fundado em 2026")
    await interaction.response.send_message(embed=embed)


# ========== +lfvote ==========
@bot.command(name="lfvote")
async def lfvote(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="🗳️ VOTE PARA LF",
        description=f"**{ctx.author.display_name}** quer fazer um LF!\nVotem abaixo para confirmar presença ( to 6 ).\n@everyone",
        color=0x00FF88
    )
    embed.set_footer(text="Reaja com ✅ para confirmar")
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("✅")


# ========== INICIAR ==========
@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot online: {bot.user}")

bot.run(os.environ["DISCORD_TOKEN"])
