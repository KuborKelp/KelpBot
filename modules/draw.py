from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
import os
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import random

def status():
    path = './data/status/command'
    Module = 'draw'
    Command = ['#scatter','#plot','#bar','#talk']
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

example = '#scatter [A,B,C],[90,22,26],[26,88,70],color=[red,blue],s=[400,210],alpha=[0.6,0.4],title=sb'
status()

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    if msg[0] != '#':
        pass
    elif msg in ['#scatter','bar','plot']:
        await app.sendMessage(group, MessageChain.create(Plain('示例:'+example)))
    elif msg[0:8] == '#scatter':
            if not os.path.exists('./plot_figure'):
                os.makedirs('./plot_figure')
            path = sca((msg[9:]))
            image_send = path    
            await app.sendMessage(group, MessageChain.create([Image(path=image_send)]))
    elif msg[0:5] == '#talk':
            msg = msg.split(' ')
            draw_mode = 'scatter'
            if len(msg) == 2:
                if msg[1] in ['scatter', 'bar', 'plot']:
                    draw_mode = msg[1]
                else:
                    await app.sendMessage(group, MessageChain.create(Plain('不存在的绘图方式')))
            if os.path.exists(f'./individual/{member.id}'):
                path = talk(member.id, member.name, draw_mode)
                await app.sendMessage(group, MessageChain.create([Image(path=path)]))
            else:
                await app.sendMessage(group, MessageChain.create(Plain('无记录')))


def check(line):  # 中括号匹配检查
    lst = []
    for i in line:
        if i in ['[', ']']:
            lst.append(i)
        if len(lst) == 2:
            if not (lst == ['[', ']']):
                return False
            lst = []
    return True


def get_draw(lst):
    draw = []
    flag = True
    for i in lst:
        if flag and i[0] != '[':
            for j in range(1, len(draw)):
                draw[j] = list(map(int, draw[j]))
            return draw
        if i[0] == '[':
            draw.append([i[1:]])
            flag = False
        elif i[-1] == ']':
            draw[-1].append(i[0:-1])
            flag = True
        else:
            draw[-1].append(i)


def sca(msg):
    font = FontProperties(fname='HarmonyOS_Sans_SC_Medium.ttf', size=16)
    error = ''
    title = ''
    color = 'pink'
    s = 200
    alpha = 0.8
    legend = []

    draw = []
    if not check(msg):
        error += '[]匹配有误;'
    msg.replace('，', ',')
    msg_re = msg.split(',')
    draw = get_draw(msg_re)

    s1 = 0
    cs_error = False
    for i in range(0, len(msg)):
        if msg[i:i + 2] == '],' and msg[i + 2] != '[':
            s1 = i + 1
            break

    msg = msg[s1:] + ','
    h = 0
    t = 0
    f = False
    para = []  # 存储参数

    for i in range(1, len(msg)):
        if msg[i] == '[':
            f = True
        if msg[i] == ']':
            f = False
        if msg[i] == ',' and not f:
            t = i
            if msg[i - 1] == ']':
                t = t - 1
            para.append(msg[h + 1: t])
            h = i

    for i in para:
        if i[0:6] == 'color=':
            if i[6] == '[':
                color = i[7:].split(',')
            else:
                color = i[6:]
        elif i[0:2] == 's=':
            if i[2] == '[':
                s = i[3:].split(',')
                s = list(map(int, s))
            else:
                s = i[3:].split(',')
        elif i[0:6] == 'alpha=':
            if i[6] == '[':
                alpha = i[7:].split(',')
                alpha = list(map(float, alpha))
            else:
                alpha = i[6:]
        elif i[0:6] == 'title=':
            title = i[6:]
        elif i[0:7] == 'legend=':
            if i[7] == '[':
                legend = i[8:].split(',')
        else:
            cs_error = True
    if cs_error:
        error += '未知的参数;'
    plt.figure(figsize=(12, 8), dpi=80)

    if len(draw) <= 1:
        error += '??;'
    if title != '':
        plt.title(title,fontproperties=font)
    count = 0

    for i in draw[1:]:
        if type(color) == type([]):
            color_plt = color[count]
        else:
            color_plt = color
        if type(s) == type([]):
            s_plt = s[count]
        else:
            s_plt = s
        if type(alpha) == type([]):
            alpha_plt = alpha[count]
        else:
            alpha_plt = alpha

        if legend:  # legend不为 空列表
            legend_plt = legend[count]
        else:
            legend_plt = str(count)

        count += 1
        plt.scatter(draw[0], draw[count], color=color_plt, s=s_plt, alpha=alpha_plt, label=legend_plt)
    path = './plot_figure/scatter.png'
    plt.legend(loc='best')
    plt.savefig(path)
    return path


def plot(msg):
    font = FontProperties(fname='HarmonyOS_Sans_SC_Medium.ttf', size=16)
    error = ''
    title = ''
    color = 'pink'
    width = 8
    legend = []

    if not check(msg):
        error += '[]匹配有误;'
    msg.replace('，', ',')
    msg_re = msg.split(',')
    draw = get_draw(msg_re)

    s1 = 0
    cs_error = False
    for i in range(0, len(msg)):
        if msg[i:i + 2] == '],' and msg[i + 2] != '[':
            s1 = i + 1
            break

    msg = msg[s1:] + ','
    h = 0
    t = 0
    f = False
    para = []  # 存储参数

    for i in range(1, len(msg)):
        if msg[i] == '[':
            f = True
        if msg[i] == ']':
            f = False
        if msg[i] == ',' and not f:
            t = i
            if msg[i - 1] == ']':
                t = t - 1
            para.append(msg[h + 1: t])
            h = i

    for i in para:
        if i[0:6] == 'color=':
            if i[6] == '[':
                color = i[7:].split(',')
            else:
                color = i[6:]
        elif i[0:6] == 'width=':
            if i[6] == '[':
                width = i[7:].split(',')
                width = list(map(int, width))
            else:
                s = i[6:].split(',')
        # elif i[0:6] == 'alpha=':
        #  if i[6] == '[':
        #      alpha = i[7:].split(',')
        #      alpha = list(map(float, alpha))
        #   else:
        #      alpha = i[6:]
        elif i[0:6] == 'title=':
            title = i[6:]
        elif i[0:7] == 'legend=':
            if i[7] == '[':
                legend = i[8:].split(',')
        else:
            cs_error = True
    if cs_error:
        error += '未知的参数;'
    plt.figure(figsize=(12, 8), dpi=80)

    if len(draw) <= 1:
        error += '??;'
    if title != '':
        plt.title(title, fontproperties=font)
    count = 0

    for i in draw[1:]:
        if type(color) == type([]):
            color_plt = color[count]
        else:
            color_plt = color
        if type(width) == type([]):
            width_plt = width[count]
        else:
            width_plt = s

        if legend:  # legend不为 空列表
            legend_plt = legend[count]
        else:
            legend_plt = str(count)

        count += 1
        plt.plot(draw[0], draw[count], color=color_plt, linewidth=width_plt, label=legend_plt)
    path = './plot_figure/plot.png'
    plt.legend(loc='best')
    plt.savefig(path)
    return path


def talk_get(tid):
    filenames = os.listdir(f'./individual/{tid}')
    count = 0
    day = []
    total = []
    for i in filenames[-1::-1]:
        with open(f'./individual/{tid}/{i}') as txt:
            day.append(i[5:-4])
            total.append(len(txt.read()))
            count += 1
        if count > 7:
            break
    return [day[-1::-1], total[-1::-1]]


def talk(my_id, my_name=None, mode='scatter'):
    font = FontProperties(fname='HarmonyOS_Sans_SC_Medium.ttf', size=16)
    if not my_name:
        my_name = my_id
    title = f'{my_name}的近期发言次数'
    t_data = talk_get(my_id)
    day = t_data[0]
    total = t_data[1]

    plt.figure(figsize=(8, 6), dpi=120)
    plt.title(title,fontproperties=font)
    if mode == 'scatter':
        smax = max(total)
        area_s = []
        for i in total:
            area_s.append(int(i / smax * 500) + 60)
        cmap = get_colorbar()
        plt.scatter(x=day, y=total, c=total, cmap=cmap, alpha=0.5, s=area_s)
        plt.colorbar()
    elif mode == 'bar':
        plt.bar(day, total)
    elif mode == 'plot':
        plt.plot(day, total, 'bo-', color='orange', linewidth=10)

    plt.savefig(f'./individual/{my_id}.png')
    return f'./individual/{my_id}.png'


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