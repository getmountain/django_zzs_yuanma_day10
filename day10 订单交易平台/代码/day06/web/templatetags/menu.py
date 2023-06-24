from django.http import QueryDict
from django.template import Library, TemplateSyntaxError
from django.conf import settings
import copy

from django.template.base import kwarg_re

register = Library()


@register.inclusion_tag("tag/nb_menu.html")
def nb_menu(request):
    # 1.读取当前用户的角色信息
    # print(request.nb_user.role)

    # 2.菜单信息
    user_menu_list = copy.deepcopy(settings.NB_MENU[request.nb_user.role])

    for item in user_menu_list:
        # item['class'] = 'hide'
        for child in item['children']:
            # if child['url'] == request.path_info: # v1版
            if child['name'] == request.nb_user.menu_name:
                child['class'] = 'active'
                # item['class'] = ""

    return {'menu_list': user_menu_list}

