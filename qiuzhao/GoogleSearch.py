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
import re
from datetime import datetime

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
        if content.startswith("查找 帮助"):
            reply = Reply(ReplyType.TEXT,self.get_help_text())     
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS 
            return ""
        if content.startswith("查找今日开启"):
            self.search_today_message(e_context)
        if content.startswith("查找 "):
            # self.handle_text_search(e_context, content[len("查找 "):])
            content_parts = content[len("查找 "):].split()
            self.handle_text_search(e_context, content, content_parts)
        if content.startswith("秋招 "):
            match = re.search(r'\d+', content[len("秋招 "):])
            if match:
                time_num = int(match.group())
            else:
                reply = Reply(ReplyType.TEXT,"找不到数字😭,输入(查找 帮助)查看格式😅")     
                e_context['reply'] = reply
                e_context.action = EventAction.BREAK_PASS 
                return ""
            self.recently_message(e_context,time_num)

            
    def handle_text_search(self, e_context, query, parts):
        cmsg : ChatMessage = e_context['context']['msg']
        session_id = cmsg.from_user_id
        data = {}

        job_types = ["2025届实习/暑期实习", "2025届校招/秋招"]
        fact_types = [
                    "石油", "钢铁", "电力", "能源", "煤矿", "新能源", "烟草",
                    "制造业", "汽车", "电子", "电器", "机械", "芯片", "半导体",
                    "国家机关", "高校", "研究所", "事业单位", "教育",
                    "互联网", "IT软件", "游戏", "物联网", "通信", "AI智能", "大数据", "集成系统",
                    "建筑", "房地产", "交通", "物流", "装饰装修", "家居建材", "景观园林", "城市规划",
                    "银行", "证券", "基金", "保险", "期货", "租赁", "投资", "理财",
                    "媒体", "广告", "旅游", "公关", "文化", "影视", "酒店",
                    "律师事务所", "会计事务所", "人力资源", "企业咨询类",
                    "消费品", "零售", "服装", "家居", "贸易", "餐饮",
                    "化工", "生物", "制药", "医疗", "农林", "畜牧" , "IT", 
                ]
        locations = [
                    "多地", "北京", "江苏", "上海", "成都", "深圳", "杭州", "西安", "重庆", "长沙", "厦门", "武汉", "宁波", 
                    "香港", "广西", "慈溪", "福建", "陕西", "广州", "山东", "河北", "新疆", "无锡", "太原", "天津", 
                    "苏州", "荷兰", "美国", "新加坡", "马来西亚", "日本", "俄罗斯", "哈萨克斯坦", "波兰", "瑞典", "德国", 
                    "韩国", "合肥", "广东", "浙江", "石家庄", "南京", "贵阳", "吉林", "常山", "青岛", "雅加达", "福州", 
                    "哈尔滨", "芜湖", "新昌", "常州", "济南", "南昌", "南宁", "乌鲁木齐", "海口", "河南", "东莞", "镇江", 
                    "六安", "越南", "佛山", "嘉兴", "连云港", "淄博", "泰国", "沈阳", "顺德", "郑州", "长春", "丰城", 
                    "金华", "乐山", "潍坊", "丰城", "宁波", "台州", "蚌埠", "珠海", "张家港", "温州", "湖州", "兰州", 
                    "大同", "海南", "哈尔滨", "顺德", "合肥", "西安", "长沙", "武汉", "青岛", "南京", "佛山", "成都", 
                    "济南", "常州", "贵阳", "上海", "杭州", "南昌", "海口", "长春", "乐山"
                ]


        # 简单的假设：如果是三部分，按照固定顺序；如果是两部分，检测哪个部分是日期格式
        if len(parts) == 3:
            data['company_name'] = parts[0]
            if parts[1] in job_types:
                data['job_type'] = parts[1]
            if re.match(r'\d{4}-\d{2}-\d{2}', parts[2]) or re.match(r'\d{4}-\d{2}', parts[2]):
                data['open_time'] = parts[2]
        elif len(parts) == 2:
            # 如果有行业的标签，就进入
            if parts[0] in fact_types or parts[1] in fact_types:
                if re.match(r'\d{4}-\d{2}-\d{2}', parts[1]) or re.match(r'\d{4}-\d{2}', parts[1]):
                    data['fact_types'] = parts[0]
                    data['open_time'] = parts[1]
                elif re.match(r'\d{4}-\d{2}-\d{2}', parts[0]) or re.match(r'\d{4}-\d{2}', parts[0]):
                    data['open_time'] = parts[0]
                    data['fact_types'] = parts[1]
                elif parts[0] in locations:
                    data['locations'] = parts[0]
                    data['fact_types'] = parts[1]
                elif parts[1] in locations:
                    data['locations'] = parts[1]
                    data['fact_types'] = parts[0]
                else:
                    reply = Reply(ReplyType.TEXT,"请输入正确的格式👺,输入(查找 帮助)查看格式😛")     
                    e_context['reply'] = reply
                    e_context.action = EventAction.BREAK_PASS 
                    return ""
            # 如果有时间标签，就进入
            elif (re.match(r'\d{4}-\d{2}-\d{2}', parts[0]) or re.match(r'\d{4}-\d{2}', parts[0])) or \
                (re.match(r'\d{4}-\d{2}-\d{2}', parts[1]) or re.match(r'\d{4}-\d{2}', parts[1])):
                if re.match(r'\d{4}-\d{2}-\d{2}', parts[1]) or re.match(r'\d{4}-\d{2}', parts[1]):
                    data['locations'] = parts[0]
                    data['open_time'] = parts[1]
                else:
                    data['open_time'] = parts[0]
                    data['locations'] = parts[1]
            else: 
                reply = Reply(ReplyType.TEXT,"请输入正确的格式👺,输入(查找 帮助)查看格式😛")     
                e_context['reply'] = reply
                e_context.action = EventAction.BREAK_PASS 
                return ""
        elif len(parts) == 1:
            # 仅提供一个参数时，判断是哪一种
            if re.match(r'\d{4}-\d{2}-\d{2}', parts[0])  or re.match(r'\d{4}-\d{2}', parts[0]):
                data['open_time'] = parts[0]
            elif parts[0] in job_types:
                # 简单的规则判断，若包含数字，可能是公司名或职位
                # 这里需要根据具体业务规则更改
                data['job_type'] = parts[0]
            elif parts[0] in fact_types:
                data['fact_types'] = parts[0]
            elif parts[0] in locations:
                data['locations'] = parts[0]
            else:          
                data['company_name'] = parts[0]
        else: 
            reply = Reply(ReplyType.TEXT,"请输入正确的格式😭,输入(查找 帮助)查看格式😊")     
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS 
            return ""
        data['job_type'] = "2025届校招/秋招"

        url = "http://8.134.255.243:5000/index"
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, json=data).json()
        
        # json1 = json.dumps(json.loads(response.text), indent=4, sort_keys=False, ensure_ascii=False)
        # print(response['msg'])
        msg = response['msg']
        # logger.info(response.text);
        # query += response.text + "\n----------------\n"
        logger.info(msg);
        if msg == "[]" or msg == None or msg == [] or msg == "":
            reply = Reply(ReplyType.TEXT,"抱歉🥰，查找不到数据😂")     
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS 
            return ""
        #prompt = "你是一位群聊信息检索机器人。只需要对输入的信息进行检索匹配的招聘信息。你先进行匹配然后格式化输出以下信息。输出格式为例子:公司/单位名称:xxx;校招类型:xxx;开启时间:xxxxx;地点:xx;投递链接地址:xxx。把所有匹配的公司都输出，如果公司名找不到说明不存在。请不要输出其他的文本\n"
        prompt = """你是一位群聊信息检索机器人。只需要对输入的信息进行检索匹配的招聘信息。你先进行匹配然后格式化输出以下信息。输出格式为例子:
                公司/单位名称: xxxx
                校招类型: 2025届实习/暑期实习 或者 2025届校招/秋招
                开启时间: xxxx-xx-xx
                地点: xxx
                行业分类: xxxx
                企业性质: xxxx
                官方标题: xxxxxxxxxx
                公告原文链接: https://xxx.xxxx.xxx
                网申/投递地址: https://xxx.xxxx.xxx
                如果需要输出的内容多于3个，就只需要输出3个然后补充如下内容(注意：只有在输出大于3个时才补充):“更多信息可查看链接: http://wayzinx.fun:5000/show”。
                输出的时候就按照上面的格式输出，如果不多余3个就按照上面的格式正常输出就行了。请不要输出其他无关的文本，严格按照上面的描述来输出，不要输出多于的不必要的文本。
                """
        msg_str = json.dumps(msg, ensure_ascii=False, indent=2)
        # query = "查找到的数据:{" + msg_str + "}" + "\n----------------\n"
        query += "查找到的数据:{" + msg_str + "},如果前面查找到的数据为空，说明不存在。举例数据含义按顺序是： 'xxxx'表示公司名；'2025届实习/暑期实习'表示校招类型, 'xxxx')表示投递链接。" +"\n----------------\n"
        logger.info(query);       
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

    def search_today_message(self, e_context):
        cmsg : ChatMessage = e_context['context']['msg']
        session_id = cmsg.from_user_id
        data = {}
        # 获取今天的日期
        today = datetime.today()
        formatted_date = today.strftime("%Y-%m-%d")
        data['open_time'] = formatted_date
        data['time_num'] = 0
        url = "http://8.134.255.243:5000/recently"
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, json=data).json()
        msg = response['msg']
        logger.info(msg);
        if msg == "[]" or msg == None or msg == [] or msg == "":
            reply = Reply(ReplyType.TEXT,"飞仓爆倩🤣，今天并没有开启的公司🥵")     
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS 
            return ""
        prompt = """你是一位群聊信息检索机器人。只需要对输入的信息进行检索匹配的招聘信息。你先进行匹配然后格式化输出以下信息。输出格式为例子:
                公司/单位名称: xxxx
                校招类型: 2025届实习/暑期实习 或者 2025届校招/秋招
                开启时间: xxxx-xx-xx
                截止时间（尽快投递≈招满即止）: xxxx-xx-xx
                地点: xxx
                行业分类: xxxx
                企业性质: xxxx                
                官方标题: xxxxxxxxxx
                公告原文链接: https://xxx.xxxx.xxx
                网申/投递地址: https://xxx.xxxx.xxx
                如果需要输出的内容多于3个，就只需要输出3个然后补充如下内容:更多信息可查看链接: http://wayzinx.fun:5000/show
                把所有匹配的公司都输出，如果公司名找不到说明不存在。输出的时候就按照上面的格式输出，请不要输出其他无关的文本。
                """

        msg_str = json.dumps(msg, ensure_ascii=False, indent=2)
        query = "查找到的数据:{" + msg_str + "}" + "\n----------------\n"
        btype = Bridge().btype['chat']
        bot = bot_factory.create_bot(Bridge().btype['chat'])
        session = bot.sessions.build_session(session_id, prompt)
        session.add_query(query)
        result = bot.reply_text(session)
        reply_content = result['content']
        reply = Reply()
        reply = Reply(ReplyType.TEXT,reply_content)     
        e_context['reply'] = reply
        e_context.action = EventAction.BREAK_PASS


    def recently_message(self, e_context, time_num):
        cmsg : ChatMessage = e_context['context']['msg']
        session_id = cmsg.from_user_id
        data = {}
        if time_num > 7 :
            reply = Reply(ReplyType.TEXT,"查找天天数太多了😯，建议天数选择一周内🥹")     
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS 
            return ""
        # 获取今天的日期
        today = datetime.today()
        formatted_date = today.strftime("%Y-%m-%d")
        data['open_time'] = formatted_date
        data['time_num'] = time_num
        url = "http://8.134.255.243:5000/recently"
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.post(url, headers=headers, json=data).json()
        msg = response['msg']
        logger.info(msg);
        if msg == "[]" or msg == None or msg == [] or msg == "":
            reply = Reply(ReplyType.TEXT,"哎😭，最近并没有开启的公司🙂")     
            e_context['reply'] = reply
            e_context.action = EventAction.BREAK_PASS 
            return ""
        prompt = """你是一位群聊信息检索机器人。只需要对输入的信息进行检索匹配的招聘信息。你先进行匹配然后格式化输出以下信息。输出格式为例子:
                公司/单位名称: xxxx
                校招类型: 2025届实习/暑期实习 或者 2025届校招/秋招
                开启时间: xxxx-xx-xx
                截止时间（尽快投递≈招满即止）: xxxx-xx-xx
                地点: xxx
                行业分类: xxxx
                企业性质: xxxx
                官方标题: xxxxxxxxxx
                公告原文链接: https://xxx.xxxx.xxx
                网申/投递地址: https://xxx.xxxx.xxx
                如果需要输出的内容多于3个，就只需要输出3个然后补充如下内容:更多信息可查看链接: http://wayzinx.fun:5000/show
                把所有匹配的公司都输出，如果公司名找不到说明不存在。输出的时候就按照上面的格式输出，请不要输出其他无关的文本。
                """
        # 将 msg 列表转换为 JSON 字符串
        msg_str = json.dumps(msg, ensure_ascii=False, indent=2)
        query = "查找到的数据:{" + msg_str + "}" + "\n----------------\n"
        btype = Bridge().btype['chat']
        bot = bot_factory.create_bot(Bridge().btype['chat'])
        session = bot.sessions.build_session(session_id, prompt)
        session.add_query(query)
        result = bot.reply_text(session)
        reply_content = result['content']
        reply = Reply()
        reply = Reply(ReplyType.TEXT,reply_content)     
        e_context['reply'] = reply
        e_context.action = EventAction.BREAK_PASS


    def get_help_text(self, **kwargs):
        help_text = (
            "1.🥰输入 查找 <您需要查找的公司名字> <校招类型二选一: (2025届校招/秋招) 或 (2025届实习/暑期实习)> <时间(2024-06-06)(格式:xxxx-xx-xx)>'，我会帮您查找\n2.😊输入 查找今日开启\n3.😁输入 秋招 最近x天(x自定)"
        )
        return help_text
