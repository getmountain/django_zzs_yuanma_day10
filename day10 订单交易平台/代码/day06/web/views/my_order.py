from django.shortcuts import render, redirect
from django import forms
from django.core.exceptions import ValidationError
from web import models
from utils.pager import Pagination
from utils.bootstrap import BootStrapForm
import datetime
import random
from django.db.models import F
from django_redis import get_redis_connection
from django.conf import settings
from django.db import transaction


def my_order_list(request):
    # 获取我的订单，当前登录的客户id
    queryset = models.Order.objects.filter(customer_id=request.nb_user.id, active=1).order_by('-id')
    pager = Pagination(request, queryset)
    return render(request, 'my_order_list.html', {"pager": pager})


class MyOrderModelForm(BootStrapForm, forms.ModelForm):
    class Meta:
        model = models.Order
        fields = ["url", 'count']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        price_count_list = []
        text_count_list = []
        queryset = models.PricePolicy.objects.all().order_by('count')
        for item in queryset:
            unit_price = item.price / item.count
            price_count_list.append([item.count, ">={} ¥{}/条".format(item.count, unit_price), unit_price])

            text_count_list.append(">={} ¥{}/条".format(item.count, unit_price))

        if text_count_list:
            self.fields['count'].help_text = "、".join(text_count_list)
        else:
            self.fields['count'].help_text = "请联系管理员设置价格"

        self.price_count_list = price_count_list

    def clean_count(self):
        count = self.cleaned_data['count']
        if not self.price_count_list:
            raise ValidationError("请联系管理员设置价格")

        min_count_limit = self.price_count_list[0][0]
        if count < min_count_limit:
            raise ValidationError("最低支持数量为:{}".format(min_count_limit))
        return count


def my_order_add(request):
    if request.method == "GET":
        form = MyOrderModelForm()
        return render(request, 'form.html', {"form": form})

    form = MyOrderModelForm(data=request.POST)
    if not form.is_valid():
        return render(request, 'form.html', {"form": form})

    # 获取到  url 和 count
    video_url = form.cleaned_data['url']
    count = form.cleaned_data['count']

    # 0.获取原播放
    from utils.video import get_old_view_count
    status, old_view_count = get_old_view_count(video_url)
    if not status:
        form.add_error('url', "视频原来播放获取失败")
        return render(request, 'form.html', {"form": form})

    # 1.根据数量获取单价，计算出原价
    for idx in range(len(form.price_count_list) - 1, -1, -1):
        limit_count, _, unit_price = form.price_count_list[idx]
        if count >= limit_count:
            break
    total_price = count * unit_price
    print(total_price, type(total_price))

    # 2.当前客户的级别，根据级别计算折扣后的价格
    try:
        with transaction.atomic():
            cus_object = models.Customer.objects.filter(id=request.nb_user.id).select_for_update().first()
            real_price = total_price * cus_object.level.percent / 100
            print(real_price, type(real_price))

            # 3.判断账户余额够不够
            print(cus_object.balance, type(cus_object.balance))
            if cus_object.balance < real_price:
                form.add_error('count', "账户余额不足")
                return render(request, 'form.html', {"form": form})

            # 4.创建订单
            # 4.1 生成订单号
            while True:
                rand_number = random.randint(10000000, 99999999)
                ctime = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                oid = "{}{}".format(ctime, rand_number)
                exists = models.Order.objects.filter(oid=oid).exists()
                if exists:
                    continue
                break

            # 4.2 爬虫，发送网络请求获取原播放
            # 4.3 客户ID=当前登录用客户的ID

            form.instance.oid = oid
            form.instance.price = total_price
            form.instance.real_price = real_price
            form.instance.old_view_count = old_view_count
            form.instance.customer_id = request.nb_user.id
            form.save()

            # 5.客户账户扣款
            models.Customer.objects.filter(id=request.nb_user.id).update(balance=F("balance") - real_price)
            # cus_object.balance = cus_object.balance - real_price
            # cus_object.save()

            # 6.生成交易记录
            models.TransactionRecord.objects.create(
                charge_type=3,
                customer_id=request.nb_user.id,
                amount=real_price,
                order_oid=oid
            )

            # 7.写入队列 redis（redis启动，django连接redis）
            conn = get_redis_connection("default")
            conn.lpush(settings.QUEUE_TASK_NAME, oid)
    except Exception as e:
        form.add_error('count', "创建订单失败")
        return render(request, 'form.html', {"form": form})

    return redirect('/my/order/list/')


def my_order_cancel(reqeust, pk):
    """ 撤单"""
    # 。。。。
    return redirect('/my/order/list/')
