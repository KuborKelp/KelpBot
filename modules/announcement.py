from time import sleep
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
import os


def status():
    Path = './data/status/command'
    Module = 'announcement'
    Command = ['#announcememnt']
    if not os.path.exists(Path):
        os.makedirs(Path)
    if not os.path.exists(f'./data/status/modules/'):
        os.makedirs(f'./data/status/modules/')
    for i in Command:
        if not os.path.exists(Path + '/' + i + '.txt'):
            with open(Path + '/' + i + '.txt', 'w') as txt:
                txt.write('0')
    with open(f'./data/status/modules/{Module}', 'w') as txt:
        txt.write('0')


status()
admin = 2321247175
channel = Channel.current()
path = './data/grass/'
state = False


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    global state
    if member.id == admin:
        msg_chain = MessageChain.create()
        if msg[0:9] == '#announce' and not state:
            state = True
            msg_chain.append('请发送公告')
        elif state:
            msg_chain = MessageChain.create()
            msg_chain.append('发送完毕')
            groups = await app.getGroupList()
            announcement = message
            state = False
            announcement.append('\n————来自Kelpbot插播的一条公告')
            for g in groups:
                await app.sendGroupMessage(g, announcement)
                sleep(0.5)

        if msg_chain:
            await app.sendGroupMessage(group, msg_chain)
