from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
from PIL import Image as Img
from PIL import ImageFont, ImageDraw
from random import choice
from time import sleep
import json
import os


def status():
    path = './data/status/command'
    Module = 'wordle'
    Command = ['#wordle start', '#wordle stop']
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
game = {}
with open('vocabulary.json', 'r', encoding='utf-8') as js:
    dic = list(json.loads(js.read()).keys())
with open('16k.json', 'r', encoding='utf-8') as js:
    words = json.loads(js.read())

class Wordle(object):
    def __init__(self, gid):
        super(Wordle, self).__init__()
        self.img = Img.new('RGB', (250 + 20, 300 + 20), color='White')
        self.pix = self.img.load()
        self.round = 1
        self.word = choice(dic).upper()
        self.gid = gid
        self.path = f'./data/wordle_cache/{gid}.png'
        for i in range(5):  # 列
            for j in range(6):  # 行
                x1 = 10 + i * 50 + 5
                y1 = 10 + j * 50 + 5
                x2 = x1 + 40
                y2 = y1 + 40
                for x in range(x1, x2 + 1):
                    self.pix[x, y1] = (128, 128, 128)
                    self.pix[x, y2] = (128, 128, 128)
                for y in range(y1, y2):
                    self.pix[x1, y] = (128, 128, 128)
                    self.pix[x2, y] = (128, 128, 128)

    def green(self, x, y):
        color = Img.new('RGB', (39, 39), color='Green')
        self.img.paste(color, (11 + x * 50 + 5, 11 + y * 50 + 5))

    def yellow(self, x, y):
        color = Img.new('RGB', (39, 39), color=(209, 198, 103))
        self.img.paste(color, (11 + x * 50 + 5, 11 + y * 50 + 5))

    def grey(self, x, y):
        color = Img.new('RGB', (39, 39), color=(128, 128, 128))
        self.img.paste(color, (11 + x * 50 + 5, 11 + y * 50 + 5))

    def write(self, letter, x, y):
        x = 11 + x * 50 + 12
        y = 11 + y * 50 + 10
        ttf_path = 'HarmonyOS_Sans_SC_Medium.ttf'
        ttf = ImageFont.truetype(ttf_path, 25, encoding='utf-8')
        img_draw = ImageDraw.Draw(self.img)
        img_draw.text((x, y), letter, fill=(255, 255, 255), font=ttf, align='right')

    def get_round(self):
        return self.round

    def get_word(self):
        return self.word

    def next(self, target):
        for i in range(5):
            letter = target[i]
            y = self.round - 1
            x = i
            if letter == self.word[i]:
                self.green(x, y)
            elif letter in self.word:
                self.yellow(x, y)
            else:
                self.grey(x, y)
            self.write(target[i], x, y)
        self.round += 1
        self.img.save(self.path)
        return self.path


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    msg_chain = MessageChain.create()
    if msg == '#wordle start':
        if not os.path.exists('./data/wordle_cache'):
            os.makedirs('./data/wordle_cache')
        if group.id in game:
            msg_chain.append('Wordle游戏已经开始!')
        else:
            game.update({group.id: Wordle(group.id)})
            msg_chain.append('Wordle游戏即将开始!请按照格式进行猜词，例:\n?maybe')
    elif msg == '#wordle stop':
        if group.id in game:
            msg_chain.append('Wordle游戏已经销毁!')
            del game[group.id]
        else:
            msg_chain.append('本群没有进行中的Wordle游戏!')
    elif msg[0] in ['?', '？'] and len(msg) == 6:
        if group.id in game:
            round = game[group.id].get_round()
            word = game[group.id].get_word()
            target = msg[1:6].upper()
            if target.lower() not in words:
                msg_chain.append('所猜的词不在词库中')
            elif round == 6:
                if target == word:
                    msg_chain.append('猜对了!游戏结束\n')
                    path = game[group.id].next(target=target)
                    msg_chain.append(Image(path=path))
                    del game[group.id]
                else:
                    msg_chain.append('猜的不对,游戏结束\n')
                    path = game[group.id].next(target=target)
                    msg_chain.append(Image(path=path))
                    msg_chain.append(f'正确的单词为{word}')
                    del game[group.id]
            else:
                if target == word:
                    msg_chain.append('猜对了!游戏结束\n')
                    path = game[group.id].next(target=target)
                    msg_chain.append(Image(path=path))
                    del game[group.id]
                else:
                    msg_chain.append('猜的不对')
                    path = game[group.id].next(target=target)
                    msg_chain.append(Image(path=path))
    if msg_chain:
        sleep(0.1)
        await app.sendGroupMessage(group, msg_chain)
        sleep(0.1)

