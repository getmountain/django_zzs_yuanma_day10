from tencentcloud.common import credential
from tencentcloud.sms.v20210111 import sms_client, models

cred = credential.Credential("AKIDa0B7nhOq3zf5G8l9TMzNVO0MRHrAE3Yn", "4rPincBUYMuCEzUjsdIiuqWv3vYu0qPh")
client = sms_client.SmsClient(cred, "ap-guangzhou")

req = models.SendSmsRequest()

req.SmsSdkAppId = "1400455481"
req.SignName = "Python之路"
req.TemplateId = "548762"
req.TemplateParamSet = ["449739"]
req.PhoneNumberSet = ["+8615131255089"]

resp = client.SendSms(req)
print(resp, type(resp))
print(resp.SendStatusSet, type(resp.SendStatusSet))
from tencentcloud.sms.v20210111.models import SendSmsResponse
# {"SendStatusSet": [{"SerialNo": "2640:262727967816586500757778766", "PhoneNumber": "+8618630087660", "Fee": 1, "SessionContext": "", "Code": "Ok", "Message": "send success", "IsoCode": "CN"}], "RequestId": "5528d8e4-31c3-41e3-9e6b-ef8006f365cd"}

# [{"SerialNo": "", "PhoneNumber": "+8618630087660", "Fee": 0, "SessionContext": "", "Code": "LimitExceeded.PhoneNumberThirtySecondLimit", "Message": "the number of SMS messages sent from a single mobile number within 30 seconds exceeds the upper limit", "IsoCode": "CN"}] <class 'list'>
# [{"SerialNo": "2640:133731727416586503152335508", "PhoneNumber": "+8615131255089", "Fee": 1, "SessionContext": "", "Code": "Ok", "Message": "send success", "IsoCode": "CN"}]
