from graia.ariadne.app import Ariadne
from graia.ariadne.model import MiraiSession
from graia.saya import Saya
from graia.saya.builtins.broadcast import BroadcastBehaviour
import os


if __name__ == '__main__':

    app = Ariadne(
        MiraiSession(
            host="http://localhost:8080",  # 填入 HTTP API 服务运行的地址
            verify_key="1145abgg",  # 填入 verifyKey
            account=2424947232,  # 你的机器人的 qq 号
        )
    )

    saya = Saya(app.broadcast)
    saya.install_behaviours(BroadcastBehaviour(app.broadcast))

    async def main() -> None:
        await app.launch()
        await app.lifecycle()

    with saya.module_context():
        path = './modules/'
        files = os.listdir(path)
        for i in files:
            if i[-3:] == '.py' and 'test' not in i:
                saya.require(f"modules.{i[:-3]}")    
    try:
        app.loop.run_until_complete(main())
    except KeyboardInterrupt:
        app.loop.run_until_complete(app.stop())
        exit()