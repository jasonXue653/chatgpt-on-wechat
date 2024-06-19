import json
import time

import openai
import openai.error
import requests

from common.log import logger
from common.token_bucket import TokenBucket
from config import conf


# OPENAI提供的画图接口
class OpenAIImage(object):
    def __init__(self):
        openai.api_key = conf().get("open_ai_api_key")
        if conf().get("rate_limit_dalle"):
            self.tb4dalle = TokenBucket(conf().get("rate_limit_dalle", 50))

    def create_img(self, query, retry_count=0, api_key=None, api_base=None):
        try:
            if conf().get("rate_limit_dalle") and not self.tb4dalle.get_token():
                return False, "请求太快了，请休息一下再问我吧"


            logger.info("[OPEN_AI] image_query={}".format(query))
            # response = openai.Image.create(
            #     api_key=api_key,
            #     prompt=query,  # 图片描述
            #     n=1,  # 每次生成图片的数量
            #     model=conf().get("text_to_image") or "dall-e-2",
            #     # size=conf().get("image_create_size", "256x256"),  # 图片大小,可选有 256x256, 512x512, 1024x1024
            # )

            url = "https://api.siliconflow.cn/v1/stabilityai/stable-diffusion-xl-base-1.0/text-to-image"

            payload = json.dumps({
                "prompt": query,
                "image_size": "1024x1024",
                "batch_size": 1,
                "num_inference_steps": 20,
                "guidance_scale": 7.5
            })
            headers = {
                'accept': 'application/json',
                'authorization': 'Bearer sk-megzeuvvhiqgqllzaowteljmpjgtzyvlsxtwguyntmdaqqyq',
                'content-type': 'application/json'
            }

            response = requests.request("POST", url, headers=headers, data=payload)
            response = json.loads(response.content)
            image_url = response["images"][0]["url"]

            logger.info("[OPEN_AI] image_url={}".format(image_url))
            return True, image_url
        except openai.error.RateLimitError as e:
            logger.warn(e)
            if retry_count < 1:
                time.sleep(5)
                logger.warn("[OPEN_AI] ImgCreate RateLimit exceed, 第{}次重试".format(retry_count + 1))
                return self.create_img(query, retry_count + 1)
            else:
                return False, "画图出现问题，请休息一下再问我吧"
        except Exception as e:
            logger.exception(e)
            return False, "画图出现问题，请休息一下再问我吧"