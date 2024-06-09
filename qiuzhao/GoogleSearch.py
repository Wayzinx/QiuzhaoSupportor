import os
import requests
import json
from bot import bot_factory
from bridge.bridge import Bridge
from bridge.reply import Reply, ReplyType
from config import conf
from common.log import logger
import plugins
from plugins import Plugin, Event, EventContext, EventAction
from channel.chat_channel import check_contain, check_prefix
from channel.chat_message import ChatMessage
import random


@plugins.register(
    name="SearchCompany",
    desire_priority=1,
    hidden=False,
    desc="A plugin that fetches daily search",
    version="0.1",
    author="zixin",
)
class GoogleSearch(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context 

    def on_handle_context(self, e_context: EventContext):
        content = e_context["context"].content
        if content.startswith("查找 "):
            self.handle_text_search(e_context, content[len("查找 "):])
            
    def handle_text_search(self, e_context, query):
        cmsg : ChatMessage = e_context['context']['msg']
        session_id = cmsg.from_user_id
        url = "http://8.134.255.243:5000/index"
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers).json()
        # json1 = json.dumps(json.loads(response.text), indent=4, sort_keys=False, ensure_ascii=False)
        # print(response['msg'])
        msg = response['msg']
        # logger.info(response.text);
        # query += response.text + "\n----------------\n"
        logger.info(msg);
        query += msg + "\n----------------\n"
        prompt = "你是一位群聊机器人，你根据问题对返回的数据进行匹配。并输出匹配问题的答案，输出格式为公司名，时间，投递链接地址。如果公司名找不到说明不存在\n"
        btype = Bridge().btype['chat']
        bot = bot_factory.create_bot(Bridge().btype['chat'])
        session = bot.sessions.build_session(session_id, prompt)
        session.add_query(query)
        result = bot.reply_text(session)
        total_tokens, completion_tokens, reply_content = result['total_tokens'], result['completion_tokens'], result['content']
        logger.debug("[Summary] total_tokens: %d, completion_tokens: %d, reply_content: %s" % (total_tokens, completion_tokens, reply_content))
        reply = Reply()
        if completion_tokens == 0:
            reply = Reply(ReplyType.ERROR, "合并摘要失败，"+reply_content+"\n原始多段摘要如下：\n"+query)
        else:
            reply = Reply(ReplyType.TEXT,reply_content)     
        e_context['reply'] = reply
        e_context.action = EventAction.BREAK_PASS # 事件结束，并跳过处理context的默认逻辑


    def get_help_text(self, **kwargs):
        help_text = (
            "🥰输入 '查找 <您需要查找的公司>'，我会帮您查找\n"
        )
        return help_text
