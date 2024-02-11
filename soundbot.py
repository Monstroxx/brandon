import discord
from discord.ext import commands
import asyncio
import json
import random
import gtts
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

def load_sounds():
    try:
        with open('sounds.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
def save_sounds(sounds):
    with open('sounds.json', 'w') as file:
        json.dump(sounds, file, indent=4)


sounds = load_sounds()



@bot.command(name='call')
async def join_call(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()

#@bot.command(name='leave')
#async def leave_call(ctx):
#    await ctx.voice_client.disconnect()

@bot.command(name='newsound')
async def new_sound(ctx, sound_name):
    attachments = ctx.message.attachments
    if attachments:
        sound_url = attachments[0].url
        sounds[sound_name] = sound_url
        save_sounds(sounds)  # Speichere die aktualisierten Sounds
        await ctx.send(f'Sound "{sound_name}" wurde gespeichert.')
    else:
        await ctx.send('Du musst eine MP3-Datei anhängen.')
        
@bot.command(name='sounds')
async def list_sounds(ctx):
    sound_names = ', '.join(sounds.keys())
    await ctx.send(f'Gespeicherte Sounds: {sound_names}')

@bot.command(name='play')
async def play_sound(ctx, sound_name):
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send('Du musst in einem Sprachkanal sein, um diesen Befehl zu verwenden.')
        return

    if not ctx.voice_client or not ctx.voice_client.is_connected():
        # Der Bot ist noch nicht im Sprachkanal, also joint einmal
        channel = ctx.author.voice.channel
        await channel.connect()

    # Überprüfe, ob es sich um eine lokale Datei handelt
    if sound_name not in sounds:
        # Wenn es kein lokaler Sound ist, versuche den Namen als URL zu verwenden
        sound_url = sound_name
    else:
        sound_url = sounds[sound_name]

    # Spiele das Audio ab
    ctx.voice_client.play(discord.FFmpegPCMAudio(sound_url, executable='C:\\Users\\jonas\\Downloads\\ffmpeg-master-latest-win64-gpl\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe'), after=lambda e: print('done', e))
    while ctx.voice_client.is_playing():
        await asyncio.sleep(1)

@bot.command(name='stop')
async def stop_sound(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('Die Audio-Wiedergabe wurde gestoppt.')
    else:
        await ctx.send('Es wird momentan keine Audio-Wiedergabe ausgeführt.')
        
# Befehl zum Beenden des Loops
@bot.command(name='stoploop')
async def stop_loop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        ctx.voice_client.looping = False
        await ctx.send('Die Audio-Wiedergabe wurde gestoppt, und der Loop wurde beendet.')
    else:
        await ctx.send('Es wird momentan keine Audio-Wiedergabe oder Loop ausgeführt.')
        
@bot.command(name='loop')
async def loop_sound(ctx, sound_name):
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send('Du musst in einem Sprachkanal sein, um diesen Befehl zu verwenden.')
        return

    if not ctx.voice_client or not ctx.voice_client.is_connected():
        # Der Bot ist noch nicht im Sprachkanal, also joint einmal
        channel = ctx.author.voice.channel
        await channel.connect()

    # Setze den Loop-Flag auf True
    ctx.voice_client.looping = True

    while ctx.voice_client.looping:
        ctx.voice_client.play(discord.FFmpegPCMAudio(sounds[sound_name], executable='C:\\Users\\jonas\\Downloads\\ffmpeg-master-latest-win64-gpl\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe'), after=lambda e: print('done', e))
        while ctx.voice_client.is_playing():
            await asyncio.sleep(1)

    # Wenn der Loop beendet wurde, trenne die Verbindung
    await ctx.voice_client.disconnect()

@bot.command(name='delsound')
async def delete_sound(ctx, sound_name):
    if sound_name in sounds:
        del sounds[sound_name]
        save_sounds(sounds)  # Speichere die aktualisierten Sounds
        await ctx.send(f'Sound "{sound_name}" wurde gelöscht.')
    else:
        await ctx.send(f'Sound "{sound_name}" wurde nicht gefunden.')

@bot.command(name='randomsound')
async def random_sound(ctx):
    if not sounds:
        await ctx.send('Es sind keine Sounds verfügbar.')
        return

    random_sound_name = random.choice(list(sounds.keys()))
    await play_sound(ctx, random_sound_name)
    
ratings_file_path = 'ratings.json'

# Lade vorhandene Bewertungen aus der Datei, falls vorhanden
try:
    with open(ratings_file_path, 'r') as ratings_file:
        ratings = json.load(ratings_file)
except FileNotFoundError:
    ratings = {}
    print("Keine Bewertungsdatei gefunden.")

@bot.command(name='rate')
async def rate_sound(ctx, sound_name, rating):
    try:
        rating = int(rating)
    except ValueError:
        await ctx.send('Die Bewertung muss eine ganze Zahl sein.')
        return

    if sound_name not in sounds:
        await ctx.send(f'Sound "{sound_name}" wurde nicht gefunden.')
        return

    # Initialisiere das ratings-Dictionary, wenn es nicht vorhanden ist
    if sound_name not in ratings:
        ratings[sound_name] = {'ratings': []}

    # Füge die Bewertung zum ratings-Dictionary hinzu
    ratings[sound_name]['ratings'].append(rating)
    await ctx.send(f'Sound "{sound_name}" wurde mit der Bewertung {rating} bewertet.')

    # Speichere die Bewertungen in der Datei
    try:
        with open(ratings_file_path, 'w') as ratings_file:
            json.dump(ratings, ratings_file)
    except Exception as e:
        print(f"Fehler beim Speichern der Bewertungen: {e}")

@bot.command(name='showratings')
async def show_ratings(ctx):
    if not ratings:
        await ctx.send('Es wurden noch keine Bewertungen abgegeben.')
        return

    # Zeige den Durchschnitt für jeden Sound an
    avg_rating_messages = []
    for sound_name, data in ratings.items():
        if isinstance(data, dict):
            ratings_list = data.get('ratings', [])
            if ratings_list:  # Überprüfe, ob es Bewertungen gibt
                avg_rating = sum(ratings_list) / len(ratings_list)
                avg_rating_messages.append(f'{sound_name}: Durchschnittsbewertung - {avg_rating:.2f}')
            else:
                avg_rating_messages.append(f'{sound_name}: Keine Bewertungen vorhanden.')
        else:
            avg_rating_messages.append(f'{sound_name}: Keine Bewertungen vorhanden.')

    await ctx.send('\n'.join(avg_rating_messages))

    
#geht nicht
    
notification_settings_file = 'notification_settings.json'

def load_notification_settings():
    try:
        with open(notification_settings_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_notification_settings(notification_settings):
    with open(notification_settings_file, 'w') as file:
        json.dump(notification_settings, file, indent=4)

notification_settings = load_notification_settings()

@bot.event
async def on_ready():
    print(f'Bot is ready: {bot.user.name}')
    for guild in bot.guilds:
        default_channel = guild.text_channels[0] if guild.text_channels else None
        if default_channel:
            await default_channel.send(
                f'Brandon ist jetzt online auf Server: {guild.name}. Joint jetzt seinem Call um nicht seine coolen mixtapes zu verpassen!'
            )
        else:
            print(f'Bot ist jetzt online auf Server: {guild.name}')

@bot.command(name='disablenotification')
async def disable_notification(ctx):
    # JSON für Dropdown-Menü erstellen
    dropdown_json = {
        "content": "Wähle aus, ob du Benachrichtigungen aktivieren oder deaktivieren möchtest:",
        "components": [
            {
                "type": 1,
                "components": [
                    {
                        "type": 3,
                        "custom_id": "notification_select",
                        "options":[
                            {
                                "label": "Benachrichtigungen aktivieren",
                                "value": "enable",
                                "description": "Aktiviere Benachrichtigungen für diesen Server."
                            },
                            {
                                "label": "Benachrichtigungen deaktivieren",
                                "value": "disable",
                                "description": "Deaktiviere Benachrichtigungen für diesen Server."
                            }
                        ],
                        "placeholder": "Wähle eine Option",
                        "min_values": 1,
                        "max_values": 1
                    }
                ]
            }
        ]
    }
    # Dropdown-Menü-Nachricht senden
    await ctx.send(dropdown_json)

@bot.event
async def on_button_click(interaction: discord.Interaction, button: discord.ui.Button):
    if button.custom_id == 'notification_select':
        value = button.values[0]  # value entspricht der Auswahl im Dropdown-Menü
        if value == 'enable':
            notification_settings[str(interaction.guild_id)] = True
            save_notification_settings(notification_settings)
            await interaction.response.edit_message(content='Benachrichtigungen aktiviert.', components=[])
        elif value == 'disable':
            notification_settings[str(interaction.guild_id)] = False
            save_notification_settings(notification_settings)
            await interaction.response.edit_message(content='Benachrichtigungen deaktiviert.', components=[])
        else:
            await interaction.response.send_message("Ungültige Interaktion.")

def should_notify(guild_id: int):
    return notification_settings.get(str(guild_id), True)

@bot.command(name='effect')
async def apply_effect(ctx, sound_name, effect_name):
    if not ctx.author.voice or not ctx.author.voice.channel:
        await ctx.send('Du musst in einem Sprachkanal sein, um diesen Befehl zu verwenden.')
        return

    if not ctx.voice_client or not ctx.voice_client.is_connected():
        # Der Bot ist noch nicht im Sprachkanal, also joint einmal
        channel = ctx.author.voice.channel
        await channel.connect()

    # Überprüfe, ob der Sound vorhanden ist
    if sound_name not in sounds:
        await ctx.send(f'Sound "{sound_name}" wurde nicht gefunden.')
        return

    # Pfade für Original- und Effekt-Sound erstellen
    original_path = sounds[sound_name]
    effect_path = f'{sound_name}_{effect_name}.mp3'

    # Anwendung des Effekts auf den Sound
    command = f'ffmpeg -i "{original_path}" -af {effect_name} "{effect_path}"'
    subprocess.run(command, shell=True)

    # Überprüfe, ob die temporäre Datei erstellt wurde
    if os.path.exists(effect_path):
        # Spiele den Sound mit dem Effekt ab
        ctx.voice_client.play(discord.FFmpegPCMAudio(effect_path, executable='C:\\Users\\jonas\\Downloads\\ffmpeg-master-latest-win64-gpl\\ffmpeg-master-latest-win64-gpl\\bin\\ffmpeg.exe'), after=lambda e: print('done', e))
        while ctx.voice_client.is_playing():
            await asyncio.sleep(1)

        # Aufräumen: Lösche die temporäre Datei
        os.remove(effect_path)
    else:
        await ctx.send('Fehler beim Anwenden des Effekts.')

@bot.command(name='tts')
async def text_to_speech(ctx, *, text):
    # Verwende die Google Text-to-Speech-API, um den Text in Sprache umzuwandeln
    tts = gtts.gTTS(text, lang='de')
    tts.save('tts_output.mp3')

    # Spiele die generierte TTS-Datei ab
    await play_sound(ctx, 'tts_output')

@bot.command(name='soundboard')
async def show_soundboard(ctx):
    # Erstelle Buttons für jeden Sound in der sounds-Variable
    buttons = []
    for sound_name, sound_url in sounds.items():
        buttons.append(discord.ui.Button(label=sound_name, custom_id=f"play_sound:{sound_name}"))

    # Erstelle eine View und füge die Buttons hinzu
    view = discord.ui.View()
    for button in buttons:
        view.add_item(button)

    # Sende die Nachricht mit den Buttons
    await ctx.send("Wähle einen Sound aus:", view=view)

# Event handler for button interactions
#@bot.event
#async def on_button_click(interaction: discord.Interaction, button: discord.ui.Button):
#    print(f"Button clicked: {button.custom_id}")
#    if button.custom_id.startswith("play_sound:"):
#        sound_name = button.custom_id[len("play_sound:"):]
#        print(f"Attempting to play sound: {sound_name}")
#        try:
#            # Get the member who clicked the button
#            member = interaction.user
            # Simulate the !play command
#            await bot.get_command('play').callback(ctx=await bot.get_context(interaction.message), sound_name=sound_name)
#        except Exception as e:
#            print(f"Error playing sound: {e}")

# Dein Token hier einfügen
bot.run(os.getenv("BRUDER_TOKEN"))

