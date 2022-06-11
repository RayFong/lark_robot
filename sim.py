import math
import json
import random

debug = False

def jaccard(s1 : str, s2 : str) -> float:
    '''
        |A & B| / (A + B - |A & B|)
    '''
    if len(s1) == 0 or len(s2) == 0:
        return 0
    
    t1, t2 = set(s1), set(s2)
    intersection = t1 & t2
    return len(intersection) / (len(t1) + len(t2) - len(intersection))

def sorensenDice(s1 : str, s2 : str) -> float:
    '''
        2|A & B| / (A + B)
    '''
    if len(s1) == 0 or len(s2) == 0:
        return 0
    
    t1, t2 = set(s1), set(s2)
    intersection = t1 & t2
    return 2 * len(intersection) / (len(t1) + len(t2))

def cos(s1: str, s2: str) -> float:
    def to_words(s):
        return s
        # import jieba
        # return jieba.lcut(s)

    w1, w2 = to_words(s1), to_words(s2)

    total_words = {v: idx for idx, v in enumerate(list(set(w1) | set(w2)))}
    def to_vec(words):
        v = [0] * len(total_words)
        for  w in words:
            if w in total_words:
                v[total_words[w]] += 1
        return v

    v1, v2 = to_vec(w1), to_vec(w2)
    dot = sum([i * j for i, j in zip(v1, v2)])
    v1Len = math.sqrt(sum([i*i for i in v1]))
    v2Len = math.sqrt(sum([j*j for j in v2]))

    return dot/(v1Len*v2Len)


class Question:
    def __init__(self, scene, question, answer, index):
        self.scene, self.question, self.answer, self.index = scene, question, answer, index

    def __str__(self):
        return f'<{self.scene}-{self.index}> {self.question}: {self.answer}'


class QuestionWithScore(Question):
    def __init__(self, base: Question, score: float):
        Question.__init__(self, base.scene, base.question, base.answer, base.index)
        self.score = score

    def __str__(self):
        return f'{self.question}: {self.answer}, scene=<{self.scene}-{self.index}>, score={self.score:.2f}'


class QuestionRepository:
    def __init__(self):
        self.questions = []
        self.simFunc = cos


    def load(self, filename):
        with open(filename) as fp:
            data = json.load(fp)
        
        for singleScene in data:
            scene = singleScene['S']
            for idx, chat in enumerate(singleScene['C']):
                q, a = chat['Q'], chat['A']
                self.questions.append(Question(scene, q, a, idx))


    def match(self, query, highSimThreshold=0.6, topK=10, minSimThreshold=0.25):
        # 返回list<QuestionWithScore>
        #   所有>0.5相似度的, 如果小于10个，再加上>0的top 10个
        candidates = []
        for q in self.questions:
            score = self.simFunc(query, q.question)
            if score > minSimThreshold:
                candidates.append(QuestionWithScore(q, score))

        candidates.sort(key=lambda x : -x.score)

        if len(candidates) <= topK or candidates[-1].score >= highSimThreshold:
            return candidates
        
        endIndex = 0
        for idx, c in enumerate(candidates):
            if c[1] < highSimThreshold:
                endIndex = idx
                break
        if endIndex < topK:
            endIndex = topK
        return candidates[:endIndex]


class Robot:
    def __init__(self, repo: QuestionRepository):
        self.repo = repo
        self.defaultCandidateAnswer = ['小机器人笨笨的', "太为难小机器人了", '小机器人还要再努力努力']
        self.last_candidate, self.last_query = None, None

    def _extract_subject(self, query):
        for s in ['小可爱', '囡囡']:
            if s in query:
                return '小可爱'
        
        for s in ['小哥哥']:
            if s in query:
                return '小哥哥'

        return '小机器人'


    def _split_by_scene(self, query, candidates):
        same_scene_candidates, other_candidates = [], []
        for c in candidates:
            if c.scene == self.last_candidate.scene:
                same_scene_candidates.append(c)
            else:
                other_candidates.append(c)
        return same_scene_candidates, other_candidates


    def _is_same_scene(self, query):
        '''
            判断是否在同一个场景中
        '''
        if self.last_candidate is None:
            return False
        return self._extract_subject(self.last_candidate.question) == self._extract_subject(query)


    def _filter_highest_score(self, candidates):
        return list(filter(lambda c: c.score == candidates[0].score, candidates))


    def _answer_by_candidates(self, query, candidates):
        if self.last_candidate is None:
            return random.choice(self._filter_highest_score(candidates))

        if not self._is_same_scene(query):
            return random.choice(self._filter_highest_score(candidates))

        same_scene_candidates, other_candidates = self._split_by_scene(query, candidates)
        if same_scene_candidates:
            for c in same_scene_candidates:
                if c.index > self.last_candidate.index:
                    return c
            return random.choice(self._filter_highest_score(same_scene_candidates))

        if other_candidates:
            return random.choice(self._filter_highest_score(other_candidates))

        return None

    def _is_same_query(self, query):
        if self.last_candidate is not None and self.last_candidate.question == query:
            return True
        
        return self.last_query == query


    def answer(self, query) -> str:
        if self._is_same_query(query):
            return random.choice(['你问的是一样的问题, 你在欺负小机器人', '你在欺负小机器人，不和你说了'])
        self.last_query = query

        candidates = self.repo.match(query)
        if not candidates:
            # 没有匹配到任意一个，随机返回一个
            return random.choice(self.defaultCandidateAnswer)

        if debug:
            print(query, ':', '\n\t'+'\n\t'.join([str(c) for c in candidates]))

        candidate = self._answer_by_candidates(query, candidates)
        if candidate:
            self.last_candidate = candidate
            if isinstance(candidate.answer, list):
                return random.choice(candidate.answer)
            elif isinstance(candidate.answer, str):
                return candidate.answer
            else:
                print('unknow answer:', candidate.answer)
        
        # fallback
        return random.choice(self.defaultCandidateAnswer)


if __name__ == '__main__':
    debug = True
    repo = QuestionRepository()
    repo.load('chat.json')
    robot = Robot(repo)
    print(robot.answer('小可爱在干嘛'))
    print(robot.answer('小可爱在干嘛'))
    print(robot.answer('小哥哥在干嘛'))
    print(robot.answer('小可爱在学习嘛'))
    print(robot.answer('你好可爱啊'))
    print(robot.answer('你好笨啊'))
    print(robot.answer('你这都懂啊'))
    print(robot.answer('听不懂'))

