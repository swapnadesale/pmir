# -*- coding:utf-8 -*-
from django import template

register = template.Library()
#
#获得城市列表
#
@register.filter(name='get_city_list')
def get_city_list(locations, id):
    return locations[id]['cities']

