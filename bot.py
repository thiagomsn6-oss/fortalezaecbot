import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="+", intents=intents)

CANAL_VOZ_ID = 1508170208525684937  # Troca pelo ID do canal de voz

# ========== BANCO DE DADOS LOCAL ==========
def carregar(arquivo):
    if os.path.exists(arquivo):
        with open(arquivo, "r") as f:
            return json.load(f)
    return {}

def salvar(arquivo, dados):
    with open(arquivo, "w") as f:
        json.dump(dados, f, indent=2)

# ========== /ss ==========
class AdicionarJogadorModal(discord.ui.Modal, title="Adicionar Jogador"):
    nome = discord.ui.TextInput(label="Nome do jogador", placeholder="Ex: Arthur")
    numero = discord.ui.TextInput(label="Número da camisa", placeholder="Ex: 10")
    posicao = discord.ui.TextInput(label="Posição", placeholder="Ex: ATA, MEI, ZAG, GOL")
    plataforma = discord.ui.TextInput(label="Plataforma", placeholder="Ex: PS5, PC, XBOX")
    nota = discord.ui.TextInput(label="Nota", placeholder="Ex: 95")

    async def on_submit(self, interaction: discord.Interaction):
        squad = carregar("squad.json")
        squad[self.numero.value] = {
            "nome": self.nome.value,
            "posicao": self.posicao.value,
            "plataforma": self.plataforma.value,
            "nota": self.nota.value
        }
        salvar("squad.json", squad)
        await interaction.response.send_message(
            f"✅ **{self.nome.value}** adicionado com sucesso!", ephemeral=True
        )

class RemoverJogadorModal(discord.ui.Modal, title="Remover Jogador"):
    numero = discord.ui.TextInput(label="Número da camisa para remover", placeholder="Ex: 10")

    async def on_submit(self, interaction: discord.Interaction):
        squad = carregar("squad.json")
        if self.numero.value in squad:
            nome = squad[self.numero.value]["nome"]
            del squad[self.numero.value]
            salvar("squad.json", squad)
            await interaction.response.send_message(f"🗑️ **{nome}** removido.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Número não encontrado.", ephemeral=True)

@bot.tree.command(name="ss", description="Ver ou gerenciar a squadsheet")
@app_commands.describe(acao="ver | adicionar | remover")
async def ss(interaction: discord.Interaction, acao: str = "ver"):
    acao = acao.lower()

    if acao == "ver":
        squad = carregar("squad.json")
        if not squad:
            await interaction.response.send_message("❌ Squad vazia.", ephemeral=True)
            return

        posicoes = {"GOL": [], "ZAG": [], "LAT": [], "MEI": [], "ATA": []}
        outros = []
        for num, p in sorted(squad.items(), key=lambda x: int(x[0]) if x[0].isdigit() else 99):
            linha = f"`[{num}]` **{p['nome']}** — {p['nota']} | {p['plataforma']}"
            if p["posicao"].upper() in posicoes:
                posicoes[p["posicao"].upper()].append(linha)
            else:
                outros.append(linha)

        embed = discord.Embed(title="📋 SQUADSHEET", color=0xC8102E)
        nomes_pos = {"GOL": "🧤 GOLEIRO", "ZAG": "🛡️ ZAGUEIROS", "LAT": "🔁 LATERAIS", "MEI": "⚙️ MEIO-CAMPO", "ATA": "⚡ ATAQUE"}
        for key, label in nomes_pos.items():
            if posicoes[key]:
                embed.add_field(name=label, value="\n".join(posicoes[key]), inline=False)
        if outros:
            embed.add_field(name="➕ OUTROS", value="\n".join(outros), inline=False)

        await interaction.response.send_message(embed=embed)

    elif acao in ["adicionar", "add"]:
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
            return
        await interaction.response.send_modal(AdicionarJogadorModal())

    elif acao in ["remover", "del"]:
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
            return
        await interaction.response.send_modal(RemoverJogadorModal())

    else:
        await interaction.response.send_message("Use: `/ss ver`, `/ss adicionar` ou `/ss remover`", ephemeral=True)


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


# ========== MANTER NA CALL ==========
@tasks.loop(minutes=5)
async def manter_na_call():
    for guild in bot.guilds:
        voice_client = guild.voice_client
        if voice_client is None:
            canal = bot.get_channel(CANAL_VOZ_ID)
            if canal:
                try:
                    await canal.connect()
                except Exception:
                    pass
        elif not voice_client.is_connected():
            try:
                await voice_client.disconnect(force=True)
                canal = bot.get_channel(CANAL_VOZ_ID)
                if canal:
                    await canal.connect()
            except Exception:
                pass

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id:
        return
    guild = member.guild
    voice_client = guild.voice_client
    if voice_client is None:
        canal = bot.get_channel(CANAL_VOZ_ID)
        if canal:
            try:
                await canal.connect()
            except Exception:
                pass


# ========== INICIAR ==========
@bot.event
async def on_ready():
    await bot.tree.sync()
    manter_na_call.start()
    for guild in bot.guilds:
        canal = bot.get_channel(CANAL_VOZ_ID)
        if canal:
            try:
                await canal.connect()
            except Exception:
                pass
    print(f"✅ Bot online: {bot.user}")

bot.run(os.environ["DISCORD_TOKEN"])
