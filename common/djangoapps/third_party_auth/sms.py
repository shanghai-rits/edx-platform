from social_django.models import UserSocialAuth
from django.conf import settings
from .phone import Phone
from .backends import SmsCodeBackend
import datetime
import time
import random
import json
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile

class TencentSmsService:
    def __init__(self, phone, code):
        # 实例化一个认证对象。
        # SecretId、SecretKey 查询: https://console.cloud.tencent.com/cam/capi
        cred = credential.Credential(settings.TENCENT_SMS_ACCESS_KEY_ID, settings.TENCENT_SMS_ACCESS_SECRET)
        # 实例化一个http选项。
        httpProfile = HttpProfile()
        httpProfile.endpoint = settings.TENCENT_SMS_DOMAIN # 指定接入地域域名(默认就近接入)

        # 实例化一个客户端配置对象
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile

        # 实例化要请求产品(以sms为例)的client对象
        self.client = sms_client.SmsClient(cred, 'ap-guangzhou', clientProfile)

        # 实例化一个请求对象，根据调用的接口和实际情况，可以进一步设置请求参数
        self.req = models.SendSmsRequest()
        # 短信应用ID: 短信SdkAppId在 [短信控制台] 添加应用后生成的实际SdkAppId，示例如1400006666
        # "1400787878"
        self.req.SmsSdkAppId = settings.TENCENT_SMS_SDK_APP_ID
        # # 短信签名内容: 使用 UTF-8 编码，必须填写已审核通过的签名，签名信息可登录 [短信控制台] 查看
        self.req.SignName =  settings.TENCENT_SMS_SIGN_NAME
        # # 短信码号扩展号: 默认未开通，如需开通请联系 [sms helper]
        # req.ExtendCode = ""
        # # 用户的 session 内容: 可以携带用户侧 ID 等上下文信息，server 会原样返回
        # req.SessionContext = ""
        # # 国际/港澳台短信 senderid: 国内短信填空，默认未开通，如需开通请联系 [sms helper]
        # req.SenderId = ""
        # 下发手机号码，采用 E.164 标准，+[国家或地区码][手机号]
        # 示例如：+8613711112222， 其中前面有一个+号 ，86为国家码，13711112222为手机号，最多不要超过200个手机号
        # req.PhoneNumberSet = ["+8613711112222"]
        # 模板 ID: 必须填写已审核通过的模板 ID。模板ID可登录 [短信控制台] 查看
        self.req.TemplateId = settings.TENCENT_SMS_TEMPLATE_CODE 
        # 下发手机号码，采用 E.164 标准，+[国家或地区码][手机号]
        # 示例如：+8613711112222， 其中前面有一个+号 ，86为国家码，13711112222为手机号，最多不要超过200个手机号
        self.req.PhoneNumberSet = ["+86" + phone]
        # 模板参数
        self.req.TemplateParamSet = [code]
        #self.req.Region = 'ap-guangzhou'
    
    def send(self):
        try:
            response = self.client.SendSms(self.req)
            return json.loads(response.to_json_string())
        except TencentCloudSDKException as err:
            return(err)

    @classmethod
    def create_sms_code(cls, length=6):
        storage = [str(i) for i in range(0, 10)]
        lst = map(lambda x: storage[random.randint(0, 9)], range(0, length))
        code = ''.join(lst)
        return code

    @classmethod
    def create_expires(cls, **kwargs):
        expires = datetime.datetime.now() + datetime.timedelta(**kwargs)
        timestamp = time.mktime(expires.timetuple())
        return timestamp


def sms_code_verification(phone, sms_code, action, session):
    return SmsCodeBackend.verify_sms_code_and_get_conflict(phone, sms_code, action, session)


def check_phone_exists(phone=None):
    return UserSocialAuth.objects.filter(provider='sms', uid=Phone(phone).make_phone()).exists()    