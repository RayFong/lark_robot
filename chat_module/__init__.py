from . import chatter
from . import guess_idiom
from . import douban
from . import podcast

Modules = [
    guess_idiom.GuessIdiomModule(),
    douban.DoubanModule(),
    podcast.PodcastModule(),

    ## 默认聊天
    chatter.ChatterModule(),
]
