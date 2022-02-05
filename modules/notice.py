from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
import datetime
import os

def status():
    path = './data/status/command'
    Module = 'notice'
    Command = ['#notice']
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
wait_lst = []
id_lst = []

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)


async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    lst = read_lst()
    if msg[0:7] == '#notice':
        msg = msg.replace('@','')
        msg = msg.replace(' ','')
        msg = [msg[0:7],msg[7:]]
        if not (len(msg)==2 and isint(msg[1])):
            print(msg)
            await app.sendMessage(group, MessageChain.create([Plain('格式错误')]))
        else:
            await app.sendMessage(group, MessageChain.create([Plain('请发送消息')]))
            wait_lst.append(member.id)
            id_lst.append(msg[1])
    elif member.id in wait_lst:
        index = wait_lst.index(member.id)
        lst.append(id_lst[index])
        notice_write(id_lst[index],member.id,message.asPersistentString()) #消息链持久化
        write_lst(lst)
        await app.sendMessage(group, MessageChain.create([Plain('将在下一次发送消息时提醒')]))
        del wait_lst[index]
        del id_lst[index]
    elif str(member.id) in lst:
        path = f'./data/notice/{member.id}/'
        files = os.listdir(path)
        for i in files:
            pos = i.find('_%_')
            name = i[:pos]
            time = i[pos+3:-4]
            info = f'{name}:{time}:'
            with open(path+i,'r') as txt:
                msg = txt.read()
            msg = MessageChain.fromPersistentString(msg) ##消息链反持久化
            msg = MessageChain.create(Plain(info)).extend(msg)
            os.remove(path+i)
            await app.sendMessage(group,msg)
        del lst[lst.index(str(member.id))]
        write_lst(lst)


def read_lst():
    '''
    1.所有文件目录检查
    '''
    if not os.path.exists('./data/notice'):
        os.makedirs('./data/notice')
    if not os.path.exists('./data/notice/list.txt'):
        with open('./data/notice/list.txt', 'w'):
            return []
    with open('./data/notice/list.txt', 'r') as txt:
        lst = txt.read().split('\n')
        return lst
    

def isint(string):#判断是否为整数
    try:
        int(string)
        return True
    except ValueError:
        return False
    
def write_lst(lst):
    with open('./data/notice/list.txt', 'w') as txt:
        for i in lst[0:-1]:
            txt.write(i+'\n')
        txt.write(lst[-1])

def notice_write(id,id_2,message):
    '''
    id:被发送者qq号
    name:提醒者昵称
    message:消息
    '''
    now = datetime.datetime.now()  # 获取时间
    now = now.strftime("%Y-%m-%d-%H-%M-%S")  # 获取 年-月-日-时-分-秒
    if not os.path.exists(f'./data/notice/{id}'):
        os.makedirs(f'./data/notice/{id}')
    path = f'./data/notice/{id}/{id_2}_%_{now}.txt'
    with open(path,'w') as txt:
        txt.write(message)