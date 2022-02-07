from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Image, Plain, At,Forward, ForwardNode
from graia.ariadne.event.message import *
import os
import random
import datetime

def status():
    path = './data/status/command'
    Module = 'fun'
    Command = ['#choose','#yys','#create']
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

status()
yys_ht  =['坚硬','疲软','松弛','富有弹性','快乐','隐忍','健康']
yys = random.choice(yys_ht)


channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)


async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    msg_chain = MessageChain.create()
    if msg[0:7] == '#choose':
        msg_chain.append('选择:')
        msg = msg.split(' ')[1:]
        msg_chain.append(random.choice(msg))
    elif msg.lower() == '#yys':
        if random.randint(0,3) == 1:
            global yys,yys_ht
            yys = random.choice(yys_ht)
        msg_chain.append(f'!!yys后庭目前很{yys}')    
    elif msg[0:7] == '#create':
        msg = msg[8:].split(';')
        node = []
        for i in msg:
            i = i.replace('@','').replace('：',':').split(':')
            if len(i) == 3:
                senderName = i[2]
            else:
                senderName = i[0]
            node.append(
            ForwardNode(
                senderId=i[0],
                time=datetime.datetime.now(),
                senderName=senderName,
                messageChain=MessageChain.create(i[1]),
            ))
        await app.sendMessage(group, MessageChain.create(Forward(nodeList=node)))      
    if msg[0] == '啊' and len(msg)>=2:
        for i in msg[1:]:
            if i != '对':
                break
        else:
            msg_chain.append(msg+'对')
            
    if msg_chain:
        await app.sendGroupMessage(group, msg_chain)

def get(mid, day):
    path = f'./rp/{mid}/{day}.txt'
    if not os.path.exists(f'./rp/{mid}'):
        os.makedirs(f'./rp/{mid}')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as rp_txt:
            line = rp_txt.readline().split(';')
            rp = list(map(int, line))
    else:
        with open(path, 'w+', encoding='utf-8') as rp_txt:
            rp = [random.randint(0, 100), 0]
            rp_txt.write(f'{rp[0]};{rp[1]}')
    return rp


def change(mid, day, value):
    path = f'./rp/{mid}/{day}.txt'
    rp = get(mid, day)

    rp[1] = rp[1] + value
    with open(path, 'w+', encoding='utf-8') as rp_txt:
        rp_txt.write(f'{rp[0]};{rp[1]}')
