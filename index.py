from telethon import TelegramClient,events,Button
from telethon.tl.functions.channels import GetParticipantsRequest
import threading
from os import path
from subprocess import Popen as P
from json import load,dump
from requests import get as G
from config import *
api = 'https://api.binance.com/api/v3/ticker/price?symbol='
if not path.exists('db.json'):
    with open('db.json','w') as i:
        dump({'alarms':dict(),'users':dict(),'limit':5},i)


def SEND(message):
    P(['python','send.py','send',str(message)])

unknown = TelegramClient('bot',api_id,api_hash).start(bot_token=token)

@unknown.on(events.NewMessage(func=lambda e: e.is_private,outgoing=False))
async def index(event):
    key = [
        [Button.text('ثبت آلارم',resize=True)],
        [Button.text('آلارم های من'),Button.text('حذف آلارم')],
        [Button.text('خرید اشتراک نامحدود'),Button.text('پشتیبانی')]
    ]
    back = [[Button.inline('🔙 بازگشت','back')]]
    check = 1 if G(f'https://api.telegram.org/bot{token}/getChatMember?chat_id={channel_id}&user_id={event.sender_id}').json()['result']['status'] == 'left' else 0
    if check:
        await event.reply(join_text,buttons=[[Button.inline('✅ تایید عضویت ✅',b'JC')]])
    else:
        with open('db.json') as i:
            x = load(i)
        if not str(event.sender_id) in x['users']:
            x['users'][str(event.sender_id)] = {'type':False,'step':'home'}
            with open('db.json','w') as i:
                dump(x,i)
            await event.reply('🔥 از گزینه های پایین استفاده کن :',buttons=key)
        elif str(event.sender_id) in x['users'] and event.raw_text == '/start':
            x['users'][str(event.sender_id)]['step'] = 'home'
            with open('db.json','w') as i:
                dump(x,i)
            await event.reply('🔥 از گزینه های پایین استفاده کن :',buttons=key)
        elif not str(event.sender_id) in x['users'] and event.raw_text == '/start':
            x['users'][str(event.sender_id)] = {'type':False,'step':'home'}
            with open('db.json','w') as i:
                dump(x,i)
            await event.reply('🔥 از گزینه های پایین استفاده کن :',buttons=key)

        if event.raw_text.lower().startswith('/alarm'):
            text = event.raw_text.split()
            Req = G(api+str(text[1]).upper()).json()
            if 'price' in Req:
                if str(event.sender_id) in x['alarms']:
                    if x['users'][str(event.sender_id)]['type'] or len(x['alarms'][str(event.sender_id)]) < int(x['limit']):
                        try:
                            if not '0x' in text[2] or not '0o' in text[2] or not '0b' in text[2]:
                                text[2] = float(text[2])
                            else:
                                raise ValueError
                            CHECK = True
                            for n in x['alarms'][str(event.sender_id)]:
                                if n['symbol'] == str(text[1]).upper() and str(n['price']) == str(text[2]):
                                    CHECK = 0
                                    break
                            if CHECK:
                                if float(Req['price']) > float(text[2]):
                                    St = 'D'
                                else:
                                    St = 'U'
                                x['alarms'][str(event.sender_id)].append({'price':str(text[2]),'symbol':str(text[1]).upper(),'S':St})
                                await event.reply('✨ آلارم با موفقیت ست شد , برای دیدن آلارم های اکانتت از گزینه های پایین استفاده کن',buttons=key)
                            else:
                                await event.reply('😐 قبلا هم یک الرت مثل همین ثبت کردی!')
                        except ValueError:
                            await event.reply('😕 عدد وارد شده صحیح نیست , یک عدد صحیح وارد کن')
                    else:
                        await event.reply(f'❌ شما {x["limit"]} آلارم فعال دارید , برای ست کردن آلارم بیشتر باید حساب vip خریداری کنید یا یک آلارم حذف کنید.\n👤 پشتیبانی : {sup}')
                else:
                    if text[2].isdigit():
                        x['alarms'][str(event.sender_id)] = [{'price':str(text[2]),'symbol':str(text[1]),'S':'D' if float(Req['price']) > float(text[2]) else 'U'}]
                        await event.reply('✨ آلارم با موفقیت ست شد , برای دیدن آلارم های اکانتت از گزینه های پایین استفاده کن')
                with open('db.json','w') as i:
                    dump(x,i)
            else:
                await event.reply(f'‼️ ارزی به نام {text[1]} پیدا نشد')
        elif event.raw_text == 'آلارم های من':
            if str(event.sender_id) in x['alarms'] and len(x['alarms'][str(event.sender_id)]) >= 1:
                text_ = '🔅 آلارم های ثبت شده اکانت شما شامل آلارم های زیر میباشند :\n\n'
                N = 1
                for n in x['alarms'][str(event.sender_id)]:
                    text_ += str(N)+'. '+str(n['symbol'])+' '+str(n['price'])+str(' ⬇️' if n['S']=='D' else ' ⬆️')+'\n'
                    N += 1
                text_ += '\n\n🔥 برای حذف هر آلارمی , از دکمه های زیر استفاده کن'
                await event.reply(text_)
            else:
                await event.reply('❌ هنوز آلارمی ثبت نکردی')
        elif event.raw_text == 'حذف آلارم':
            if str(event.sender_id) in x['alarms'] and len(x['alarms'][str(event.sender_id)]) > 0:
                button_s = [[Button.inline(i['symbol']+' '+i['price'],f'Alert_{i}')] for i in x['alarms'][str(event.sender_id)]]
                await event.reply('⚙️ برای حذف هرکدام از آلارم ها روی اون کلیک کن :',buttons=button_s)
            else:
                await event.reply('🤷🏻‍♂️ شما آلارمی اضافه نکردید که بخواید حذفش کنید')

        elif x['users'][str(event.sender_id)]['step'] == 'set vip' and event.sender_id == admin:
            if str(event.raw_text) in x['users']:
                await unknown.send_message(int(event.raw_text),'✨ حساب شما توسط مدیر ربات vip شد و از این پس محدودیتی برای ثبت آلارم ندارید.',buttons=key)
                x['users'][str(event.raw_text)]['type'] = True
                x['users'][str(event.sender_id)]['step'] = 'home'
                with open('db.json','w') as i:
                    dump(x,i)
                await event.reply('🔥 حساب کاربری مورد نظر با موفقیت vip شد و محدودیتی برای ثبت آلارم ندارد')
            else:
                await event.reply('❌ یوزر آیدی کاربر اشتباه است و یا ربات را /start نکرده.')


        elif x['users'][str(event.sender_id)]['step'] == 'del vip' and event.sender_id == admin:
            if str(event.raw_text) in x['users']:
                await unknown.send_message(int(event.raw_text),'❌ حساب vip شما توسط ادمین ربات به حساب معمولی تبدیل شد , در صورت بروز هرگونه مشکل از گزینه های پایین با پشتیبانی تماس بگیرید.',buttons=key)
                x['users'][str(event.raw_text)]['type'] = False
                x['users'][str(event.sender_id)]['step'] = 'home'
                with open('db.json','w') as i:
                    dump(x,i)
                await event.reply('🔥 حساب vip کاربری مورد نظر با موفقیت به حساب معمولی تبدیل شد')
            else:
                await event.reply('❌ یوزر آیدی کاربر اشتباه است و یا ربات را /start نکرده.')

        elif x['users'][str(event.sender_id)]['step'] == 'set limit' and event.sender_id == admin:
            TT = event.raw_text.lower()
            try:
                if not '0x' in TT or not '0o' in TT or not '0b' in TT:
                    TT = float(TT)
                else:
                    raise ValueError
                x['limit'] = TT
                x['users'][str(event.sender_id)]['step'] = 'home'
                with open('db.json','w') as i:
                    dump(x,i)
                await event.reply('✅ محدودیت با موفقیت تنظیم شد')
            except ValueError:
                await event.reply('❌ عدد وارد شده صحیح نیست\n✅ مجددا تلاش کنید :',buttons=back)
        elif event.raw_text == 'ثبت آلارم':
            await event.reply(help_text)

        elif event.raw_text == 'خرید اشتراک نامحدود':
            await event.reply(f'✨ رفیق ممنون که به ما اعتماد میکنی\n\nبرای خرید اشتراک ماهانه , کافیه فیش واریزی خودت رو به پشتیبانی ارسال کنی.\n\nشماره کارت واریزی به نام حیدر منصوری : \n6219861915702079\n\n✨ اشتراک یک ماه : 49T\n\n✨ اشتراک دوماهه : 89T\n\n✨ اشتراک سه ماهه : 115T\n\nپشتیبانی : {sup}')

        elif event.raw_text == '🔴 قطع مکالمه 🔴':
            x['users'][str(event.sender_id)]['step'] = 'home'
            with open('db.json','w') as i:
                dump(x,i)
            await event.reply('برگشتیم , یکی از دکمه های زیر رو انتخاب کن 🦾',buttons=key)

        elif event.raw_text == 'پشتیبانی':
            x['users'][str(event.sender_id)]['step'] = 'sup'
            with open('db.json','w') as i:
                dump(x,i)
            await event.reply('📍 شما به پشتیبانی متصل شدی , پیامتو ارسال کن تا به پشتیبانی برسونم',buttons=[[Button.text('🔴 قطع مکالمه 🔴',resize=True)]])
        elif x['users'][str(event.sender_id)]['step'] == 'sup':
            text__ = f"""🟢 پیام جدیدی از سمت کاربر {event.sender.first_name} دریافت شد
🔻 متن پیام :
➖➖➖➖➖➖➖➖➖
{event.raw_text}
➖➖➖➖➖➖➖➖➖
🔸 برای جواب دادن به پیام از دکمه زیر استفاده کن"""
            await unknown.send_message(admin,text__,buttons=[[Button.inline('♻️ پاسخ به کاربر ♻️',f'answer_{event.sender_id}')]])
            await event.reply('✅ ارسال شد')

        elif x['users'][str(event.sender_id)]['step'].startswith('answer_'):
            ID = int(x['users'][str(event.sender_id)]['step'].split('_')[1])
            x['users'][str(event.sender_id)]['step'] = 'home'
            t_ = f"""🔥 پیام جدیدی از سمت پشتیبانی دریافت کردید
✨ متن پیام :
➖➖➖➖➖➖➖
{event.raw_text}
➖➖➖➖➖➖➖"""
            await unknown.send_message(ID,t_)
            with open('db.json','w') as i:
                dump(x,i)
            await event.reply('✅ با موفقیت ارسال شد',buttons=key)


        elif event.raw_text.lower() in ['panel','پنل','/panel','پنل مدیریت'] and event.sender_id == admin:
            admin_ = [
                [Button.inline('🔅 دریافت آمار ربات 🔅','amar'),Button.inline('⚙️ پیام همگانی ⚙️','PHM')],
                [Button.inline('✨ vip ✨','vip'),Button.inline('🔧 تنظیم limit 🔧','limit_')],
                [Button.inline('❌ بستن پنل ❌','Del_')]
            ]
            await event.reply('🔥 سلام ادمین , به پنل مدیریت خوش آمدی , از دکمه های زیر استفاده کن :',buttons=admin_)
        elif x['users'][str(event.sender_id)]['step'] == 'phm' and event.sender_id == admin:
            x['users'][str(event.sender_id)]['step'] = 'home'
            with open('db.json','w') as i:
                dump(x,i)
            T_ = threading.Thread(target=SEND,args=(event.raw_text,))
            T_.start()
            await event.reply('♻️ درحال ارسال پیام به همه کاربران ربات . . .',buttons=back)


@unknown.on(events.CallbackQuery())
async def Query(event):
    key = [
        [Button.text('ثبت آلارم',resize=True)],
        [Button.text('آلارم های من'),Button.text('حذف آلارم')],
        [Button.text('خرید اشتراک نامحدود'),Button.text('پشتیبانی')]
    ]
    admin_ = [
        [Button.inline('🔅 دریافت آمار ربات 🔅','amar'),Button.inline('⚙️ پیام همگانی ⚙️','PHM')],
        [Button.inline('✨ vip ✨','vip'),Button.inline('🔧 تنظیم limit 🔧','limit_')],
        [Button.inline('❌ بستن پنل ❌','Del_')]
    ]
    back = [[Button.inline('🔙 بازگشت','back')]]
    with open('db.json') as i:
        x = load(i)
    data = event.data.decode()
    if data == 'JC':
        check = 1 if G(f'https://api.telegram.org/bot{token}/getChatMember?chat_id={channel_id}&user_id={event.sender_id}').json()['result']['status'] == 'left' else 0
        if check:
            await event.answer('❌ هنوز توی چنل جوین نشدی')
        else:
            if not str(event.sender_id) in x['users']:
                x['users'][str(event.sender_id)] = {'type':False,'step':'home'}
                with open('db.json','w') as i:
                    dump(x,i)
            await event.respond('🤍 عضویت شما با موفقیت تایید شد , برای دریافت راهنمای ربات از دکمه های زیر استفاده کن :',buttons=key)
            await event.delete()
    elif data.startswith('Alert_'):
        D = eval(data.split('_')[1])
        x['alarms'][str(event.sender_id)].remove(D)
        with open('db.json','w') as i:
            dump(x,i)
        await event.edit('✅ با موفقیت حذف شد')
    
    elif data.startswith('answer_'):
        x['users'][str(event.sender_id)]['step'] = f'answer_{data.split("_")[1]}'
        with open('db.json','w') as i:
            dump(x,i)
        await event.edit('‼️ پیامتو ارسال کن تا بفرستم بهش :',buttons=[[Button.inline('😆 منصرف شدم','C')]])
    elif data == 'C':
        x['users'][str(event.sender_id)]['step'] = 'home'
        with open('db.json','w') as i:
            dump(x,i)
        await event.answer('باشه :)')
        await event.edit('❌ بسته شده ❌',buttons=[[Button.inline('🎉','A')]])
    elif data == 'amar':
        await event.answer('🧿 آمار ربات شما : '+str(len(x['users'])))
    elif data == 'vip':
        VIP = [
            [Button.inline('✅ تنظیم vip ✅','set_v'),Button.inline('❌ حذف vip ❌','del_v')],
            [Button.inline('🔙 بازگشت','back')]
        ]
        await event.edit('🔅 از گزینه های پایین استفاده کن :',buttons=VIP)
    elif data == 'set_v':
        x['users'][str(event.sender_id)]['step'] = 'set vip'
        with open('db.json','w') as i:
            dump(x,i)
        await event.edit('📝 آیدی عددی کاربر مورد نظر رو ارسال کن تا حسابشو vip کنم',buttons=back)
    elif data == 'del_v':
        x['users'][str(event.sender_id)]['step'] = 'del vip'
        with open('db.json','w') as i:
            dump(x,i)
        await event.edit('📝 آیدی عددی کاربر مورد نظر رو ارسال کن تا vip شو بردارم :',buttons=back)

    elif data == 'back':
        x['users'][str(event.sender_id)]['step'] = 'home'
        with open('db.json','w') as i:
            dump(x,i)
            await event.edit('🔥 سلام ادمین , به پنل مدیریت خوش آمدی , از دکمه های زیر استفاده کن :',buttons=admin_)

    elif data == 'limit_':
        x['users'][str(event.sender_id)]['step'] = 'set limit'
        with open('db.json','w') as i:
            dump(x,i)
        await event.edit('🔅 عدد limit را ارسال کنید :',buttons=back)

    elif data == 'Del_':
        await event.edit('😎 پنل بسته شد')
    elif data == 'PHM':
        x['users'][str(event.sender_id)]['step'] = 'phm'
        with open('db.json','w') as i:
            dump(x,i)
        await event.edit('🎉 پیامتونو در قالب یک متن ارسال کنید تا به همه ممبرا بفرستم :',buttons=back)

def cron():
    while True:
        try:
            with open('db.json') as i:
                x = load(i)
            if len(x['alarms']) > 0:
                for i in x['alarms']:
                    for n in x['alarms'][i]:
                        if 'price' in n:
                            Price = n['price']
                            API = G(api+n['symbol'].upper()).json()['price']
                            if n['S'] == 'D':
                                if float(API) < float(Price):
                                    P(['python','send.py','D',str(i),str(n['price']),str(n['symbol']),str(API)])
                                    x['alarms'][i].remove(n)
                                    with open('db.json','w') as i:
                                        dump(x,i)
                            else:
                                if float(API) > float(Price):
                                    P(['python','send.py','U',str(i),str(n['price']),n['symbol'],str(API)])
                                    x['alarms'][i].remove(n)
                                    with open('db.json','w') as i:
                                        dump(x,i)
        except:
            pass

_thread = threading.Thread(target=cron)
_thread.start()
unknown.run_until_disconnected()