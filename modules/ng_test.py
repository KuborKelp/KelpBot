from typing import get_origin
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
import random

channel = Channel.current()

class Ng(object):
    def __init__(self,gid):
        super(Ng,self).__init__()
        self.status = False
        self.length = 0
        self.players = []
        self.out = []
    def if_in(self,pid):
        if pid in self.players:
            return True
        else:
            return False
    def join(self,pid):
        self.players.append(pid)
        self.length += 1
    def leave(self,pid):
        del self.players[self.players.index(pid)]
        self.length -= 1
    def start(self):
        self.status = True
        if self.length >=0:
            self.dic = {i:'' for i in self.players}
            step = random.randint(1,len(self.players))
            r_players = self.players[step:]+self.players[:step]
            self.reflection = {self.players[i]:r_players[i] for i in range(0,len(self.players))}
            return True
        else:
            return False
    def get_status(self):
        return self.status
    def set_dic(self,setter_id,word):
        self.dic[self.reflection[setter_id]] = word
    def check_dic(self):
        flag = True
        unset = []
        for i in self.reflection:
            if self.dic[i] == '':
                flag = False
                unset.append([i,self.reflection[i]])
        if flag:
            return [True]
        else:
            return [False,unset]
    def check_status(self):
        if self.length == 1:
            return [self.players,self.out]
        else:
            return [False]
    def if_out(self,pid,msg):
        if self.dic[pid] in msg:
            self.out.append(pid)
            self.length -= 1
            del self.players[self.players.index(pid)]
            return True
        else:
            return False
    def get_length(self):
        return self.length
    def get_reflection(self):
        return self.reflection
    def get_all_players(self):
        players = self.players
        players.extend(self.out)
        return players
    def get_winner(self):
        return self.players[0]

game = {}

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    if msg[0:3] == '#ng':
        msg = msg.split(' ')
        if len(msg)<=1:
            await app.sendGroupMessage(group,MessageChain.create([Plain('发送#ng help 获取帮助')]))
        elif msg[1] == 'start':
            if group.id not in game:
                game[group.id] = Ng(group.id)
                await app.sendGroupMessage(group,MessageChain.create([Plain('游戏已建立，发送#ng help 获取帮助')]))
            elif game[group.id].get_length()<=0:
                await app.sendGroupMessage(group,MessageChain.create([Plain('玩家数量不足，至少需要3位玩家')]))
            else:
                game[group.id].start()
                await app.sendGroupMessage(group,MessageChain.create([Plain('游戏已开始，请注意私聊窗口')]))
                reflection = game[group.id].get_reflection()
                for i in reflection:
                    await app.sendFriendMessage(i,MessageChain.create([Plain(f'请为{reflection[i]}指定ng词')]))
        elif msg[1] == 'help':
            await app.sendGroupMessage(group,MessageChain.create([Plain('ng词游戏帮助\n#ng join 加入游戏\n#ng start 创建/开始 游戏')]))
        elif group.id not in game:
            await app.sendGroupMessage(group,MessageChain.create([Plain('尚未创建游戏，请输入#ng start 创建游戏')]))
        else:
            if msg[1] == 'join':
                if game[group.id].if_in(member.id):
                    await app.sendGroupMessage(group,MessageChain.create([Plain('已加入游戏')]))
                else:
                    if game[group.id].get_status == True:
                        await app.sendGroupMessage(group,MessageChain.create([Plain('游戏已开始，不可加入')]))
                    else:
                        game[group.id].join(member.id)
                        await app.sendGroupMessage(group,MessageChain.create([Plain('加入成功')]))
            if msg[1] == 'leave':
                if game[group.id].if_in(member.id):
                    await app.sendGroupMessage(group,MessageChain.create([Plain('退出成功')]))
                    game[group.id].leave(member.id)
                else:
                    await app.sendGroupMessage(group,MessageChain.create([Plain('不在队伍中')]))
            if msg[1] == 'status':
                length = game[group.id].get_length()
                if group.id not in game:
                    await app.sendGroupMessage(group,MessageChain.create([Plain('未创建游戏')]))
                elif game[group.id].get_status():
                    await app.sendGroupMessage(group,MessageChain.create([Plain(f'游戏进行中,剩余人数:{length}')]))
                else:
                    await app.sendGroupMessage(group,MessageChain.create([Plain(f'游戏未开始,准备中人数:{length}')]))
            if msg[1] == 'stop':
                if member.id in game[group.id].get_all_players() or member.id == 2321247175:
                    del game[group.id]
                    await app.sendGroupMessage(group,MessageChain.create([Plain('游戏已销毁')]))
    if group.id in game and game[group.id].get_status() and game[group.id].check_dic()[0]:
        if game[group.id].if_in(member.id):
            if game[group.id].if_out(member.id, msg):
                await app.sendGroupMessage(group,MessageChain.create([Plain(f'{member.id}已淘汰')]))
                if game[group.id].get_length() == 0:
                    winner = game[group.id].get_winner()
                    await app.sendGroupMessage(group,MessageChain.create([Plain(f'{winner}获得本局游戏胜利')]))
                    del game[group.id]
@channel.use(
    ListenerSchema(
        listening_events=[FriendMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, friend:Friend):
    print(1)
    for i in game:
        check = game[i].check_dic()
        print(check)
        if not check[0]:
            print(2)
            for j in check[1]:
                if friend.id == j[1]:
                    msg = message.asDisplay()
                if len(msg) <=1:
                    await app.sendFriendMessage(friend,MessageChain.create([Plain('长度必须大于 1')]))
                else:
                    game[i].set_dic(friend.id,msg)
                    await app.sendFriendMessage(friend,MessageChain.create([Plain('设置成功')]))
                    if len(game[i].check_dic()) == 1:
                        await app.sendGroupMessage(i,MessageChain.create([Plain('ng词已指定完毕，游戏开始')]))
                    else:
                        unset = ' '
                        for k in game[i].check_dic()[1:]:
                            unset += k[0]+' '
                        await app.sendGroupMessage(i,MessageChain.create([Plain('还有如下玩家未指定ng词')]))
            