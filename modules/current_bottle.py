from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
from random import choice,randint
import os
import shutil
import time


def status():
    path = './data/status/command'
    Module = 'current_bottle'
    Command = ['#cb get','#cb send','#cb info','#cb throw_waste']
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(f'./data/status/modules/'):
        os.makedirs(f'./data/status/modules/')
    for i in Command:
        if not os.path.exists(path+'/'+i+'.txt'):
            with open(path+'/'+i+'.txt','w') as txt:
                txt.write('0')
    with open(f'./data/status/modules/{Module}','w') as txt:
                txt.write('0')


def prepare(path):
    leaves = ['old','available']
    for i in leaves:
        if not os.path.exists(path+i):
            os.makedirs(path+i)


status()
path = './data/currentbottle/'
send_wait = []
prepare(path)

channel = Channel.current()
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    global send_wait
    if msg[0:3] == '#cb':
        msg_chain = MessageChain.create()
        msg = msg.split()
        length = len(msg)
        if length == 1:
            msg_chain.append('#cb send -> 投出一个漂流瓶\n#cb get ->获取一个漂流瓶')
        elif length == 2:
            if msg[1] == 'send':
                send_wait.append(member.id)
                msg_chain.append('请发送漂流瓶内容=￣ω￣=')
            elif msg[1] == 'get':
                cb_list = get_cb()
                if cb_list:
                    if randint(0,randint(3,5)) == 1:
                        msg_chain.append('很遗憾,海里什么都捞不到😅')
                    else: 
                        cb = choice(cb_list)
                        with open(r'./data/currentbottle/available/'+cb,'r',encoding='utf-8') as bottle: #野蛮转义
                            msg_chain = MessageChain.fromPersistentString(bottle.read())
                        remove_cb(cb)
                        cb = cb[:-4].split('&')
                        msg_chain.append(f'\n来自{cb[0]}在{cb[1]}投出的的一只漂流瓶')
                else:
                    msg_chain.append('当前没有可拾取的漂流瓶,快扔一个给大伙看看😁')
            elif msg[1] == 'info':
                info = get_info()
                msg_chain.append(f'可获取的漂流瓶{info[0]}只\n已被拾取过的漂流瓶{info[1]}只')
        if msg_chain:
            await app.sendGroupMessage(group,msg_chain)
            time.sleep(0.1)
    elif member.id in send_wait:
        msg_chain = MessageChain.create()
        del send_wait[send_wait.index(member.id)]
        send_cb(message.asPersistentString(),get_time(),member.id)
        msg_chain.append('您的漂流瓶正在等待有缘人拾取!\^o^/')
        await app.sendGroupMessage(group,msg_chain)


def get_time():
    return time.strftime("%Y-%m-%d %X", time.localtime()).replace(':','-')


def send_cb(msg,time,member_id):
    path = './data/currentbottle/available'
    with open(f'./data/currentbottle/available/{member_id}&{time}.txt','w+',encoding='utf-8') as bottle:
        bottle.write(msg)


def get_cb():
    path = './data/currentbottle/available/'
    return os.listdir(path)


def remove_cb(cb):
    old_path = './data/currentbottle/available/'
    new_path = './data/currentbottle/old'
    shutil.move(old_path+cb,new_path)

def get_info():
    old_path = './data/currentbottle/available/'
    new_path = './data/currentbottle/old'
    return [len(os.listdir(old_path)),len(os.listdir(new_path))]