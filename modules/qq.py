from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
import os
import requests
from random import sample
from PIL import Image as Img


def status():
    path = './data/status/command'
    Module = 'qq'
    Command = ['#avatar']
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(f'./data/status/modules/'):
        os.makedirs(f'./data/status/modules/')
    for i in Command:
        if not os.path.exists(path + '/' + i + '.txt'):
            with open(path + '/' + i + '.txt', 'w') as txt:
                txt.write('0')
    with open(f'./data/status/modules/{Module}', 'w') as txt:
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
    if msg == '#avatar all':
        member_lst = await app.getMemberList(group)
        num = len(member_lst)
        size = 7
        while size*size > num:
            size -= 1
        member_lst = sample(member_lst, size**2)

        im = Img.new('RGB', (size*100, size*100))
        msg_chain = MessageChain.create(f'你群共有{num}个人，正在使用{size**2}个人的头像生成图像中.......')
        await app.sendGroupMessage(group, msg_chain)
        for i in range(len(member_lst)):
            mid = member_lst[i].id
            path = download_image(f'http://q2.qlogo.cn/headimg_dl?dst_uin={mid}&spec=100')
            avatar = Img.open(path)
            x = i % size * 100
            y = i // size * 100
            im.paste(avatar, (x, y))
        avatar_path = './cache/avatar_all.png'
        im.save(avatar_path)
        msg_chain = MessageChain.create(Image(path=avatar_path))
        await app.sendGroupMessage(group, msg_chain)
    elif msg[0:7] == '#avatar':
        msg = msg[8:].replace('@', '')
        msg_chain = MessageChain.create()
        msg_chain.append(Image(url=f'https://q1.qlogo.cn/g?b=qq&nk={msg}&s=640'))
        if msg_chain:
            await app.sendGroupMessage(group, msg_chain)


def download_image(url):
    f = requests.get(url)
    path = './cache/'
    if not os.path.exists(path):
        os.makedirs(path)
    path = path + 'qq_avatar.jpg'
    with open(path, 'wb') as img:
        img.write(f.content)
    return path
