'''
Kbot基础:
 #status
'''
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *
import os
import datetime
import psutil
import time


def status():
    path = './data/status/command'
    Module = 'status'
    Command = ['#status']
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.exists(f'./data/status/modules/'):
        os.makedirs(f'./data/status/modules/')
    for i in Command:
        if not os.path.exists(path+'/'+i):
            with open(path+'/'+i+'.txt','w') as txt:
                txt.write('0')
    with open(f'./data/status/modules/{Module}','w') as txt:
                txt.write('0')


status()
channel = Channel.current()
statu = [time.time(), 0]
module = []
command = []
times = []
Version = 'V3.7'
module_get = False

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    global module_get,command,times,statu,module,Version
    if not module_get:
        module_get = True
        module = os.listdir(f'./data/status/modules')
        filenames = os.listdir(f'./data/status/command')
        command = [i[0:-4] for i in filenames]
        times=[0]*len(command)
        for i in range(0,len(filenames)):
            with open(f'./data/status/command/{filenames[i]}','r') as txt:
                times[i] = len(txt.read())
    
    for i in command:
        if i in msg:
            with open(f'./data/status/command/{i}.txt','a') as txt:
                txt.write('0')
            times[command.index(i)] += 1
            break

    
    if msg == '#status':
        now = datetime.datetime.now()  # 获取时间
        now = now.strftime("%Y-%m-%d")  # 获取 年-月-日
        length = len(command)
        if length>3:
            for i in range(0,length):
                for j in range(i+1,length):
                    if times[i]<times[j]:
                        command[i],command[j] = command[j],command[i]
                        times[i],times[j] = times[j],times[i]
        lines = ['','','','','','','','','','']
        
        line = ''

        index = 0
        lines[index] = f'bot已运行{int(time.time() - statu[0])}s'

        index += 1
        lines[index] = f'bot版本{Version}'

        index += 1
        lines[index] = '插件:'
        for i in module[:-1]:
            lines[index] += i+','
        lines[index] += module[-1]

        index += 1
        lines[index] = '常用指令:'
        for i in command[0:min(len(command),7)]:
            lines[index] += f'{i}({times[command.index(i)]})'
        index += 1
        lines[index] = '已被调用次数'+str(sum(times))

        index += 1
        #psutil.cpu_count() # CPU逻辑数量
        cpu_core = psutil.cpu_count(logical=False)
        cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)
        lines[index] = f'cpu占用率:{cpu_percent},核心数{cpu_core}'
        
        index += 1
        mem = psutil.virtual_memory()
        mem = [int(mem.used/1024**2),int(mem.free/1024**2)]
        lines[index] = f'内存:{mem[1]}MB/{mem[0]}MB'
        
        for i in lines[:-1]:
            if i != '':
                line = line+i+'\n'
        line = line+lines[-1]
        await app.sendGroupMessage(group,MessageChain.create(Plain(line)))