from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
import os
import bilibili_api as b
from time import sleep

def status():
    path = './data/status/command'
    Module = 'bilibili'
    Command = ['#info']
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


def prepare(path):
    if not os.path.exists(path):
        os.makedirs(path)
        
status()
channel = Channel.current()


@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)


async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    if msg[0] == '#':
        msg_chain = MessageChain.create()
        length = len(msg)
        if msg[0:5] == '#info':
            if length == 5:
                msg_chain.append('正确的格式为#info {bv/av}')
            else:
                bv = msg[6:]
                info = b.video.get_video_info(bvid=bv)
                lines = f_info(info)
                msg_chain.append(Image(url=info['pic']))
                msg_chain.append(lines)
        if msg_chain:
            await app.sendGroupMessage(group,msg_chain)
            sleep(0.5)


def f_info(i):
    result = ''
    stat = i['stat']
    lines = []
    lines.append(f'''bv:{i['bvid']} av:{i['aid']}''')
    lines.append(f'''[视频链接]:https://www.bilibili.com/video/{i['bvid']}''')
    lines.append(f'''[UP]:{i['owner']['name']}''')
    lines.append(f'''[标题]:{i['title']}''')
    lines.append(f'''[简介]:{i['desc']}''')
    lines.append(f'''[分区]:{i['tname']}''')
    lines.append(f'''[播放量]:{stat['view']};[弹幕]:{stat['danmaku']}条;[评论]:{stat['reply']}''')
    lines.append(f'''[点赞]:{stat['like']};[收藏]:{stat['favorite']};[投币]:{stat['coin']};[转发]:{stat['share']}''')
    for line in lines[:-1]:
        result += line+'\n'
    result += lines[-1]
    return result