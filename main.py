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
    async def scheduled_fetch(self):
        """后台定时任务，每小时执行一次"""
        while True:
            # 等待1800秒（30mins）
            await asyncio.sleep(1800)
            await self.fetch_and_push()

    async def fetch_website(self) -> str:
        """抓取目标网站的核心内容，并进行格式化处理"""
        url = "https://wc.wahlap.net/maidx/location/"

        # 使用aiohttp异步请求库，高效地进行HTTP请求[reference:7]
        async with aiohttp.ClientSession() as session:
            # 添加User-Agent可以降低被一些网站拒绝的风险
            async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as resp:
                html = await resp.text()
                # 使用BeautifulSoup解析HTML[reference:8]
                soup = BeautifulSoup(html, 'html.parser')

        # --- 重点修改：你需要分析网页结构，替换下面的CSS选择器 ---
        # 比如，如果店铺列表在 <div class="store-list"> 里面的 <li> 标签中
        # 那么选择器就是 ".store-list li"
        items = soup.select('YOUR_CSS_SELECTOR')  # 待定：请根据实际页面结构修改

        # 如果你只是想监控整个页面是否有变化，可以使用下面的简单方法：
        # processed_content = str(soup)

        # 处理提取到的数据
        if items:
            content_lines = ["【当前机台列表】"]
            for item in items:
                # 注意：get_text(strip=True) 可以提取标签内的文本并去除首尾空白[reference:9]
                content_lines.append(f"- {item.get_text(strip=True)}")
            processed_content = "\n".join(content_lines)
        else:
            # 如果没提取到特定内容，也可以返回整个页面文本作为对比基准
            processed_content = f"抓取时间: {asyncio.get_event_loop().time()}\n内容摘要: {html[:500]}..."

        return processed_content

    async def fetch_and_push(self):
        """抓取内容并判断是否需要推送"""
        new_content = await self.fetch_website()
        logger.info("定时任务执行了一次抓取。") # 记录日志以便在控制台查看运行状态[reference:10]
        if new_content != self.last_content:
            # 注意：这里的 "你的会话唯一标识(UMO)" 需要你在步骤3.4获取后替换[reference:11]
            my_umo = "你的会话唯一标识(UMO)"
            # 构建消息链
            message_chain = MessageChain().message(f"【舞萌机台更新】\n{new_content}")
            # 主动发送消息[reference:12]
            await self.context.send_message(my_umo, message_chain)
            self.last_content = new_content

    @filter.command("maickeck")
    async def query(self, event: AstrMessageEvent):
        """用户主动查询指令，发送 /maicheck 即可触发"""
        # 这是关键：通过 event.unified_msg_origin 获取会话的唯一标识符（UMO）[reference:13]
        umo = event.unified_msg_origin
        # 这条日志会打印到AstrBot的控制台，你可以在那里看到并复制它
        logger.info(f"收到查询指令，来自会话: {umo}")

        latest = await self.fetch_website()
        yield event.plain_result(latest)
