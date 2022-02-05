from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain
from graia.ariadne.event.message import *
from random import choice
import os

def status():
    path = './data/status/command'
    Module = 'thunder'
    Command = ['#thunder','#thunder#']
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
channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    msg_chain = MessageChain.create()
    if msg == '#thunder':
        member_lst = await app.getMemberList(group)
        victim = choice(member_lst)
        msg_chain.append(f'{member.name}({member.id})劈中了{victim.name}({victim.id})')
    elif msg == '#thunder#':
        pass
    if msg_chain:
        await app.sendGroupMessage(group,msg_chain)