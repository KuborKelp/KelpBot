#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *

import random  # 随机数
import datetime
import os
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    if msg[0] == '#':
        msg = msg[1:].split(' ')
    if len(msg) == 1:
        '''
        #jrrp
        '''
        if msg[0] == 'jrrp':
            now = datetime.datetime.now()  # 获取时间
            now = now.strftime("%Y-%m-%d")  # 获取 年-月-日
            rp_lst = get(member.id, now)
            qq_name = str(member.name)
            reply = f'{qq_name}的今日人品为{rp_lst[0] + rp_lst[1]}({rp_lst[0]})'
            await app.sendMessage(group, MessageChain.create([Plain(reply)]))
    elif len(msg) == 2:
        if msg[0] == 'jrrp':
            if msg[1] in ['scatter', 'bar', 'plot']:
                        draw_mode = msg[1]
                        image_send = rp_draw(mid=member.id, mode=draw_mode)
                        await app.sendMessage(group, MessageChain.create([Image(path = image_send)]))


def info():
    pms = False
    pms_chage = True


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


def rp_get(mid, days):
    files = os.listdir(f'./rp/{mid}')
    count = 0
    day = []
    total = []
    for i in files[-1::-1]:
        with open(f'./rp/{mid}/{i}', encoding='utf-8') as txt:
            day.append(i[5:-4])
            total.append(int(txt.read().split(';')[0]))
            count += 1
        if count >= days:
            break
    return [day[-1::-1], total[-1::-1]]


def rp_draw(mid, mode, days=15):
    #font = FontProperties(fname='HarmonyOS_Sans_SC_Medium.ttf', size=16)
    title = f'{mid}的近期人品'
    rp_data = rp_get(mid, days)
    day = rp_data[0]
    total = rp_data[1]

    plt.figure(figsize=(16, 6), dpi=100)
    plt.title(title,)

    smax = max(total)
    area_s = []
    for i in total:
        area_s.append(int(i / smax * 500) + 60)
    if mode == 'scatter':
        plt.scatter(x=day, y=total, c=total, cmap=get_colorbar(),
                    alpha=0.5, s=area_s, marker=get_maker(), linewidths=5)
        plt.colorbar()

    if mode == 'plot':
        color = [random.uniform(0, 1) for i in range(0, 3)]
        plt.plot(day, total, c=(color[0], color[1], color[2]), linewidth=15)

    path = f'./rp/images/{mid}/scatter.png'
    if not os.path.exists(f'./rp/images/{mid}'):
        os.makedirs(f'./rp/images/{mid}')
    plt.savefig(path)
    return path


def get_colorbar():
    lst = ['Accent', 'Blues', 'BrBG', 'BuGn', 'BuPu', 'CMRmap', 'Dark2', 'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges',
           'Paired', 'Pastel1', 'Pastel2', 'PiYG', 'PuBu', 'PuBuGn', 'PuOr', 'PuRd', 'Purples', 'RdBu', 'RdGy', 'RdPu',
           'RdYlBu', 'RdYlGn', 'Reds', 'Set1', 'Set2', 'Set3', 'Spectral', 'Wistia', 'YlGn', 'YlGnBu', 'YlOrBr',
           'YlOrRd', 'afmhot', 'autumn', 'binary', 'bone', 'brg', 'bwr', 'cividis', 'cool', 'coolwarm', 'copper',
           'cubehelix', 'flag', 'gist_earth', 'gist_gray', 'gist_heat', 'gist_ncar', 'gist_stern', 'gist_yarg',
           'gnuplot', 'gnuplot2', 'gray', 'hot', 'hsv', 'inferno', 'jet', 'magma', 'nipy_spectral', 'ocean', 'pink',
           'plasma', 'prism', 'rainbow', 'seismic', 'spring', 'summer', 'tab10', 'tab20', 'tab20b', 'tab20c', 'terrain',
           'twilight', 'twilight_shifted', 'viridis', 'winter']
    return random.choice(lst)


def get_maker():
    maker = ['.', 'o', 'v', '^', '<', '>', '8', 's', 'p', '*', 'h', 'H', 'x', 'd']
    return random.choice(maker)