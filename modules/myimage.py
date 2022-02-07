from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
import os
import time
from PIL import Image as Img
from math import *
from random import *
import requests


def status():
    path = './data/status/command'
    Module = 'MyImage'
    Command = ['#img info', '#rgb create']
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
lst = {}
Banned = ['eval', 'exit', 'import', 'from', 'setup', 'ping', 'builtins', 'rm', 'system', 'out', 'put', 'read', 'del',
          'delete', 'open']


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    msg_chain = MessageChain.create()
    if msg[0:4].lower() in ['#img', '#rgb', '#hsv']:
        msg = msg.lower()
        if msg == '#img info':
            lst.update({member.id: 'info'})
            msg_chain.append('请发送图片!')
        if msg[0:12] == '#rgb create ':  # rgb
            msg = msg.split('#rgb create')
            flag = True
            for i in msg[1:]:
                new_path = rgb_create(i, msg)
                if new_path:
                    if flag:
                        msg_chain.append('生成结果:')
                        flag = False
                    msg_chain.append(Image(path=new_path))
                else:
                    msg_chain.append('生成失败(T_T)')
        elif msg[0:12] == '#hsv create ':  # hsv
            msg = msg.split('#rgb create')
            flag = True
            for i in msg[1:]:
                new_path = hsv_create(i, msg)
                if new_path:
                    if flag:
                        msg_chain.append('生成结果:')
                        flag = False
                    msg_chain.append(Image(path=new_path))
                else:
                    msg_chain.append('生成失败(T_T)')
    elif member.id in lst:
        if lst[member.id] == 'info':
            if Image not in message:
                msg_chain.append('未发现图片!')
            else:
                img = message.getFirst(Image)
                img_path = download_image(img.url)
                # msg_chain.append(f'图片信息如下:\n')
                msg_chain.append(Image(path=img_path))
        del lst[member.id]
    if msg_chain:
        await app.sendGroupMessage(group, msg_chain)


def download_image(url):
    f = requests.get(url)
    path = './cache/'
    if not os.path.exists(path):
        os.makedirs(path)
    path = path + 'myimage.jpg'
    with open(path, 'wb') as img:
        img.write(f.content)
    return path


def rgb_create(expression, msg):
    SIZE = 256
    im = Img.new('RGB', (SIZE, SIZE))
    im.resize((SIZE, SIZE))
    pix = im.load()
    for i in Banned:
        if i in msg:
            return False
    else:
        for i in range(SIZE):
            for j in range(SIZE):
                r, g, b = eval(expression)
                r, g, b = int(r), int(g), int(b)
                pix[i, j] = (r, g, b)
        if not os.path.exists('./data/image/'):
            os.makedirs('./data/image')
        im.save('./data/image/create.png')
        return './data/image/create.png'


def hsv_create(expression, msg):
    SIZE = 360
    im = Img.new('RGB', (SIZE, SIZE))
    im.resize((SIZE, SIZE))
    pix = im.load()
    for i in Banned:
        if i in msg:
            return False
    else:
        for i in range(SIZE):
            for j in range(SIZE):
                h, s, v = eval(expression)
                r, g, b = hsv2rgb(h, s, v)
                pix[i, j] = (r, g, b)
        if not os.path.exists('./data/image/'):
            os.makedirs('./data/image')
        im.save('./data/image/create.png')
        return './data/image/create.png'


def hsv2rgb(h, s, v):
    h = float(h)
    s = float(s)
    v = float(v)
    h60 = h / 60.0
    h60f = floor(h60)
    hi = int(h60f) % 6
    f = h60 - h60f
    p = v * (1 - s)
    q = v * (1 - f * s)
    t = v * (1 - (1 - f) * s)
    r, g, b = 0, 0, 0
    if hi == 0:
        r, g, b = v, t, p
    elif hi == 1:
        r, g, b = q, v, p
    elif hi == 2:
        r, g, b = p, v, t
    elif hi == 3:
        r, g, b = p, q, v
    elif hi == 4:
        r, g, b = t, p, v
    elif hi == 5:
        r, g, b = v, p, q
    r, g, b = int(r * 255), int(g * 255), int(b * 255)
    return r, g, b
