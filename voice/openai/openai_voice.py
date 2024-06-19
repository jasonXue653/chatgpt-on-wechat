"""
google voice service
"""
import json

import openai

from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
from voice.voice import Voice
import requests
from common import const
import datetime, random

class OpenaiVoice(Voice):
    def __init__(self):
        openai.api_key = conf().get("open_ai_api_key")

    def voiceToText(self, voice_file):
        logger.debug("[Openai] voice file name={}".format(voice_file))
        try:
            file = open(voice_file, "rb")
            # api_base = conf().get("open_ai_api_base") or "https://api.openai.com/v1"
            api_base = "https://api.apichat.shop/v1"
            url = f'{api_base}/audio/transcriptions'
            headers = {
                # 'Authorization': 'Bearer ' + conf().get("open_ai_api_key"),
                'Authorization': 'Bearer sk-549taNxL66HcAf3LBf64D7C7D79f49268c08967a6326Fa60',
                # 'Content-Type': 'multipart/form-data' # 加了会报错，不知道什么原因
            }
            files = {
                "file": file,
            }
            data = {
                "model": "whisper-1",
            }
            response = requests.post(url, headers=headers, files=files, data=data)
            response_data = response.json()
            text = response_data['text']
            reply = Reply(ReplyType.TEXT, text)
            logger.info("[Openai] voiceToText text={} voice file name={}".format(text, voice_file))
        except Exception as e:
            reply = Reply(ReplyType.ERROR, "我爹说了让我暂时听不清您的语音，等会再问，如果着急联系微信:keepfighted。")
        finally:
            return reply


    def textToVoice(self, text):
        try:
            # api_base = conf().get("open_ai_api_base") or "https://api.openai.com/v1"
            url = 'https://api.minimax.chat/v1/t2a_pro?GroupId=1782658868262748416'
            headers = {
                'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJHcm91cE5hbWUiOiJqYXNvbiIsIlVzZXJOYW1lIjoiamFzb24iLCJBY2NvdW50IjoiamFzb25AMTc4MjY1ODg2ODI2Mjc0ODQxNiIsIlN1YmplY3RJRCI6IjE3OTY0Mzg4NjM5ODQ0Njc5NjgiLCJQaG9uZSI6IiIsIkdyb3VwSUQiOiIxNzgyNjU4ODY4MjYyNzQ4NDE2IiwiUGFnZU5hbWUiOiIiLCJNYWlsIjoiIiwiQ3JlYXRlVGltZSI6IjIwMjQtMDUtMzEgMTU6MDk6MzYiLCJpc3MiOiJtaW5pbWF4In0.VuS--ZSCumcisvli0Mx2vilhM9pAI4oPPMKCOsauJvQww2-nHqunYbs7UaEUFi-jfI7-nZ3UozG4Zb3MTVKnGCta6jC-dz_UJYsK2WT4X-fQj6ynu0Yth0MmPkPaWOOSR0wd5nksowmCa2UgCS7SXESimKufgMxMRitJzE4FzluqpRgfIYKL6K_iPIvsGXvd00L0VehpJZna_-JRjS-AK4SYre2SxfgwciH-aYl7bGq5okUO1M1-VK8KE0eCovfstLw_z-4_2KF943yTFqnSZeLI4xGG4hHC8b8Zrx8xWXMwXn13THLe_DvPE4HaruOoWcvyUcKeJzH5EoKJcN6OxA',
                'Content-Type': 'application/json',
                'Cookie': 'acw_tc=467e3516de783fd3f7548616dbfac6f22856f0fd49e694f41986b19db5d7f083'
            }

            voice_ids = [
                "male-qn-qingse", "male-qn-jingying", "male-qn-badao", "male-qn-daxuesheng",
                "female-shaonv", "female-yujie", "female-chengshu", "female-tianmei",
                "presenter_male", "presenter_female", "audiobook_male_1", "audiobook_male_2",
                "audiobook_female_1", "audiobook_female_2", "male-qn-qingse-jingpin",
                "male-qn-jingying-jingpin", "male-qn-badao-jingpin", "male-qn-daxuesheng-jingpin",
                "female-shaonv-jingpin", "female-yujie-jingpin", "female-chengshu-jingpin",
                "female-tianmei-jingpin"
            ]

            # Randomly select a voice ID
            selected_voice_id = random.choice(voice_ids)

            payload = json.dumps({
                "voice_id": selected_voice_id,
                "text": text,
                "model": "speech-01",
                "speed": 1,
                "vol": 1,
                "pitch": 0,
                "char_to_pitch": [
                    "你/(ni3)"
                ]
            })
            response = requests.post(url, headers=headers, data=payload)
            file_name = "tmp/" + datetime.datetime.now().strftime('%Y%m%d%H%M%S') + str(
                random.randint(0, 1000)) + ".mp3"
            logger.debug(f"[OPENAI] text_to_Voice file_name={file_name}, input={text}")

            # 解析返回值中的文件
            audio_url = response.json()['audio_file']
            logger.info(f"[MINIMAX] text_to_Voice audio_url={audio_url}")

            audio_response = requests.get(audio_url)
            if audio_response.status_code == 200:
                with open(file_name, 'wb') as f:
                    f.write(audio_response.content)
                    print("音频文件下载成功:", file_name)
            else:
                print("下载失败，状态码:", response.status_code)

            logger.info(f"[OPENAI] text_to_Voice success")
            reply = Reply(ReplyType.VOICE, file_name)
        except Exception as e:
            logger.error(e)
            reply = Reply(ReplyType.ERROR, "我爹说了遇到了一点小问题，等会再问，如果着急联系微信:keepfighted。")
        return reply
