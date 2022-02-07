from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
from random import choice, randint
import os
import shutil
import time
import datetime


def status():
    path = './data/status/command'
    Module = 'current_bottle'
    Command = ['#cb get', '#cb throw', '#cb info', '#cb throw_waste', '#cb clean_waste', '#cb rethrow']
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


def prepare(path):
    leaves = ['old', 'available']
    for i in leaves:
        if not os.path.exists(path + i):
            os.makedirs(path + i)


status()
path = './data/currentbottle/'
send_wait = []
rethrow = {}
prepare(path)

channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    global send_wait, rethrow
    if msg[0:3] == '#cb':
        msg_chain = MessageChain.create()
        msg = msg.split()
        length = len(msg)
        if length == 1:
            msg_chain.append(
                '#cb throw -> 投出一个漂流瓶\n#cb get ->获取一个漂流瓶\n#cb info ->获取漂流瓶状态 \n#cb throw_waste ->消耗人品丢垃圾 \n#cb '
                'clean_waste ->清理垃圾并获得人品\n#cb rethrow ->重新抛出上一个获取到的漂流瓶')
        elif length == 2:
            if msg[1] == 'throw':
                send_wait.append(member.id)
                msg_chain.append('请发送漂流瓶内容=￣ω￣=')
            elif msg[1] == 'get':
                cb_list = get_cb()
                if cb_list:
                    n = len(cb_list)
                    if randint(0, int(100 * n / (n + 100))) <= min(20, n):
                        msg_chain.append('😅😅😅很遗憾,海里连垃圾都没捞到😅😅😅')
                    else:
                        cb = choice(cb_list)
                        with open(r'./data/currentbottle/available/' + cb, 'r', encoding='utf-8') as bottle:
                            msg_chain = MessageChain.fromPersistentString(bottle.read())
                        remove_cb(cb)
                        if member.id in rethrow:
                            rethrow[member.id] == cb
                        else:
                            rethrow.update({member.id: cb})
                        cb = cb[:-4].split('&')
                        if cb[0][0] == '$':
                            msg_chain.append(f'\n来自{cb[0][1:]}在{cb[1]}投放的垃圾')
                        else:
                            msg_chain.append(f'\n来自{cb[0]}在{cb[1]}投出的的一只漂流瓶')
                else:
                    msg_chain.append('当前没有可拾取的漂流瓶,快扔一个给大伙看看😁')
            elif msg[1] == 'info':
                info = get_info()
                msg_chain.append(f'可获取的漂流瓶{info[0]}只\n已被拾取过的漂流瓶{info[1]}只')
            elif msg[1] == 'throw_waste':
                waste = choice(['鞋子', '骨头', '腐肉', '帽子', 'yys'])
                now = datetime.datetime.now().strftime("%Y-%m-%d")  # 获取时间;获取 年-月-日
                rp_lst = get_rp(member.id, now)  # 输入qq号，返回rp值  # 输入qq号，返回rp值
                rp_member_final = rp_lst[0] + rp_lst[1] - 2
                if rp_member_final >= 0:
                    change_rp(member.id, now, -2)
                    msg_chain.append(f'成功消耗2点人品投放垃圾:{waste}!')
                else:
                    msg_chain.append('人品不足!')
                throw_waste(waste, get_time(), member.id)
            elif msg[1] == 'clean_waste':
                waste_num = get_waste()
                if waste_num <= 0:
                    msg_chain.append('很干净!没有一点垃圾!')
                else:
                    now = datetime.datetime.now().strftime("%Y-%m-%d")  # 获取时间;获取 年-月-日
                    change_rp(member.id, now, 1)
                    msg_chain.append('成功清理一个垃圾并获得1点人品!')
                    clean_waste(1)
            elif msg[1] == 'rethrow':
                if member.id not in rethrow:
                    msg_chain.append('没有可以扔回去的漂流瓶!😫')
                else:
                    rethrow_cb(rethrow[member.id])
                    msg_chain.append('漂流瓶已经被扔回大海了!😊')
                    del rethrow[member.id]
        if msg_chain:
            await app.sendGroupMessage(group, msg_chain)
            time.sleep(0.1)
    elif member.id in send_wait:
        msg_chain = MessageChain.create()
        del send_wait[send_wait.index(member.id)]
        send_cb(message.asPersistentString(), get_time(), member.id)
        msg_chain.append('您的漂流瓶正在等待有缘人拾取!\^o^/')
        await app.sendGroupMessage(group, msg_chain)


def get_time():
    return time.strftime("%Y-%m-%d %X", time.localtime()).replace(':', '-')


def send_cb(msg, time, member_id):
    path = './data/currentbottle/available'
    with open(f'./data/currentbottle/available/{member_id}&{time}.txt', 'w+', encoding='utf-8') as bottle:
        bottle.write(msg)


def get_cb():
    path = './data/currentbottle/available/'
    return os.listdir(path)


def remove_cb(cb):
    old_path = './data/currentbottle/available/'
    new_path = './data/currentbottle/old'
    shutil.move(old_path + cb, new_path)


def rethrow_cb(cb):
    new_path = './data/currentbottle/available/'
    old_path = './data/currentbottle/old/'
    shutil.move(old_path + cb, new_path)


def get_info():
    old_path = './data/currentbottle/available/'
    new_path = './data/currentbottle/old/'
    return [len(os.listdir(old_path)), len(os.listdir(new_path))]


def throw_waste(waste, time, member_id):
    path = './data/currentbottle/available'
    with open(f'./data/currentbottle/available/${member_id}&{time}.txt', 'w+', encoding='utf-8') as bottle:
        bottle.write(waste)


def get_waste():
    path = './data/currentbottle/available'
    waste = 0
    for i in os.listdir(path):
        if i[0] == '$':
            waste += 1
    return waste


def clean_waste(num):
    path = './data/currentbottle/available'
    for i in os.listdir(path):
        if i[0] == '$':
            os.remove(path + '/' + i)
            return


def get_rp(mid, day):
    path = f'./rp/{mid}/{day}.txt'
    if not os.path.exists(f'./rp/{mid}'):
        os.makedirs(f'./rp/{mid}')
    if os.path.exists(path):
        with open(path, encoding='utf-8') as rp_txt:
            line = rp_txt.readline().split(';')
            rp = list(map(int, line))
    else:
        with open(path, 'w+', encoding='utf-8') as rp_txt:
            rp = [randint(0, 100), 0]
            rp_txt.write(f'{rp[0]};{rp[1]}')
    return rp


def change_rp(mid, day, value):
    path = f'./rp/{mid}/{day}.txt'
    rp = get_rp(mid, day)

    rp[1] = rp[1] + value
    with open(path, 'w+', encoding='utf-8') as rp_txt:
        rp_txt.write(f'{rp[0]};{rp[1]}')
