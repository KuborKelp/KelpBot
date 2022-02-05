from tkinter import E
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
import os
import datetime
import time


def status():
    path = './data/status/command'
    Module = 'toolkit'
    Command = ['#calc','#hexconvert','#helltp']
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
calc_char = '0123456789+-*/.e'
channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    if msg[0:5] == '#calc':
        msg = msg[6:]
        not_allowed = ''
        for char in msg:
            if char not in calc_char and char not in not_allowed:
                not_allowed += char
        if not_allowed != '':
            reply = f'非法字符{not_allowed}'
        else:
            reply = eval(msg)
        await app.sendGroupMessage(group,MessageChain.create(Plain(reply)))
    elif msg[0:11] == '#hexconvert':
        msg = msg[12:].replace('->',' ').split(' ')
        a = int(msg[0])
        b = int(msg[1])
        data = msg[2]
        if b>1 and a>1:
            await app.sendGroupMessage(group,MessageChain.create(Plain(f'{data}:{a}->{b}结果为{binary(a,b,data)}')))
    elif msg[0:7] == '#helltp':
        pt = list(map(int,msg.split()[1:]))
        if len(pt) != 2:
            await app.sendGroupMessage(group,MessageChain.create(Plain('格式错误,正确格式为#helltp x y')))
        else:
            line1 = f'主世界->地狱 {pt[0]//8},{pt[1]//8}'
            line2 = f'地狱->主世界 {pt[0]*8},{pt[1]*8}'
            await app.sendGroupMessage(group,MessageChain.create(Plain(f'{line1}\n{line2}')))
        


def binary(a,b,data):
    dic = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    result = ''
    i = len(data)-1
    s=0
    q=1
    while i>=0:
        s += q*dic.find(data[i])
        q *= a
        i -= 1
    while s>0:
        result = dic[s%b]+result
        s = s//b
    return result