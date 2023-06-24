from django.shortcuts import render, redirect
from django.http import JsonResponse
from web import models
from django import forms
from utils.bootstrap import BootStrapForm
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from utils.encrypt import md5
from utils.reponse import BaseResponse
from django.utils.safestring import mark_safe
from utils.pager import Pagination
from django.db.models import Q


def customer_list(request):
    keyword = request.GET.get("keyword", "").strip()
    con = Q()
    if keyword:
        con.connector = 'OR'
        con.children.append(('username__contains', keyword))
        con.children.append(('mobile__contains', keyword))
        con.children.append(('level__title__contains', keyword))

    queryset = models.Customer.objects.filter(con).filter(active=1).select_related('level')
    obj = Pagination(request, queryset)
    context = {
        "queryset": queryset[obj.start:obj.end],
        "pager_string": obj.html(),
        "keyword": keyword
    }

    return render(request, 'customer_list.html', context)


class CustomerModelForm(BootStrapForm, forms.ModelForm):
    exclude_filed_list = ['level']

    confirm_password = forms.CharField(
        label="重复密码",
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.Customer
        fields = ["username", 'mobile', 'password', 'confirm_password', 'level']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
            'level': forms.RadioSelect(attrs={'class': "form-radio"})
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 此处可能用到 request
        self.fields['level'].queryset = models.Level.objects.filter(active=1)

    def clean_password(self):
        password = self.cleaned_data['password']

        return md5(password)

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = md5(self.cleaned_data.get('confirm_password', ''))

        if password != confirm_password:
            raise ValidationError("密码不一致")
        return confirm_password


def customer_add(request):
    if request.method == "GET":
        form = CustomerModelForm(request)
        return render(request, "form2.html", {'form': form})

    form = CustomerModelForm(request, data=request.POST)
    if not form.is_valid():
        return render(request, "form2.html", {'form': form})

    form.instance.creator_id = request.nb_user.id
    form.save()
    return redirect("/customer/list/")


class CustomerEditModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Customer
        fields = ["username", 'mobile', 'level']
        widgets = {
            'password': forms.PasswordInput(render_value=True)
        }

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 此处可能用到 request
        self.fields['level'].queryset = models.Level.objects.filter(active=1)


def customer_edit(request, pk):
    instance = models.Customer.objects.filter(id=pk, active=1).first()

    if request.method == 'GET':
        form = CustomerEditModelForm(request, instance=instance)
        return render(request, 'form2.html', {'form': form})

    form = CustomerEditModelForm(request, instance=instance, data=request.POST)
    if not form.is_valid():
        return render(request, 'form2.html', {'form': form})
    form.save()

    from utils.link import filter_reverse
    return redirect(filter_reverse(request, "/customer/list/"))


class CustomerResetModelForm(BootStrapForm, forms.ModelForm):
    confirm_password = forms.CharField(
        label="重复密码",
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.Customer
        fields = ['password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }

    def clean_password(self):
        password = self.cleaned_data['password']

        return md5(password)

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = md5(self.cleaned_data.get('confirm_password', ''))

        if password != confirm_password:
            raise ValidationError("密码不一致")
        return confirm_password


def customer_reset(request, pk):
    if request.method == "GET":
        form = CustomerResetModelForm()
        return render(request, 'form2.html', {'form': form})
    instance = models.Customer.objects.filter(id=pk, active=1).first()
    form = CustomerResetModelForm(data=request.POST, instance=instance)
    if not form.is_valid():
        return render(request, 'form2.html', {'form': form})
    form.save()
    return redirect("/customer/list/")


def customer_delete(request):
    cid = request.GET.get('cid', 0)
    if not cid:
        res = BaseResponse(status=False, detail="请选择要删除的数据")
        return JsonResponse(res.dict)

    exists = models.Customer.objects.filter(id=cid, active=1).exists()
    if not exists:
        res = BaseResponse(status=False, detail="要删除的数据不存在")
        return JsonResponse(res.dict)

    models.Customer.objects.filter(id=cid, active=1).update(active=0)
    res = BaseResponse(status=True)
    return JsonResponse(res.dict)


class ChargeModelForm(BootStrapForm, forms.ModelForm):
    # 静态变量
    charge_type = forms.TypedChoiceField(
        label="类型",
        choices=[(1, "充值"), (2, "扣款")],  # 只适合固定的数据，不适合去数据表中数据
        coerce=int
    )

    class Meta:
        model = models.TransactionRecord
        fields = ['charge_type', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields['charge_type'].choices = [(1, "充值"), (2, "扣款")]  # 只适合固定的数据，不适合去数据表中数据
        # self.fields['creator'].choices = models.Administrator.objects.filter(id__gt=1).values_list("id", 'username')


def customer_charge(request, pk):
    """ 交易记录列表 """

    queryset = models.TransactionRecord.objects.filter(customer_id=pk, customer__active=1, active=1).select_related(
        'customer').order_by('-id')
    pager = Pagination(request, queryset)

    form = ChargeModelForm()
    # return render(request, 'customer_charge.html', {"pager": pager, "form": form, 'pk': pk})
    return render(request, 'customer_charge.html', locals())


def customer_charge_add(reqeust, pk):
    form = ChargeModelForm(data=reqeust.POST)
    if not form.is_valid():
        return JsonResponse({'status': False, 'detail': form.errors})

    # 如果校验成功
    amount = form.cleaned_data['amount']
    charge_type = form.cleaned_data['charge_type']
    from django.db import transaction
    try:
        with transaction.atomic():
            # 1.对当前操作的客户进行更新操作，账户余额：增加、减少 + 锁
            cus_object = models.Customer.objects.filter(id=pk, active=1).select_for_update().first()

            if charge_type == 2 and cus_object.balance < amount:
                return JsonResponse(
                    {'status': False, 'detail': {"amount": ["余额不足，账户总余额只有:{}".format(cus_object.balance)]}})

            if charge_type == 1:
                cus_object.balance = cus_object.balance + amount
            else:
                cus_object.balance = cus_object.balance - amount
            cus_object.save()

            # 2.交易记录
            form.instance.customer = cus_object
            form.instance.creator_id = reqeust.nb_user.id
            form.save()

    except Exception as e:
        return JsonResponse({'status': False, 'detail': {"amount": ["操作失败"]}})

    return JsonResponse({'status': True})
