import aiohttp
import asyncio
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger  # 使用官方logger记录日志[reference:2]
from bs4 import BeautifulSoup
from astrbot.api.event import MessageChain  # 导入MessageChain用于构建主动消息[reference:3]

@register("maimaidx_checker", "冷沫", "查看国服舞萌机台的更新信息", "1.0.0")
class MaimaiWatcher(Star):
    def __init__(self, context: Context, config: dict = None):
        super().__init__(context)
        self.last_content = ""

        # 在后台启动一个异步任务，用于执行定时监控，这是实现每小时检查的关键[reference:4][reference:5]
        asyncio.create_task(self.scheduled_fetch())
