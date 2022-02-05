from sys import path
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, Image
from graia.ariadne.event.message import *
import jieba
import random
import numpy as np
import imageio
#import matplotlib.pyplot as plt
from PIL import Image as img
from wordcloud import WordCloud
import os


def status():
    path = './data/status/command'
    Module = 'wordcloud'
    Command = ['#wordcloud','#sw']
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
    if not msg[0:10] == '#wordcloud':
        pass
    elif msg == '#wordcloud':
        await app.sendGroupMessage(group,MessageChain.create(Plain('正在生成云图中...')))
        image_path = wd_group(group.id)
        await app.sendGroupMessage(group,MessageChain.create(Image(path=image_path)))
    elif msg == '#wordcloud mask':
        await app.sendGroupMessage(group,MessageChain.create(Image(path='./data/wordcloud/mask2.png')))
    if member.id == 2321247175:
        if msg[0:7] == '#sw add':
            await app.sendGroupMessage(group,MessageChain.create(Plain(sw_add(msg[8:]))))
        elif msg[0:7] == '#sw del':
            await app.sendGroupMessage(group,MessageChain.create(Plain(sw_del(msg[8:]))))
def sw_read():
    path = './data/wordcloud/sw.txt'
    if not os.path.exists(path):
        txt = open(path, 'w', encoding='utf-8')
        txt.close()
    with open(path, 'r',encoding='utf-8') as txt:
        return txt.read()[:-1].split(';')


def sw_add(word):
    path = './data/wordcloud/sw.txt'
    sw_lst = sw_read()
    if word in sw_lst:
        return '已存在'
    else:
        with open(path, 'a',encoding='utf-8') as txt:
            txt.write(word + ';')
        return '添加成功!'


def sw_del(word):
    path = './data/wordcloud/sw.txt'
    sw_lst = sw_read()
    if word in sw_lst:
        sw_lst.remove(word)
        with open(path, 'w',encoding='utf-8') as txt:
            for i in sw_lst[:-1]:
                txt.write(i + ';')
            txt.write(sw_lst[-1])
        return '删除成功!'

    else:
        return '不存在'


def wd_group(group_id):
    mytext = ''
    filenames = os.listdir(f'./groupwords/{group_id}')
    count = 0
    sw = sw_read()

    for i in filenames[-1::-1]:
        with open(f'./groupwords/{group_id}/{i}', encoding='utf-8', errors='ignore') as txt:
            text = txt.read()
            for j in sw:
                if j in text:
                    text = text.replace(j, '')
            mytext += text
            count += 1
        if count > 7:
            break
        
    mask_path = './data/wordcloud/mask/'+random.choice(os.listdir('./data/wordcloud/mask'))
  
    #mask1 = np.array(img.open(mask_path))
    mask1 = imageio.imread(mask_path)
    mask2 = img.open(mask_path)
    size = [mask2.width,mask2.height]
    mytext = ' '.join(jieba.cut(mytext, cut_all=False))
    
    to_path = './data/wordcloud/stylecloud.png'
    wc = WordCloud(
        mask=mask1,
        background_color='White',  # 背景色
        width=size[0],  # 宽度
        height=size[1],  # 高度
        max_words=150,
        colormap=get_cmap(),
        font_path='HarmonyOS_Sans_SC_Medium.ttf',
        #max_font_size=40,
        #min_font_size=15,
        margin=1,  # 词语边缘距离
        scale=4,  # 清晰度
        collocations=False
    )
    wc = wc.generate(mytext)  # 绘制词云
    wc.to_file(to_path)
    return to_path


def get_cmap():
    lst = ['Accent', 'Blues', 'BrBG', 'BuGn', 'BuPu', 'CMRmap', 'Dark2', 'GnBu', 'Greens', 'Greys', 'OrRd', 'Oranges',
           'Paired', 'Pastel1', 'Pastel2', 'PiYG', 'PuBu', 'PuBuGn', 'PuOr', 'PuRd', 'Purples', 'RdBu', 'RdGy', 'RdPu',
           'RdYlBu', 'RdYlGn', 'Reds', 'Set1', 'Set2', 'Set3', 'Spectral', 'Wistia', 'YlGn', 'YlGnBu', 'YlOrBr',
           'YlOrRd', 'afmhot', 'autumn', 'binary', 'bone', 'brg', 'bwr', 'cividis', 'cool', 'coolwarm', 'copper',
           'cubehelix', 'flag', 'gist_earth', 'gist_gray', 'gist_heat', 'gist_ncar', 'gist_stern', 'gist_yarg',
           'gnuplot', 'gnuplot2', 'gray', 'hot', 'hsv', 'inferno', 'jet', 'magma', 'nipy_spectral', 'ocean', 'pink',
           'plasma', 'prism', 'rainbow', 'seismic', 'spring', 'summer', 'tab10', 'tab20', 'tab20b', 'tab20c', 'terrain',
           'twilight', 'twilight_shifted', 'viridis', 'winter']
    return random.choice(lst)