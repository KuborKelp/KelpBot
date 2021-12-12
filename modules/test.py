from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import Plain, At, Image
from graia.ariadne.event.message import *

channel = Channel.current()

@channel.use(
    ListenerSchema(
        listening_events=[GroupMessage],
    )
)
async def main(app: Ariadne, message: MessageChain, member: Member, group: Group):
    msg = message.asDisplay()
    if msg == '#test':
        msg_chain = MessageChain.create()
        msg_chain.append(Plain('2'))
        msg_chain.append(At(2321247175))
        await app.sendMessage(group, msg_chain)