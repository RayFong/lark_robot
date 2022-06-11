import json, random

def onset_num(word):
    for c in ['zh', 'ch', 'sh']:
        if word.startswith(c):
            return 2
    for c in ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'r', 'x', 'w', 'y', 'z', 'c', 's']:
        if word.startswith(c):
            return 1
    return 0

def parse_idiom(idiom_pinyin): # 把输入的拼音拆开
    words = [w.strip() for w in idiom_pinyin.strip().split()]
    pinyin_list = []
    for word in words:
        n = onset_num(word)
        pinyin_list.append((word[:n], word[n:-1], word[-1]))

    return pinyin_list

def guess(idiom_list, guess_idiom, guess_result):
    # guess_idiom: [拼音_音调]，音调1234
    # guess_result: 3种状态3个位置，状态：0-没有该项,1-完全正确，2-存在但位置不对，3-不存在，位置：1-声母，2-韵母，3-音调，如123 321 123 212
    guess_pinyin_list = parse_idiom(guess_idiom) # 猜的拼音拆开来
    pinyin_results = [r.strip() for r in guess_result.strip().split()] # 332这种的四个元素的列表
    must_exist, possible_exist = {}, {}
    for idx, single_result in enumerate(pinyin_results): # idx是第几个字， single_result是332这种
        g = guess_pinyin_list[idx] # 第几个字的拼音的拆开来
        for label, v in enumerate(single_result): # label是声母还是韵母还是音调，v是正确与否
            if v == '0':
                continue
            if v == '1':
                must_exist[(idx, label)] = g[label] # must_exist[(idx第几个字, label声母还是韵母还是音调)] = g[label]第几个字的拼音的声母还是韵母还是音调是什么
            else:
                key = (label, g[label])
                diff = 1 if v == '2' else 0
                upper = v == '3'
                if key in possible_exist:
                    v = possible_exist[key]
                    v[1].append(idx)
                    possible_exist[key] = (v[0]+diff, v[1], v[-1] or upper)  # (多少个, 不存在的地方, 上限)
                else:
                    possible_exist[key] = (diff, [idx], upper)

    def match(idiom):
        for (idx, label), val in must_exist.items():
            if idiom[idx][label] != val and idiom[idx][label] != '0':
                return False
        
        for (label, val), (total, exclude, upper) in possible_exist.items():
            hasCount = 0
            for idx, word in enumerate(idiom):
                if pinyin_results[idx][label] == '1':
                    continue

                if word[label] != val and word[label] != '0':
                    continue

                if idx in exclude:
                    return False
                
                hasCount += 1
            if (upper and hasCount != total) or (not upper and hasCount < total):
                return False

        return True

    return [idiom for idiom in idiom_list if match(idiom[-1])]


class IdiomGuesser:
    def __init__(self, path='idioms_new.json', candidate_num=30):
        self._load(path)
        self.lastCandidate = None
        self.guessing = False
        self.nextCursor = 0
        self.candidate_num = candidate_num
    

    def _load(self, path):
        with open(path) as fp:
            self.idiomMap = json.load(fp)
            self.idioms = [(k, v, parse_idiom(v)) for k, v in self.idiomMap.items()]
            print('invalid idioms:', [i[v] for i in self.idioms if len(i[-1]) != 4])
            self.idioms = [i for i in self.idioms if len(i[-1]) == 4]


    def startNewGuess(self):
        self.guessing = True
        self.lastCandidate = self.idioms


    def isGuessing(self):
        return self.guessing


    def guess(self, guess_idiom, guess_result):
        self.lastCandidate = guess(self.lastCandidate, guess_idiom, guess_result)
        self.guessing = len(self.lastCandidate) > 1
        random.shuffle(self.lastCandidate)
        self.nextCursor = 0
        return self.moreCandidate()


    def moreCandidate(self):
        result = self.lastCandidate[self.nextCursor:self.nextCursor+self.candidate_num]
        self.nextCursor += self.candidate_num
        return [r[0] for r in result]


if __name__ == '__main__':
    with open('./idioms_new.json') as fp:
        idiomMap = json.load(fp)
        idioms = [(k, v, parse_idiom(v)) for k, v in idiomMap.items()]

    guesser = IdiomGuesser('./idioms_new.json')
    guesser.startNewGuess()
    while guesser.isGuessing():
        guess_idiom = input('猜测的成语拼音:')
        guess_result = input('结果:')
        result = guesser.guess(guess_idiom, guess_result)
        print(f'总共有{len(guesser.lastCandidate)}个，任意推荐30个：', result)
    print('results: ', [c[0] for c in guesser.lastCandidate])

