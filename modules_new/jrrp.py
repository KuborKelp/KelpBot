from graia.saya import Channel
from graia.ariadne.message.parser.twilight import RegexMatch, SpacePolicy, Twilight
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *

import random
import datetime
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.font_manager import FontProperties
from time import sleep


def status():
    path = './data/status/command'
    Module = 'jrrp'
    Command = ['#jrrp','#jrrp plot','#jrrp bar','#jrrp scatter','#jrrp barh','#jrrp test','#jrrp try']
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
rp_x = np.array([i for i in range(101)])
rp_table = 85**1.002**(-(rp_x-66)**2/4)+15  #计算公式
rp_total = rp_table.sum()
draw_mode = ['bar','plot','scatter','barh'] #四种支持的绘图方式


channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
        inline_dispatchers=[Twilight([RegexMatch(r'#jrrp(| plot| scatter| bar| test| try| barh)')])],
    ),
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay().split() #消息链预处理
    msg_chain=MessageChain.create() #创建一个空的消息链
    length = len(msg)
    if length == 1: # #jrrp
        msg_chain=MessageChain.create()
        now = datetime.datetime.now().strftime("%Y-%m-%d")  # 获取 年-月-日
        rp = rp_get(member.id,now)
        msg_chain.append(Plain(f'{member.name}的今日人品为{rp[0]+rp[1]}({rp[0]})'))
    elif length == 2:
        if msg[1] == 'test':
            msg_chain.append(Image(path=rp_test()))
        elif msg[1] == 'try':
            msg_chain.append(Image(path=rp_try()))
        elif msg[1] in draw_mode:
            msg_chain.append(Image(path=rp_draw(member.id,msg[1]))) 
    if msg_chain:
        sleep(0.2) #防止频繁操作导致风控
        await app.sendGroupMessage(group, msg_chain)


def rp_get(mid,now): # 随机获取一个人品
    path=f'./data/rp/{mid}/'
    if not os.path.exists(path): #检查数据所存放的文件夹
        os.makedirs(path)
    if not os.path.exists(path+now):
        global rp_table,rp_total
        count = 0
        i = 0
        k = random.uniform(0,rp_total)
        while count<k and i<=99:
            i+=1
            count += rp_table[i]
        with open(path+now,'w',encoding='utf-8') as f:
            rp = [i,0]
            f.write(f'{i};0')
    else:
        with open(path+now,'r',encoding='utf-8') as f: #读取已生成过的人品
            rp=f.read().split(';')
            rp=list(map(int,rp))
    return rp


def rp_test(): # 生成jrrp理论分布折线图
    global rp_x,rp_table
    path = './cache'
    if not os.path.exists(path): #文件路径检查
        os.makedirs(path)
    path += '/jrrp_test.png'
    plt.figure(figsize=(7,3),dpi=150)
    plt.plot(rp_x,rp_table,color='#3fef53',alpha=0.8,linewidth=8)
    plt.title('rp distribution')
    plt.savefig(path)
    return path

def rp_try(): # 随机生成10000个rp样本，并绘制图表
    path = './cache'
    if not os.path.exists(path):
        os.makedirs(path)
    path += '/jrrp_try.png'
    rp = []
    for i in range(10000):
        global rp_table,rp_total,rp_x
        count = 0
        i = -1
        k = random.uniform(0,rp_total)
        while count<=k and i<=99:
            i+=1
            count += rp_table[i]
        rp.append(i)
    tot = {i:0 for i in range(101)}
    for i in rp:
        tot[i]+=1
    plt.figure(figsize=(7,3),dpi=150)
    plt.plot(rp_x,tot.values(),color='#f34fe3',alpha=0.8,linewidth=8)
    plt.title('rp*10000')
    plt.savefig(path)
    return path


def rp_change(mid, time, delta): # rp增减函数
    path=f'./data/rp/{mid}/'
    rp = rp_get(mid, time)
    rp[1] += delta
    with open(path+time,'w',encoding='utf-8') as f:
        f.write(f'{rp[0]};{rp[1]}')



def rp_draw(mid,mode):
    rp_get(mid, now = datetime.datetime.now().strftime("%Y-%m-%d"))
    days = 10
    path = f'./data/rp/{mid}/'
    ipath = './cache/rp.png'
    x = os.listdir(path)[0:days]
    y = []
    for i in x:
        with open(path+i,'r',encoding = 'utf-8') as f:
            y.append(int(f.read().split(';')[0]))
    
    font = FontProperties(fname='./resources/HarmonyOS_Sans_SC_Medium.ttf', size=18)
    plt.figure(figsize=(4+len(x)*1.3,8), dpi=100)
    plt.title(f'{mid}近期的jrrp',fontproperties=font)

    if mode == 'plot':
        plt.plot(x,y,linewidth=12,color='#4e3f99')
    elif mode == 'scatter':
        s = [rp*8 for rp in y]
        plt.scatter(x,y,linewidth=5,c=y,s=s,cmap=get_colorbar(),marker=get_maker(),alpha=0.7)
        plt.colorbar()
    elif mode == 'bar':
        plt.bar(x,y,color='#3f524a')
    elif mode == 'barh':
        plt.barh(x,y,color='#4e278d')

    plt.savefig(ipath)
    return ipath


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
