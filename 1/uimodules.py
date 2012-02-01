#coding=utf-8
__author__ = 'vfasky'

import tornado.web

'''
分页条
'''
class Pagination(tornado.web.UIModule):
    def render(self, pagination, url=None, key='page', maxItem=10):
        if not url:
            url = self.request.path

        if url.find('?') != -1:
            link = url + '&' + key + '='
        else:
            link = url + '?' + key + '='

        list = []
        if pagination['countPage'] > maxItem:
            import math

            # 左右个数
            itemCount = int(math.floor((maxItem - 3) / 2))




            # 开头
            list.append({'name': '1', 'class': '', 'url': link + '1'})

            pageCount = pagination['countPage'] > itemCount and  itemCount or pagination['countPage']
            # 确定起始号码;
            pageBegin = ( pagination['current'] - itemCount ) < 2 and  2 or ( pagination['current'] - itemCount )
            pageEnd = ( pagination['current'] + itemCount ) > pagination['countPage'] and  pagination['countPage'] or (
                pagination['current'] + itemCount )

            if pageEnd < maxItem:
                pageEnd = maxItem

            if pageBegin != 2:
                list.append({'name': '...', 'class': 'disabled', 'url': '#'})

            for i in range(pageBegin, pageEnd + 1):
                list.append({'name': str(i), 'class': '', 'url': link + str(i)})

            if pageEnd < pagination['countPage']:
                list.append({'name': '...', 'class': 'disabled', 'url': '#'})
                list.append(
                        {'name': str(pagination['countPage']), 'class': '', 'url': link + str(pagination['countPage'])})
        else:
            for i in range(1, int(pagination['countPage']) + 1):
                list.append({'name': str(i), 'class': '', 'url': link + str(i)})
        return self.render_string("module/pagination.html", pagination=pagination, list=list, link=link)