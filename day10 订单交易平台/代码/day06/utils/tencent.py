from tencentcloud.common import credential
from tencentcloud.sms.v20210111 import sms_client, models


def send_sms(mobile, sms_code):
    mobile = "+86{}".format(mobile)
    try:
        cred = credential.Credential("AKIDa0B7nhOq3zf5G8l9TMzNVO0MRHrAE3Yn", "4rPincBUYMuCEzUjsdIiuqWv3vYu0qPh")
        client = sms_client.SmsClient(cred, "ap-guangzhou")

        req = models.SendSmsRequest()

        req.SmsSdkAppId = "1400455481"
        req.SignName = "Python之路"
        req.TemplateId = "548762"
        req.TemplateParamSet = [sms_code, ]
        req.PhoneNumberSet = [mobile, ]
        resp = client.SendSms(req)
        print(resp.SendStatusSet)
        data_object = resp.SendStatusSet[0]
        # print(data_dict,type(data_dict))
        from tencentcloud.sms.v20210111.models import SendStatus
        print(data_object.Code)
        if data_object.Code == "Ok":
            return True
    except Exception as e:
        print(e)
