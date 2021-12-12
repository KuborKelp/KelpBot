'''
Kbot基础:
 #status
'''
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
import os
import datetime
import time

channel = Channel.current()
status = [time.time(), 0]

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    now = datetime.datetime.now()  # 获取时间
    now = now.strftime("%Y-%m-%d")  # 获取 年-月-日
    if not os.path.exists(f'./groupwords/{group.id}'):
        os.makedirs(f'./groupwords/{group.id}')
    with open(f'./groupwords/{group.id}/{now}.txt', 'a', encoding='utf-8') as gw:
        gw.write(msg.replace('[图片]', '') + '\n')
    if not os.path.exists(f'./individual/{member.id}'):
        os.makedirs(f'./individual/{member.id}')
    with open(f'./individual/{member.id}/{now}.txt', 'a', encoding='utf-8') as sp:
        sp.write('1')
    
    if msg == '#status':
        reply = f'bot已运行{int(time.time() - status[0])}s\nVersion 3.1'
        await app.sendGroupMessage(group,MessageChain.create(Plain(reply)))