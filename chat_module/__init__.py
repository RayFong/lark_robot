from . import chatter
from . import guess_idiom
from . import douban

Modules = [
    guess_idiom.GuessIdiomModule(),
    douban.DoubanModule(),

    ## 默认聊天
    chatter.ChatterModule(),
]
