from time import sleep
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
import os
from random import choice

def status():
    path = './data/status/command'
    Module = 'grass_collector'
    Command = ['#grass get','#grass add','#grass del']
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
    if not os.path.exists(path):
        os.makedirs(path)
        

wait = {}
state = 0
examine = []
admin = 2321247175
path = './data/grass/'
prepare(path)
status()
channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)


async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    global wait,examine,state
    msg = message.asDisplay()
    if msg[0:6] == '#grass':
        msg = msg.split()[1:]
        msg_chain = MessageChain.create()
        if msg[0] == 'add' and len(msg) == 1:
            wait.update({member.id:'add'})
            msg_chain.append('请发送生草图')
        elif msg[0] == 'get' and len(msg) == 1:
            grass = grass_get()
            msg_chain=MessageChain.fromPersistentString(grass[0])
            msg_chain.append(f'\n编号为{grass[1]}')
        if msg_chain:
            await app.sendGroupMessage(group,msg_chain)
    elif member.id in wait:
        msg_chain = MessageChain.create()
        if wait[member.id] == 'add':
            if Image not in message:
                msg_chain.append('未发现图片!')
            else:
                if member.id == admin:
                    index = grass_save(message.asPersistentString())
                    msg_chain.append(f'添加成功!该生草图编号为{index}')
                else:
                    msg_chain.append('已发送给KuborKelp进行审核')
                    examine.append([member,group,message])
                    await app.sendFriendMessage(admin,MessageChain.create('有新的grass!,开始审核请输入#start or s'))
                    state += 1
            del wait[member.id]
        if msg_chain:
            await app.sendGroupMessage(group,msg_chain)
        
def grass_save(msg):
    global path
    files = os.listdir(path)
    i=0
    while str(i)+'.txt' in files:
        i+=1
    with open(f'{path}{i}.txt','w',encoding='utf-8') as txt:
        txt.write(msg)
    return i

def grass_get(index=-1):
    global path
    files = os.listdir(path)
    if index == -1:
        index = choice(files)
    with open (f'{path}{index}','r',encoding='utf-8') as txt:
        msg = txt.read()
        return [msg,index[:-4]]


@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
    )
)


async def main(app: Ariadne, message: MessageChain, friend:Friend):
    msg = message.asDisplay()
    if friend.id == admin:
        global examine,state
        msg_chain = MessageChain.create()
        if examine and msg in ['#start','s'] and state:
            member = examine[0][0]
            group = examine[0][1]
            msg_chain.append(f'来自{group.name}({group.id})的{member.name}({member.id}):允许:1;拒绝:0')
            await app.sendFriendMessage(admin,msg_chain)
            sleep(0.4)
            await app.sendFriendMessage(admin,examine[0][2])
        if msg[0] == '1':
            index = grass_save(examine[0][2].asPersistentString())
            msg_chain.append(At(examine[0][0].id))
            msg_chain.append(f'您的生草图添加成功!该生草图编号为{index}')
            if msg != '1':
                msg_chain.append(f'评语:{msg[1:]}')
            await app.sendGroupMessage(examine[0][1],msg_chain)
            del examine[0]
            state -= 1
        elif msg[0] == '0':
            msg_chain.append(At(examine[0][0].id))
            msg_chain.append(f'您的生草图被拒绝添加!')
            if msg != '0':
                msg_chain.append(f'拒绝理由:{msg[1:]}')
            await app.sendGroupMessage(examine[0][1],msg_chain)
            del examine[0]
            state -= 1
            
    



    