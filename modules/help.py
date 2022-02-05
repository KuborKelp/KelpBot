#from pydoc import plain
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Image, Plain, At,Forward, ForwardNode
from graia.ariadne.event.message import *
import os
import datetime

def status():
    path = './data/status/command'
    Module = 'help'
    Command = ['#help','#help add','#help del']
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
state = []
admin = 2321247175
path = './data/help/'
backup_path = './data/help/backup/'
help_path = './data/help/now/'
for i in [path,backup_path,help_path]:
    if not os.path.exists(i):
        os.makedirs(i)

channel = Channel.current()
@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)


async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    global state
    if msg[0:5] == '#help':
        msg_chain = MessageChain.create()  
        help_indexs = os.listdir(help_path)
        if msg == '#help':
            if not help_indexs:
                msg_chain.append('None')
            else:
                node = []
                for i in help_indexs:
                    with open(help_path+i,'r',encoding='utf-8') as help:
                        node.append(
                            ForwardNode(
                            senderId=2424947232,
                            time=datetime.datetime.now(),
                            senderName=i[:-4],
                            messageChain=MessageChain.fromPersistentString(help.read())),
                            )
                msg_chain = MessageChain.create(Forward(nodeList=node))
        if msg_chain:
            await app.sendGroupMessage(group,msg_chain)
    if member.id == admin:
        help_indexs = os.listdir(help_path)
        msg_chain = MessageChain.create()    
        if not state:                            
            if msg[0:9] == '#help add':
                if len(msg) <= 10:
                    msg_chain.append('坏坏')
                else:
                    state = ['add',msg[10:]]
                    msg_chain.append(f'请为{state[1]}指定帮助')
            elif msg[0:9] == '#help del':
                if msg[10:]+'.txt' not in help_indexs:
                    msg_chain.append(f'不存在{msg[10:]}!')
                else:
                    os.remove(help_path+msg[10:]+'.txt') #删除文件
                    msg_chain.append('删除成功!')
        else:
            if state[0] == 'add':
                with open(help_path+state[1]+'.txt','w',encoding='utf-8') as help:
                    help.write(message.asPersistentString())
                msg_chain.append('添加成功!')
            state = []
        if msg_chain:
            await app.sendGroupMessage(group,msg_chain)
                
