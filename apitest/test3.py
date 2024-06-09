import os
import requests
import json
# url = "http://8.134.255.243:5000/index"
# headers = {
#     'Content-Type': 'application/json'
# }
# response = requests.get(url, headers=headers).json()
# # json1 = json.dumps(json.loads(response.text), indent=4, sort_keys=False, ensure_ascii=False)
# print(response['msg'])
# -*- coding: UTF-8 -*-
"""
@Project :small-tools 
@File    :tengxun.py
@Author  :silen
@Time    :2022/5/26 15:42
@Description : 
"""
import json
import os
import re
import time
from datetime import datetime
from time import sleep
import click
import pandas as pd
import requests
from bs4 import BeautifulSoup


class TengXunDocument():

    def __init__(self, document_url, local_pad_id, cookie_value):
        # excel文档地址
        self.document_url = document_url
        # 此值每一份腾讯文档有一个,需要手动获取
        self.localPadId = local_pad_id
        self.headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Cookie': cookie_value
        }

    def get_now_user_index(self):
        """
        # 获取当前用户信息,供创建下载任务使用
        :return:
            # nowUserIndex = '4883730fe8b94fbdb94da26a9a63b688'
            # uid = '144115225804776585'
            # utype = 'wx'
        """
        response_body = requests.get(url=self.document_url, headers=self.headers, verify=False)
        parser = BeautifulSoup(response_body.content, 'html.parser')
        global_multi_user_list = re.findall(re.compile('window.global_multi_user=(.*?);'), str(parser))
        if global_multi_user_list:
            user_dict = json.loads(global_multi_user_list[0])
            print(user_dict)
            return user_dict['nowUserIndex']
        return 'cookie过期,请重新输入'

    def export_excel_task(self, export_excel_url):
        """
        导出excel文件任务,供查询文件数据准备进度
        :return:
        """
        body = {
            'docId': self.localPadId, 'version': '2'
        }

        res = requests.post(url=export_excel_url,
                                      headers=self.headers, data=body, verify=False)
        operation_id = res.json()['operationId']
        return operation_id



    def download_excel(self, check_progress_url, file_name):
        """
        下载excel文件
        :return:
        """
        # 拿到下载excel文件的url
        start_time = time.time()
        file_url = ''
        while True:
            res = requests.get(url=check_progress_url, headers=self.headers, verify=False)
            progress = res.json()['progress']
            if progress == 100:
                file_url = res.json()['file_url']
                break
            elif time.time() - start_time > 30:
                print("数据准备超时,请排查")
                break
        if file_url:
            self.headers['content-type'] = 'application/octet-stream'
            res = requests.get(url=file_url, headers=self.headers, verify=False)
            with open(file_name, 'wb') as f:
                f.write(res.content)
            print('下载成功,文件名: ' + file_name)
        else:
            print("下载文件地址获取失败, 下载excel文件不成功")


if __name__ == '__main__':
    # excel文档地址
    document_url = 'https://docs.qq.com/sheet/DZlVOanBMb2N2dWhD?tab=BB08J2'
    # 此值每一份腾讯文档有一个,需要手动获取
    local_pad_id = '300000000$fUNjpLocvuhC'
    # 打开腾讯文档后,从抓到的接口中获取cookie信息
    cookie_value = 'fingerprint=0ed7a8b5fcec4548af5d256da80065b97; RK=gr8gfzOmeX; ptcz=27d7ea169acefcbe4b53104bca8ba1ced3095073aa4dde7903b8bed0b558952e; eas_sid=31F7Y1M1k2C4m6q7z4P8z8E627; pgv_pvid=2848417708; LW_uid=x147o1y4S4o5L5x655o4B0u6t2; pac_uid=0_8ab4279e2f35f; iip=0; _qimei_uuid42=18501132733100e880bb71f762b45fa54d8001df22; _qimei_fingerprint=d4efa01b33985a833c58061325fe1e99; _qimei_q36=; _qimei_h38=30e76a7280bb71f762b45fa502000007e18501; suid=ek171456359322156999; LW_sid=x1g7q1x7f06771L8m5K6b1x0o2; low_login_enable=1; uid=144115211846965314; uid_key=EOP1mMQHGixrcDNtU1JpRTZ6b011OGs5UlA4aGNNYmFOUUpUNXNtMG8wWFA1ZkIyZDR3PSKBAmV5SmhiR2NpT2lKQlEwTkJURWNpTENKMGVYQWlPaUpLVjFRaWZRLmV5SlVhVzU1U1VRaU9pSXhORFF4TVRVeU1URTRORFk1TmpVek1UUWlMQ0pXWlhJaU9pSXhJaXdpUkc5dFlXbHVJam9pYzJGaGMxOTBiMk1pTENKU1ppSTZJa1pDV1ZsYVlpSXNJbVY0Y0NJNk1UY3lNREU1TWprNE9Td2lhV0YwSWpveE56RTNOakF3T1RnNUxDSnBjM01pT2lKVVpXNWpaVzUwSUVSdlkzTWlmUS5xei1KZnEyZ0NxeFNYYzJVdjVFMS02XzJOU19wc3NRXzV3YjRINU9rMWlRKN2foLQG; utype=wx; wx_appid=wx46dfe750eef96da7; openid=o2MwI04jA11mQnEF8RV9FgRfe9sQ; access_token=81_r6mJISnPz3-AhWhsu91e07WHhmi2JDXwNOaSatPZFnGmCJM07Jl96Pww1_tK5-oZTlTaRrl0QBqJzy90teiS5XxYetR1Dc24TeAzYRqfWQE; refresh_token=81__jChC24rkL-PwiaC6j3EzvLLqJA9JFQ61kKQaTU8UUqMuyc_wEtvWCtUQO8SlrlUQqXvGaamcIs0nyz8EAXoiKxCUSFSUufCjwaKYPKpxB8; env_id=gray-pct25; gray_user=true; DOC_SID=ff656f0c2f1b4cff874cacd9ea7a87dd3109dc5697004c26bc9a1b1798b889aa; SID=ff656f0c2f1b4cff874cacd9ea7a87dd3109dc5697004c26bc9a1b1798b889aa; loginTime=1717600992033; optimal_cdn_domain=docs.gtimg.com; traceid=380320ce7f; TOK=380320ce7f3a54aa; hashkey=380320ce'
    tx = TengXunDocument(document_url, local_pad_id, cookie_value)
    now_user_index = tx.get_now_user_index()
    # 导出文件任务url
    export_excel_url = f'https://docs.qq.com/v1/export/export_office?u={now_user_index}'
    # 获取导出任务的操作id
    operation_id = tx.export_excel_task(export_excel_url)
    check_progress_url = f'https://docs.qq.com/v1/export/query_progress?u={now_user_index}&operationId={operation_id}'
    # current_datetime = datetime.strftime(datetime.now(), '%Y_%m_%d_%H_%M_%S')
    # file_name = f'{current_datetime}.xlsx'
    file_name = f'秋招信息表.xlsx'
    tx.download_excel(check_progress_url, file_name)


