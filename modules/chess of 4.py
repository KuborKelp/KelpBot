from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
from graia.ariadne.event.mirai import *
from PIL import Image as Img
from time import sleep
import os
import random


def status():
    path = './data/status/command'
    Module = 'chess of 4'
    Command = ['#chess start', '#chess join', '#chess stop']
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


slime = Img.open('./slime.png').convert('RGBA').resize((64, 64))
cream = Img.open('./cream.png').convert('RGBA').resize((64, 64))
smask = slime.split()[-1]
cmask = cream.split()[-1]


class Chess(object):
    def __init__(self, gid):
        super(Chess, self).__init__()
        self.img = Img.open('./map.png').convert('RGBA')
        self.gid = gid
        self.map = [[1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0], [2, 2, 2, 2]]
        self.pair = []
        self.name = []
        self.now = 0  # 0:slime 1:cream

    def draw(self):
        chess_map = Img.open('./map.png').convert('RGBA')
        for i in range(4):
            for j in range(4):
                chess = self.map[i][j]
                pos_now = (4 + 72 * j, 4 + 72 * i)
                if chess == 1:
                    chess_map.paste(slime, pos_now, smask)
                elif chess == 2:
                    chess_map.paste(cream, pos_now, cmask)
        chess_map.save(f'./data/chess/cache/{self.gid}.png')
        return f'./data/chess/cache/{self.gid}.png'

    def examine(self, x, y):
        x, y = y, x
        it = self.map[x][y]
        # 行
        line = ''
        for j in range(0, 4):
            line += str(self.map[x][j])
        if ('112' in line or '211' in line) and '0' in line and it == 1:
            for j in range(0, 4):
                if self.map[x][j] == 2:
                    self.map[x][j] = 0
                    break
        elif ('221' in line or '122' in line) and '0' in line and it == 2:
            for j in range(0, 4):
                if self.map[x][j] == 1:
                    self.map[x][j] = 0
                    break
        # 列
        line = ''
        for i in range(0, 4):
            line += str(self.map[i][y])
        if ('112' in line or '211' in line) and '0' in line and it == 1:
            for i in range(0, 4):
                if self.map[i][y] == 2:
                    self.map[i][y] = 0
                    break
        elif ('221' in line or '122' in line) and '0' in line and it == 2:
            for i in range(0, 4):
                if self.map[i][y] == 1:
                    self.map[i][y] = 0
                    break

    def if_win(self):
        cmap = str(self.map)
        num1 = cmap.count('1')
        num2 = cmap.count('2')
        if num1 == 1:
            return [True, 2]
        elif num2 == 1:
            return [True, 1]
        return [False, None]

    def move(self, x, y, xx, yy):
        self.map[yy][xx] = self.now + 1
        self.map[y][x] = 0
        self.now = 1 if self.now == 0 else 0

    def set_pair(self, p, n):
        self.pair = p
        self.name = n
        if random.randint(0, 1) == 1:
            self.pair = p[::-1]
            self.name = n[::-1]

    def get_pair(self):
        return self.pair

    def get_name(self):
        return self.name

    def get_map(self):
        return self.map

    def get_now(self):
        return self.now


status()
channel = Channel.current()
game = {}
pair = {}
name = {}
pos = [1, 2, 3, 4]
pos_m = [[0, -1], [0, 1], [-1, 0], [1, 0]]  # pos match
move = ['u', 'd', 'l', 'r']


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    msg_chain = MessageChain.create()
    if msg == '#chess start':
        if group.id in game:
            prepare()
            msg_chain.append('Chess游戏进行中!')
        else:
            pair.update({group.id: [member.id]})
            name.update({group.id: [member.name]})
            game.update({group.id: Chess(group.id)})
            msg_chain.append('请第二位玩家输入#chess join加入游戏!')
    elif msg == '#chess join':
        if group.id not in pair:
            msg_chain.append('chess不在配对环节中')
        else:
            p = pair[group.id]
            n = name[group.id]
            if member.id == p[0]:
                msg_chain.append('跟自己配对是什么重量级?')
            else:
                p.append(member.id)
                n.append(member.name)
                game[group.id].set_pair(p, n)
                p = game[group.id].get_pair()
                n = game[group.id].get_name()
                msg_chain.append(f'玩家配对完成:\n{n[0]}({p[0]})对应史莱姆球,{n[1]}({p[1]})对应岩浆膏,{p[0]}先操作\n以下为棋盘\n')
                msg_chain.append(Image(path=game[group.id].draw()))
                del p, pair[group.id]
    elif msg == '#chess stop':
        if group.id in game:
            p = game[group.id].get_pair().append(2321247175)
            msg_chain.append('Chess游戏已经销毁!')
            del game[group.id]
        else:
            msg_chain.append('本群没有进行中的Chess游戏!')
    elif group.id in game:
        p = game[group.id].get_pair()
        now = game[group.id].get_now()
        if member.id not in p or len(msg) != 3:
            return
        if int(msg[0]) in pos and int(msg[1]) in pos and msg[2] in move and member.id == p[now]:
            x, y = int(msg[0]) - 1, int(msg[1]) - 1
            delta = pos_m[move.index(msg[2])]
            xx = x + delta[0]
            yy = y + delta[1]
            cmap = game[group.id].get_map()
            block_1 = cmap[y][x]
            block_2 = cmap[yy][xx]
            if block_1 != now + 1 or block_2 != 0 or not (0 <= xx <= 3 and 0 <= yy <= 3):
                msg_chain.append('非法操作,请检查')
            else:
                n = game[group.id].get_name()
                game[group.id].move(x, y, xx, yy)
                game[group.id].examine(xx, yy)
                state = game[group.id].if_win()
                if state[0]:
                    winner = state[1] - 1
                    msg_chain.append(f'胜者为{n[winner]}')
                    msg_chain.append(Image(path=game[group.id].draw()))
                else:
                    msg_chain.append(Image(path=game[group.id].draw()))
                    msg_chain.append(f'现在轮到{n[game[group.id].get_now()]}操作')
    if msg_chain:
        sleep(0.2)
        await app.sendGroupMessage(group, msg_chain)
        sleep(0.3)


def prepare():
    path = './data/chess/cache/'
    if not os.path.exists(path):
        os.makedirs(path)
