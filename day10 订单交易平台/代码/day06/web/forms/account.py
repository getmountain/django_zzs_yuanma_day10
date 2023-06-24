import random
from django import forms
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from utils.encrypt import md5
from web import models
from utils import tencent
from django_redis import get_redis_connection


class LoginForm(forms.Form):
    role = forms.ChoiceField(
        label="角色",
        required=True,
        choices=(("2", "客户"), ("1", "管理员")),
        widget=forms.Select(attrs={"class": "form-control"})
    )

    username = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "用户名"})
    )

    password = forms.CharField(
        label="密码",
        # min_length=6,
        # max_length=10,
        # validators=[RegexValidator(r'^[0-9]+$', '密码必须是数字'), ],  # 正则表达式
        widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "密码"}, render_value=True)
    )

    def clean_username(self):
        user = self.cleaned_data['username']
        # 校验规则
        # 校验失败
        if len(user) < 3:
            from django.core.exceptions import ValidationError
            raise ValidationError("用户名格式错误")
        return user

    def clean_password(self):
        return md5(self.cleaned_data['password'])

    def clean(self):
        # 对所有值进行校验，无论前面的字段校验成功与否
        user = self.cleaned_data.get('username')
        pwd = self.cleaned_data.get('password')
        if user and pwd:
            pass
        from django.core.exceptions import ValidationError
        # 1.不返回值，默认 self.cleaned_data
        # 2.返回值，self.cleaned_data=返回的值
        # 3.报错，ValidationError ->  self.add_error(None, e)
        # print(self.cleaned_data)
        # raise ValidationError("整xxxxx体错误")

    def _post_clean(self):
        pass


class SmsLoginForm(forms.Form):
    role = forms.ChoiceField(
        label="角色",
        required=True,
        choices=(("2", "客户"), ("1", "管理员")),
        widget=forms.Select(attrs={"class": "form-control"})
    )

    mobile = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1[358]\d{9}$', '手机格式错误'), ],
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "手机号"})
    )

    code = forms.CharField(
        label="短信验证码",
        validators=[RegexValidator(r'^[0-9]{4}$', '验证码格式错误'), ],
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "短信验证码"})
    )


    def clean_code(self):
        mobile = self.cleaned_data.get('mobile')
        code = self.cleaned_data['code']
        if not mobile:
            return code

        conn = get_redis_connection("default")
        cache_code = conn.get(mobile)
        if not cache_code:
            raise ValidationError("短信验证码未发送或失效")

        if code != cache_code.decode('utf-8'):
            raise ValidationError("短信验证码未发送或失效")

        return code


class MobileForm(forms.Form):
    role = forms.ChoiceField(
        label="角色",
        required=True,
        choices=(("2", "客户"), ("1", "管理员")),
        widget=forms.Select(attrs={"class": "form-control"})
    )

    mobile = forms.CharField(
        label="手机号",
        required=True,
        validators=[RegexValidator(r'^1[358]\d{9}$', '手机格式错误'), ]
    )

    def clean_mobile(self):
        role = self.cleaned_data.get('role')
        mobile = self.cleaned_data['mobile']
        if not role:
            return mobile

        if role == "1":
            exists = models.Administrator.objects.filter(active=1, mobile=mobile).exists()
        else:
            exists = models.Customer.objects.filter(active=1, mobile=mobile).exists()
        if not exists:
            raise ValidationError("手机号不存在-钩子")

        # 2.发送短信 + 生成验证码
        sms_code = str(random.randint(1000, 9999))
        is_success = tencent.send_sms(mobile, sms_code)
        if not is_success:
            raise ValidationError("短信发送失败-钩子")

        # 3.将手机号和验证码保存（以便于下次校验） redis -> 超时时间
        conn = get_redis_connection("default")
        conn.set(mobile, sms_code, ex=60)

        return mobile
