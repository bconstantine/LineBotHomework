'''
This is my LineBot API
How to Start:
    > Step 0. Go to ./Line
        > cd ./MVCLab-Summer-Course/LineBotHomework
    > Step 1. Install Python Packages
        > pip install -r requirements.txt
    > Step 2. Run main.py
        > python main.py
Reference:
1. LineBot API for Python
    > https://github.com/line/line-bot-sdk-python
2. Random 
    > https://pokemondb.net/pokedex/all
3. Line Developer Messaging API Doc
    > https://developers.line.biz/en/docs/messaging-api/
'''
from multiprocessing.sharedctypes import Value
import os
import re
import json
import random
from dotenv import load_dotenv
from pyquery import PyQuery
from fastapi import FastAPI, Request, HTTPException
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError

"""
init DB Class
"""
class DB():
    def __init__(self, ip, port, user, password, db_name):
        """db_name is measurement"""
        self.client = InfluxDBClient(ip, port, user, password, db_name)
        self.client.create_database(db_name) #to handle error: accounting_db database doesnt exist
        print('Influx DB Init successful')

    def insertData(self, data):
        """
        [data] should be a list of datapoint JSON,
        "measurement": means table name in db
        "tags": you can add some tag as key
        "fields": data that you want to store
        """
        if self.client.write_points(data):
            return True
        else:
            print('Falied to write data')
            return False

    def queryData(self, query):
        """
        [query] should be a SQL like query string
        """
        return self.client.query(query)

# Init a Influx DB and connect to it
db = DB('127.0.0.1', 8086, 'root', '', 'accounting_db')

load_dotenv() # Load your local environment variables

'''
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
'''

#create random study quote giver
study_quotes_link = 'https://www.goodreads.com/quotes/tag/study'
#get all quotes
d = PyQuery(url = study_quotes_link)
_quotes = list(d(".quoteText").map(lambda i,e: PyQuery(e).remove('span').remove('script').text()))
for i in range(len(_quotes)):
  _quotes[i] = _quotes[i].split('―')[0]
d = PyQuery(url = study_quotes_link)
_author = d(".quoteText").map(lambda i,e: PyQuery(e)(".authorOrTitle").text())
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
my_event = ['+', '-', '*', '/', '#help', '#note', '#report', '#delete', '#sum', '#quote']
"""format of note, query, delete and sum: 
note: #note <event> 
report: #report <event> [+/-] <amount>
delete: #delete <event>
sum: #sum <duration> 

where duration: 
u or µ microseconds 
ms milliseconds 
s seconds 
m minutes 
h hours 
d days 
w weeks
"""

supported_intervals = ["u", "ms", "s", "m", "h", "d", "w"]
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
    #clean equal sign
    if(len(recieve_message) == 4 and recieve_message[3]=='='):
        recieve_message.pop(3)
    # Get first splitted message as command
    case_ = recieve_message[0].lower().strip()

    #verify input format
    formatVerified = False
    if len(recieve_message) == 3:
        if recieve_message[1] in my_event:
            formatVerified = True
    elif len(recieve_message) == 4 and case_ == "#note":
        formatVerified = True
    elif len(recieve_message) == 2:
        if case_ == "#delete":
            formatVerified = True
        elif case_ == "#sum" and recieve_message[1][-1] in supported_intervals: 
            formatVerified = True
    elif len(recieve_message) == 1 and case_ in ["#help", '#report', '#quote']:
        formatVerified = True

    if(formatVerified):
        # Help command for listing all commands to user
        if my_event[4] == case_:
            command_describtion = '$ Commands:\n\
            <decimal> + <decimal>\n\t-->Show the result of the addition\n\
            <decimal> - <decimal>\n\t-->Show the result of the subtraction\n\
            <decimal> * <decimal>\n\t-->Show the result of the multiplication\n\
            <decimal> / <decimal>\n\t-->Show the result of the division\n\
            #quote\n\t-->get one random quote about studying\n\
            or send me any sticker to get a sticker reply!\n\n\n\
            Additionally, I can also help you record your expenses and income report! Use the following command:\n\
            note: #note <event> [+/-] <amount>\n\t-->record your expenses(-) or income(+) amount in current event\n\
            report: #report\n\t-->Show all of your recorded income and expenses\n\
            delete: #delete <event>\n\t-->Delete all income/expenses event with the name you give!\n\
            sum: #sum <amount><duration>\n\t-->Sum income and expenses in now - (duration) prior!\n\n\
            Supported intervals for sum are as below:\n\
            u or µ microseconds\n\
            ms milliseconds\n\
            s seconds\n\
            m minutes\n\
            h hours\n\
            d days\n\
            w weeks\n\
            As an example, #sum 1d will total all the expenses and income in 1 day prior!'
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
        elif my_event[5] == case_:
            event_ = recieve_message[1]
            op = recieve_message[2]
            money = None
            try:
                money = int(recieve_message[3])
            except ValueError:
                My_LineBotAPI.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text='$ Money amount is invalid! Check again input!', 
                            emojis = [
                            {
                                'index':0,
                                'productId':'5ac1bfd5040ab15980c9b435',
                                'emojiId':'004'
                            }
                        ])
                    )
            else:
                # process +/-
                if op == '-':
                    money *= -1
                # get user id
                user_id = event.source.user_id
                
                # build data
                data = [
                    {
                        "measurement" : "accounting_items",
                        "tags": {
                            "user": str(user_id),
                            # "category" : "food"
                        },
                        "fields":{
                            "event": str(event_),
                            "money": money
                        }
                    }
                ]
                if db.insertData(data):
                    # successed
                    My_LineBotAPI.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text="Write to DB Successfully!"
                        )
                    )
        elif my_event[6] == case_:
            #report
            user_id = event.source.user_id
            query_str = """
            select * from accounting_items 
            """
            try:
                result = db.queryData(query_str)
                points = result.get_points(tags={'user': str(user_id)})
            except:
                My_LineBotAPI.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text="Database error! Perhaps database is empty?")
                )
            else:
                reply_text = ''
                for i, point in enumerate(points):
                    time = point['time']
                    event_ = point['event']
                    money = point['money']
                    reply_text += f'[{i}] -> [{time}] : {event_}   {money}\n'

                My_LineBotAPI.reply_message(
                    event.reply_token,
                    TextSendMessage(
                        text=reply_text)
                )
        elif case_ == my_event[7]:
            #delete
            user_id = str(event.source.user_id)
            deleteEvent = recieve_message[1]
            db.queryData(f"SELECT * INTO temporary FROM accounting_items WHERE \"event\"!=\'{deleteEvent}\'")
            db.queryData("DROP measurement accounting_items")
            result =db.queryData("SELECT * INTO accounting_items FROM temporary")
            db.queryData("DROP measurement temporary")
            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=f"Deleted {deleteEvent}!"
                )
            )
            
        elif case_ == my_event[8]:
            #sum
            # get user id
            user_id = event.source.user_id
            query_str = """
            select * from accounting_items where time > now() - """
            query_str += recieve_message[1]
            result = db.queryData(query_str)
            points = result.get_points(tags={'user': str(user_id)})

            totalSum = 0
            for i, point in enumerate(points):
                totalSum += point['money']

            My_LineBotAPI.reply_message(
                event.reply_token,
                TextSendMessage(
                    text=f"Your {recieve_message} prior money amount: {totalSum}"
                )
            )
        elif case_ == my_event[9]:
            #get random quote
            #reply with quote
            index = random.randrange(min(len(_quotes), len(_author)))
            My_LineBotAPI.reply_message(
                                event.reply_token,
                                TextSendMessage(
                                    text=f'{_quotes[index]}\n\nby: {_author[index]}')
                    )
        else:
            #calculator mode
            case_ = recieve_message[1].lower().strip()
            # Case 1: add
            if my_event[0] == case_:
                num1 = None
                num2 = None
                try:
                    num1 = float(recieve_message[0].lower().strip())
                    num2 = float(recieve_message[2].lower().strip())
                except ValueError:
                    My_LineBotAPI.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text='$ Either LHS of RHS number is invalid! Check again input!', 
                            emojis = [
                            {
                                'index':0,
                                'productId':'5ac1bfd5040ab15980c9b435',
                                'emojiId':'004'
                            }
                        ])
                    )
                else:
                    num1 += num2
                    My_LineBotAPI.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text=f'Result: {num1}')
                    )
            # Case 2: subtract
            elif my_event[1] == case_:
                num1 = None
                num2 = None
                try:
                    num1 = float(recieve_message[0].lower().strip())
                    num2 = float(recieve_message[2].lower().strip())
                except ValueError:
                    My_LineBotAPI.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text='$ Either LHS of RHS number is invalid! Check again input!', 
                            emojis = [
                            {
                                'index':0,
                                'productId':'5ac1bfd5040ab15980c9b435',
                                'emojiId':'004'
                            }
                        ])
                    )
                else:
                    num1 -= num2
                    My_LineBotAPI.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text=f'Result: {num1}')
                    )
            # Case 3: multiply
            elif my_event[2] == case_:
                num1 = None
                num2 = None
                try:
                    num1 = float(recieve_message[0].lower().strip())
                    num2 = float(recieve_message[2].lower().strip())
                except ValueError:
                    My_LineBotAPI.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text='$ Either LHS of RHS number is invalid! Check again input!', 
                            emojis = [
                            {
                                'index':0,
                                'productId':'5ac1bfd5040ab15980c9b435',
                                'emojiId':'004'
                            }
                        ])
                    )
                else:
                    num1 *= num2
                    My_LineBotAPI.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text=f'Result: {num1}')
                    )
            # Case 4: divide
            elif my_event[3] == case_:
                num1 = None
                num2 = None
                try:
                    num1 = float(recieve_message[0].lower().strip())
                    num2 = float(recieve_message[2].lower().strip())
                    num1 /= num2
                except ValueError:
                    My_LineBotAPI.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text='$ Either LHS of RHS number is invalid! Check again input!', 
                            emojis = [
                            {
                                'index':0,
                                'productId':'5ac1bfd5040ab15980c9b435',
                                'emojiId':'004'
                            }
                        ])
                    )
                except ZeroDivisionError:
                    My_LineBotAPI.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text='$ The divisior is zero, invalid!', 
                            emojis = [
                            {
                                'index':0,
                                'productId':'5ac1bfd5040ab15980c9b435',
                                'emojiId':'004'
                            }
                        ])
                    )
                else:
                    My_LineBotAPI.reply_message(
                        event.reply_token,
                        TextSendMessage(
                            text=f'Result: {num1}')
                    )
    else:
        My_LineBotAPI.reply_message(
            event.reply_token,
            TextSendMessage(
                text='$ Welcome to Calculator ! Enter "#help" for commands !',
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