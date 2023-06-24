from django.shortcuts import render, redirect
from web import models
from django import forms
from django.urls import reverse
from utils.bootstrap import BootStrapForm


class LevelForm(BootStrapForm, forms.Form):
    title = forms.CharField(
        label="标题",
        required=True,
    )
    percent = forms.CharField(
        label="折扣",
        required=True,
        help_text="填入0-100整数表示百分比，例如：90，表示90%"
    )


class LevelModelForm(BootStrapForm, forms.ModelForm):

    # confirm_percent = forms.CharField(label="确认")

    class Meta:
        model = models.Level
        fields = ['title', 'percent']


def level_list(request):
    queryset = models.Level.objects.filter(active=1)
    return render(request, 'level_list.html', {"queryset": queryset})


def level_add(request):
    if request.method == "GET":
        form = LevelModelForm()
        return render(request, 'form.html', {"form": form})

    form = LevelModelForm(data=request.POST)
    if not form.is_valid():
        return render(request, 'form.html', {"form": form})

    # {'title': '1', 'percent': 2, 'confirm_percent': '3'}
    print(form.cleaned_data)
    # form.instance.percent = 10
    form.save()

    return redirect(reverse('level_list'))


def level_edit(request, pk):
    level_object = models.Level.objects.filter(id=pk, active=1).first()

    if request.method == "GET":
        form = LevelModelForm(instance=level_object)
        return render(request, 'form.html', {"form": form})

    form = LevelModelForm(data=request.POST, instance=level_object)
    if not form.is_valid():
        return render(request, 'form.html', {"form": form})

    # form.instance.percent = 10
    form.save()
    # return redirect(reverse('level_list'))
    from utils.link import filter_reverse
    return redirect(filter_reverse(request, "/level/list/"))

def level_delete(request, pk):

    exists = models.Customer.objects.filter(level_id=pk).exists()
    if not exists:
        models.Level.objects.filter(id=pk).update(active=0)
    return redirect(reverse('level_list'))
