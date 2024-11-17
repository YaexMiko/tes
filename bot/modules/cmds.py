from asyncio import sleep as asleep, gather
from pyrogram.filters import command, private, user
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import FloodWait, MessageNotModified

from bot import bot, bot_loop, Var, ani_cache
from bot.core.database import db
from bot.core.func_utils import decode, is_fsubbed, get_fsubs, editMessage, sendMessage, new_task, convertTime, getfeed
from bot.core.auto_animes import get_animes
from bot.core.reporter import rep

@bot.on_message(command('start') & private)
@new_task
async def start_msg(client, message):
    uid = message.from_user.id
    from_user = message.from_user
    txtargs = message.text.split()
    temp = await sendMessage(message, "<b>𝙲𝚘𝚗𝚗𝚎𝚌𝚝𝚒𝚗𝚐..</b>")
    if not await is_fsubbed(uid):
        txt, btns = await get_fsubs(uid, txtargs)
        return await editMessage(temp, txt, InlineKeyboardMarkup(btns))
    if len(txtargs) <= 1:
        await temp.delete()
        btns = []
        for elem in Var.START_BUTTONS.split():
            try:
                bt, link = elem.split('|', maxsplit=1)
            except:
                continue
            if len(btns) != 0 and len(btns[-1]) == 1:
                btns[-1].insert(1, InlineKeyboardButton(bt, url=link))
            else:
                btns.append([InlineKeyboardButton(bt, url=link)])
        smsg = Var.START_MSG.format(first_name=from_user.first_name,
                                    last_name=from_user.first_name,
                                    mention=from_user.mention, 
                                    user_id=from_user.id)
        if Var.START_PHOTO:
            await message.reply_photo(
                photo=Var.START_PHOTO, 
                caption=smsg,
                reply_markup=InlineKeyboardMarkup(btns) if len(btns) != 0 else None
            )
        else:
            await sendMessage(message, smsg, InlineKeyboardMarkup(btns) if len(btns) != 0 else None)
        return
    try:
        arg = (await decode(txtargs[1])).split('-')
    except Exception as e:
        await rep.report(f"User : {uid} | Error : {str(e)}", "error")
        await editMessage(temp, "<b>𝙸𝚗𝚙𝚞𝚝 𝙻𝚒𝚗𝚔 𝙲𝚘𝚍𝚎 𝙳𝚎𝚌𝚘𝚍𝚎 𝙵𝚊𝚒𝚕𝚎𝚍 !</b>")
        return
    if len(arg) == 2 and arg[0] == 'get':
        try:
            fid = int(int(arg[1]) / abs(int(Var.FILE_STORE)))
        except Exception as e:
            await rep.report(f"User : {uid} | Error : {str(e)}", "error")
            await editMessage(temp, "<b>𝙸𝚗𝚙𝚞𝚝 𝙻𝚒𝚗𝚔 𝙲𝚘𝚍𝚎 𝙳𝚎𝚌𝚘𝚍𝚎 𝙵𝚊𝚒𝚕𝚎𝚍 !</b>")
            return
        try:
            msg = await client.get_messages(Var.FILE_STORE, message_ids=fid)
            if msg.empty:
                return await editMessage(temp, "<b>𝙵𝚒𝚕𝚎 𝙽𝚘𝚝 𝙵𝚘𝚞𝚗𝚍 !</b>")
            nmsg = await msg.copy(message.chat.id, reply_markup=None)
            await temp.delete()
            if Var.AUTO_DEL:
                async def auto_del(msg, timer):
                    await asleep(timer)
                    await msg.delete()
                await sendMessage(message, f'<b>𝙵𝚒𝚕𝚎 𝚆𝚒𝚕𝚕 𝙱𝚎 𝙰𝚞𝚝𝚘 𝙳𝚎𝚕𝚎𝚝𝚎𝚍 𝙸𝚗 {convertTime(Var.DEL_TIMER)}, 𝙵𝚘𝚛𝚠𝚊𝚛𝚍 𝚃𝚘 𝚂𝚊𝚟𝚎𝚍 𝙼𝚎𝚜𝚜𝚊𝚐𝚎𝚜 𝙽𝚘𝚠....</b>')
                bot_loop.create_task(auto_del(nmsg, Var.DEL_TIMER))
        except Exception as e:
            await rep.report(f"User : {uid} | Error : {str(e)}", "error")
            await editMessage(temp, "<b>𝙵𝚒𝚕𝚎 𝙽𝚘𝚝 𝙵𝚘𝚞𝚗𝚍 !</b>")
    else:
        await editMessage(temp, "<b>𝙸𝚗𝚙𝚞𝚝 𝙻𝚒𝚗𝚔 𝙸𝚜 𝙸𝚗𝚟𝚊𝚕𝚒𝚍 𝚏𝚘𝚛 𝚄𝚜𝚊𝚐𝚎 !</b>")
    
@bot.on_message(command('pause') & private & user(Var.ADMINS))
async def pause_fetch(client, message):
    ani_cache['fetch_animes'] = False
    await sendMessage(message, "𝚂𝚞𝚌𝚌𝚎𝚜𝚜𝚏𝚞𝚕𝚕𝚢 𝙿𝚊𝚞𝚜𝚎𝚍 𝙵𝚎𝚝𝚌𝚑𝚒𝚗𝚐 𝙰𝚗𝚒𝚖𝚎𝚜...`")

@bot.on_message(command('resume') & private & user(Var.ADMINS))
async def pause_fetch(client, message):
    ani_cache['fetch_animes'] = True
    await sendMessage(message, "𝚂𝚞𝚌𝚌𝚎𝚜𝚜𝚏𝚞𝚕𝚕𝚢 𝚁𝚎𝚜𝚞𝚖𝚎𝚍 𝙵𝚎𝚝𝚌𝚑𝚒𝚗𝚐 𝙰𝚗𝚒𝚖𝚎𝚜...`")

@bot.on_message(command('log') & private & user(Var.ADMINS))
@new_task
async def _log(client, message):
    await message.reply_document("log.txt", quote=True)

@bot.on_message(command('addlink') & private & user(Var.ADMINS))
@new_task
async def add_task(client, message):
    if len(args := message.text.split()) <= 1:
        return await sendMessage(message, "<b>𝙽𝚘 𝙻𝚒𝚗𝚔 𝙵𝚘𝚞𝚗𝚍 𝚃𝚘 𝙰𝚍𝚍</b>")
    
    Var.RSS_ITEMS.append(args[0])
    req_msg = await sendMessage(message, f"𝙶𝚕𝚘𝚋𝚊𝚕 𝙻𝚒𝚗𝚔 𝙰𝚍𝚍𝚎𝚍 𝚂𝚞𝚌𝚌𝚎𝚜𝚜𝚏𝚞𝚕𝚕𝚢!`\n\n    • **𝙰𝚕𝚕 𝙻𝚒𝚗𝚔(𝚜) :** {', '.join(Var.RSS_ITEMS)[:-2]}")

@bot.on_message(command('addtask') & private & user(Var.ADMINS))
@new_task
async def add_task(client, message):
    if len(args := message.text.split()) <= 1:
        return await sendMessage(message, "<b>𝙽𝚘 𝚃𝚊𝚜𝚔 𝙵𝚘𝚞𝚗𝚍 𝚃𝚘 𝙰𝚍𝚍</b>")
    
    index = int(args[2]) if len(args) > 2 and args[2].isdigit() else 0
    if not (taskInfo := await getfeed(args[1], index)):
        return await sendMessage(message, "<b>𝙽𝚘 𝚃𝚊𝚜𝚔 𝙵𝚘𝚞𝚗𝚍 𝚃𝚘 𝙰𝚍𝚍 𝙵𝚘𝚛 𝚃𝚑𝚎 𝙿𝚛𝚘𝚟𝚒𝚍𝚎𝚍 𝙻𝚒𝚗𝚔</b>")
    
    ani_task = bot_loop.create_task(get_animes(taskInfo.title, taskInfo.link, True))
    await sendMessage(message, f"<b>𝚃𝚊𝚜𝚔 𝙰𝚍𝚍𝚎𝚍 𝚂𝚞𝚌𝚌𝚎𝚜𝚜𝚏𝚞𝚕𝚕𝚢!</b>\n\n    • <b>𝚃𝚊𝚜𝚔 𝙽𝚊𝚖𝚎 :</b> {taskInfo.title}\n    • <b>𝚃𝚊𝚜𝚔 𝙻𝚒𝚗𝚔 :</b> {args[1]}")
