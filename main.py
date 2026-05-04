import aiohttp
from bs4 import BeautifulSoup
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("astrbot_plugin_maicheck", "你的名字", "查询舞萌机房信息的插件", "1.0.0")
class MaicheckPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.command("maicheck")
    async def maicheck(self, event: AstrMessageEvent):
        '''查询舞萌机房的最新信息'''
        yield event.plain_result("正在查询，请稍后...")
        try:
            url = "https://wc.wahlap.net/maidx/location/"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as resp:
                    html = await resp.text()

            # --- 数据解析部分 (你需要根据网页结构调整) ---
            soup = BeautifulSoup(html, 'html.parser')
            # 示例: 查找带有特定class的div
            items = soup.select('div.location-item')  # 你需要确认这个选择器是否正确
            if items:
                result_lines = ["【当前机房信息】"]
                for item in items[:10]:  # 限制返回条数，避免消息过长
                    result_lines.append(f"- {item.get_text(strip=True)}")
                result = "\n".join(result_lines)
            else:
                # 如果找不到特定元素，可以返回页面标题等通用信息作为备选
                page_title = soup.title.string if soup.title else "舞萌机房信息"
                result = f"当前获取到网页信息: {page_title}"
            # --------------------------------
            yield event.plain_result(result)
        except Exception as e:
            logger.error(f"抓取网站时发生错误：{e}")
            yield event.plain_result(f"获取信息失败，请稍后重试。错误: {str(e)}")
