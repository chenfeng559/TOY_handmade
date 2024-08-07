
import websocket
import datetime
import hashlib
import base64
import hmac
import json
from urllib.parse import urlencode
import time
import ssl
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import _thread as thread

full_message = ""

STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识


class SpeechRecognition(object):
    # 初始化
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile

        # 公共参数(common)
        self.CommonArgs = {"app_id": self.APPID}
        # 业务参数(business)，更多个性化参数可在官网查看
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo":1,"vad_eos":10000}

    # 生成url
    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        # 生成RFC1123格式的时间戳
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))

        # 拼接字符串
        signature_origin = "host: " + "ws-api.xfyun.cn" + "\n"
        signature_origin += "date: " + date + "\n"
        signature_origin += "GET " + "/v2/iat " + "HTTP/1.1"
        # 进行hmac-sha256进行加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')

        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urlencode(v)
        # print("date: ",date)
        # print("v: ",v)
        # 此处打印出建立连接时候的url,参考本demo的时候可取消上方打印的注释，比对相同参数时生成的url与自己代码生成的url是否一致
        # print('websocket url :', url)
        return url


# 收到websocket消息的处理
def on_message(ws, message, message_list):
    try:
        code = json.loads(message)["code"]
        sid = json.loads(message)["sid"]
        if code != 0:
            errMsg = json.loads(message)["message"]
            print(f"sid:{sid} call error:{errMsg} code is:{code}")
        else:
            data = json.loads(message)["data"]["result"]["ws"]
            result = ""
            for i in data:
                for w in i["cw"]:
                    result += w["w"]
            message_list.append(result)
    except Exception as e:
        print("receive msg, but parse exception:", e)


# 收到websocket错误的处理
def on_error(ws, error):
    print("### error:", error)


# 收到websocket关闭的处理
def on_close(ws,a,b):
    print("### Finsh ###")


# 收到websocket连接建立的处理
def on_open(ws, instance):
    def run(*args):
        frameSize = 8000
        intervel = 0.04
        status = STATUS_FIRST_FRAME
        try:
            with open(instance.AudioFile, "rb") as fp:
                while True:
                    buf = fp.read(frameSize)
                    if not buf:
                        status = STATUS_LAST_FRAME
                    if status == STATUS_FIRST_FRAME:
                        d = {"common": instance.CommonArgs,
                             "business": instance.BusinessArgs,
                             "data": {"status": 0, "format": "audio/L16;rate=16000",
                                      "audio": str(base64.b64encode(buf), 'utf-8'),
                                      "encoding": "raw"}}
                        d = json.dumps(d)
                        ws.send(d)
                        status = STATUS_CONTINUE_FRAME
                    elif status == STATUS_CONTINUE_FRAME:
                        d = {"data": {"status": 1, "format": "audio/L16;rate=16000",
                                      "audio": str(base64.b64encode(buf), 'utf-8'),
                                      "encoding": "raw"}}
                        ws.send(json.dumps(d))
                    elif status == STATUS_LAST_FRAME:
                        d = {"data": {"status": 2, "format": "audio/L16;rate=16000",
                                      "audio": str(base64.b64encode(buf), 'utf-8'),
                                      "encoding": "raw"}}
                        ws.send(json.dumps(d))
                        time.sleep(1)
                        break
            time.sleep(1)
            ws.close()
        except Exception as e:
            print("file exception:", e)

    thread.start_new_thread(run, ())


# 语音识别,外部调用
def recognize_speech(APPID, APIKey, APISecret, AudioFile):
    recognizer = SpeechRecognition(APPID, APIKey, APISecret, AudioFile)
    ws_url = recognizer.create_url()
    message_list = []

    ws = websocket.WebSocketApp(ws_url,
                                on_message=lambda ws, msg: on_message(ws, msg, message_list),
                                on_error=on_error,
                                on_close=on_close)

    ws.on_open = lambda ws: on_open(ws, recognizer)
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    return ''.join(message_list)



if __name__ == "__main__":
    key = recognize_speech(
        APPID='68c6d108',
        APISecret='YjAyN2QxM2JjZDUwNmRlMTYxZDExYTE4',
        APIKey='d05347012a653385c38b8d877d844344',
        AudioFile=r'.\audio\iat_pcm_16k.pcm'
    )
    print(key)