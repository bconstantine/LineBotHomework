'''
This is my LineBot API
How to Start:
    > Step 0. Go to ./MVCLab-Summer-Course/LineBot/
        > cd ./MVCLab-Summer-Course/LineBot
    > Step 1. Install Python Packages
        > pip install -r requirements.txt
    > Step 2. Run main.py
        > python main.py
Reference:
1. LineBot API for Python
    > https://github.com/line/line-bot-sdk-python
2. Pokemon's reference
    > https://pokemondb.net/pokedex/all
3. Line Developer Messaging API Doc
    > https://developers.line.biz/en/docs/messaging-api/
'''
import os
import re
import json
import random
from dotenv import load_dotenv
from pyquery import PyQuery
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *

load_dotenv() # Load your local environment variables

# Pokedex Link
pokemons_link = 'https://pokemondb.net/pokedex/all'
# Get all info from link (html)
doc = PyQuery(url=pokemons_link).find('td').find('span').children()
# Create My_pokedex Images Dict
pokemons_imgs = dict()
# For filter the empty image from link
empty_img_url = 'https://img.pokemondb.net/s.png'
# Add each pokemon img url into dict
for poke in doc:
    poke = PyQuery(poke)
    # Filter empty img
    if not re.match(poke.attr('data-src'), empty_img_url):
        poke_url = poke.attr('data-src') # Attribute['data-src'] value
        poke_name = str(poke_url).split('/')[-1][:-4].lower() # Get lower case of a pokemon name & filter .png behind
        # Save a pokemon's img info
        pokemons_imgs[poke_name] = poke_url

CHANNEL_TOKEN = os.environ.get('LINE_TOKEN')
CHANNEL_SECRET = os.getenv('LINE_SECRET')

app = FastAPI()

My_LineBotAPI = LineBotApi(CHANNEL_TOKEN) # Connect Your API to Line Developer API by Token
handler = WebhookHandler(CHANNEL_SECRET) # Event handler connect to Line Bot by Secret key

'''
For first testing, you can comment the code below after you check your linebot can send you the message below
'''
CHANNEL_ID = os.getenv('LINE_UID') # For any message pushing to or pulling from Line Bot using this ID
# My_LineBotAPI.push_message(CHANNEL_ID, TextSendMessage(text='Welcome to my pokedex !')) # Push a testing message

# Events for message reply
my_event = ['#getpokemon', '#mypokemon', '#addpokemon', '#delpokemon', '#help']
# My pokemon datas
my_pokemons = dict()
poke_file = 'my_pokemons.json'
# Load local json file if exist
if os.path.exists(poke_file):
    with open(poke_file, 'r') as f:
        my_pokemons = json.load(f)

'''
See more about Line Emojis, references below
> Line Bot Free Emojis, https://developers.line.biz/en/docs/messaging-api/emoji-list/
'''
# Create my emoji list
my_emoji = [
    [{'index':27, 'productId':'5ac1bfd5040ab15980c9b435', 'emojiId':'005'}],
    [{'index':27, 'productId':'5ac1bfd5040ab15980c9b435', 'emojiId':'019'}],
    [{'index':27, 'productId':'5ac1bfd5040ab15980c9b435', 'emojiId':'096'}]
]

# Line Developer Webhook Entry Point
@app.post('/')
async def callback(request: Request):
    body = await request.body() # Get request
    signature = request.headers.get('X-Line-Signature', '') # Get message signature from Line Server
    try:
        handler.handle(body.decode('utf-8'), signature) # Handler handle any message from LineBot and 
    except InvalidSignatureError:
        raise HTTPException(404, detail='LineBot Handle Body Error !')
    return 'OK'

# All message events are handling at here !
@handler.add(MessageEvent, message=TextMessage)
def handle_textmessage(event):
    global my_pokemons
    ''' Basic Message Reply
    message = TextSendMessage(text= event.message.text)
    My_LineBotAPI.reply_message(
        event.reply_token,
        message
    )
    '''
    # Split message by white space
    recieve_message = str(event.message.text).split(' ')
    # Get first splitted message as command
    case_ = recieve_message[0].lower().strip()
    # Case 1: get pokemon
    if re.match(my_event[0], case_):
        pokename = recieve_message[1].lower().strip()
        if pokename in pokemons_imgs.keys():
            url = pokemons_imgs[pokename]
            # Return image
            My_LineBotAPI.reply_message(
                event.reply_token,
                ImageSendMessage(
                    original_content_url=url,
                    preview_image_url=url
                )
            )
        else:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(text='Pokemon not found in pokedex !')
            )
    # Case 2: show my pokemons (if existed)
    elif re.match(my_event[1], case_):
        if len(my_pokemons) > 0:
            message = 'Here is your pokemons :\n'
            for idx, pokename in enumerate(my_pokemons.keys(), 1):
                # Send Poke name
                message += str(idx) + ': ' + pokename + '\n'
            # LineBot Reply Message can only send up to 5, otherwise you will see an error in console
            # LineBot event reply_token can only be used once !
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(text=message)
            )
        else:
            # Reply message with emoji
            reply_emoji = random.choice(my_emoji)
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text='You don\'t have any pokemon $',
                    emojis= reply_emoji
                )
            )
    # Case 3: add a pokemon into my pokedex
    elif re.match(my_event[2], case_):
        pokename = recieve_message[1].lower().strip()
        if pokename in pokemons_imgs.keys():
            if pokename in my_pokemons.keys():
                My_LineBotAPI.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f'You have already add {pokename} into your pokedex !')
                )
            else:
                # Add a new pokemon into my pokedex and sorted by key value
                my_pokemons[pokename] = pokemons_imgs[pokename]
                my_pokemons = dict(sorted(my_pokemons.items()))
                # Save to local json file
                with open(poke_file, 'w') as f:
                    json.dump(my_pokemons, f, indent=4)
                # Reply successful message
                My_LineBotAPI.reply_message(
                    event.reply_token,
                    TextSendMessage(text=f'Successful add {pokename} into your pokedex !')
                )
        else:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(text=f'Pokemon "{pokename}" not found in global pokedex !')
            )
    # Case 3: Delete a pokemon from my pokedex
    elif re.match(my_event[3], case_):
        pokename = recieve_message[1].lower().strip()
        if pokename in my_pokemons.keys():
            # Remove an existed pokemon in my pokedex
            my_pokemons.pop(pokename)
            # Save to local json file
            with open(poke_file, 'w') as f:
                json.dump(my_pokemons, f, indent=4)
            # Reply successful message
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(text=f'Successful delete {pokename} from your pokedex !')
            )
        else:
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(text=f'Pokemon "{pokename}" not found in your pokedex !')
            )
    # Help command for listing all commands to user
    elif re.match(my_event[4], case_):
        command_describtion = '$ Commands:\n\
        #getpokemon <pokemon\'s name>\n\t-->Show this pokemon\'s name & Image for you if existed !\n\
        #mypokemon\n\t-->List all pokemons in your pokedex if existed !\n\
        #addpokemon <pokemon\'s name>\n\t-->Add a pokemon from global pokedex into your pokedex if existed !\n\
        #delpokemon <pokemon\'s name>\n\t-->Delete a pokemon from your pokedex if existed !\n'
        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(
                text=command_describtion,
                emojis=[
                    {
                        'index':0,
                        'productId':'5ac21a18040ab15980c9b43e',
                        'emojiId':'110'
                    }
                ]
            )
        )
    else:
        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(
                text='$ Welcome to my pokedex ! Enter "#help" for commands !',
                emojis=[
                    {
                        'index':0,
                        'productId':'5ac2213e040ab15980c9b447',
                        'emojiId':'035'
                    }
                ]
            )
        )

# Line Sticker Class
class My_Sticker:
    def __init__(self, p_id: str, s_id: str):
        self.type = 'sticker'
        self.packageID = p_id
        self.stickerID = s_id

'''
See more about Line Sticker, references below
> Line Developer Message API, https://developers.line.biz/en/reference/messaging-api/#sticker-message
> Line Bot Free Stickers, https://developers.line.biz/en/docs/messaging-api/sticker-list/
'''
# Add stickers into my_sticker list
my_sticker = [My_Sticker(p_id='446', s_id='1995'), My_Sticker(p_id='446', s_id='2012'),
     My_Sticker(p_id='446', s_id='2024'), My_Sticker(p_id='446', s_id='2027'),
     My_Sticker(p_id='789', s_id='10857'), My_Sticker(p_id='789', s_id='10877'),
     My_Sticker(p_id='789', s_id='10881'), My_Sticker(p_id='789', s_id='10885'),
     ]

# Line Sticker Event
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker(event):
    # Random choice a sticker from my_sticker list
    ran_sticker = random.choice(my_sticker)
    # Reply Sticker Message
    My_LineBotAPI.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id= ran_sticker.packageID,
            sticker_id= ran_sticker.stickerID
        )
    )
if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app='main:app', reload=True, host='0.0.0.0', port=8787)