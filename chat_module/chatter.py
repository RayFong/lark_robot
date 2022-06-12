import random

def handle_chatter(content):
    if '小可爱' in content:
        return random.choice(['小可爱在努力学习','小可爱在摸鱼','小可爱在研究小机器人呢','小可爱不睡觉觉了']) 

    if '可爱' in content:
        return '我就是这么可爱嘻嘻嘻'

    if '囡囡' in content:
        return '叫囡囡干嘛？'

    if '小哥哥' in content:
        return '小哥哥咋这么厉害！'

    if ('想你' in content) or ('想小可爱'in content):
        return '快到小可爱身边来！'
    
    if ('笨' in content) or  ('傻' in content):
        return '你才是大笨蛋'

    if '是' in content:
        return '可不是嘛'

    if '不' in content:
        return '没错，就是这样' 

    return random.choice(['小机器人笨笨滴..'])


class ChatterModule:
    def __init__(self):
        pass

    def Handle(self, content, **kvargs):
        return handle_chatter(content)

