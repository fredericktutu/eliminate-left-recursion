class Rule:
    def __init__(self, line, lan):
        self.name, self.exprs = self.parse(line)
        self.count = len(self.exprs)
        self.lan = lan

    def parse(self, line):
        name = line[0]
        exprs_Str = line[2:].split("|")
        exprs = [Expr(e) for e in exprs_Str]
        return name,exprs
    
    def combine_leftFac(self):
        matchTab = {}
        for i in range(self.count):
            for j in range(i+1, self.count):
                pre = self.exprs[i].match(self.exprs[j])
                if pre:
                    if pre in matchTab:
                        matchTab[pre].append(self.exprs[j])
                    else:
                        matchTab[pre] = [self.exprs[i],self.exprs[j]]
        #print("maxtab:" , matchTab)
        if matchTab: #有东西
            maxpre = max(matchTab, key=lambda x:len(x))
            #print("maxpre：" + maxpre)
            maxlen = len(maxpre)
            hinds = [i.str[maxlen:] if i.str[maxlen:] else "@" for i in matchTab[maxpre]]
            sym = self.lan.newSymbol()
            newLine = sym + "=" + "|".join(hinds)
            #print(newLine)
            self.lan.addRule(newLine)
            self.addExpr(Expr(maxpre + sym))
            for s in [i.str for i in matchTab[maxpre]]:
                self.delExpr(s)

    def eliminate_directRec(self):
        directRec = [e for e in self.exprs if e.first == self.name]
        if directRec: #如果存在自身左递归那么做接下来的
            others = [e for e in self.exprs if e.first != self.name] #把表达式中第一个不是自身的找出来
            #之前我以为是单个小写字母才可以，理解错了
            sym = self.lan.newSymbol()
            for o in others:
                if o.epsilon:
                    o.reBuild(sym)
                else:
                    o.reBuild(o.str + sym) #把这些式子都改成了βA'
            newLine = sym + "=" + "|".join([e.second + sym for e in directRec] + ["@"])
            self.lan.addRule(newLine)
            for d in directRec:
                self.delExpr(d.str)
        
    def addExpr(self, exp):
        assert isinstance(exp, Expr)
        self.exprs.append(exp)
        self.count += 1

    def delExpr(self, str):
        for i in range(self.count):
            if self.exprs[i].str == str:
                self.exprs.pop(i)
                self.count -= 1
                break

    def matchExprByFirst(self, first):
        #return the Expr instances
        res = []
        for i in range(self.count):
            if self.exprs[i].first == first:
                res.append(self.exprs[i])
        return res

class Language:
    def __init__(self):
        self.rules = []
        self.count = 0
        self.table = {}
        for i in [chr(i) for i in range(65, 91)]:
            self.table[i] = True
    def newSymbol(self):
        for i in self.table:
            if self.table[i]:
                self.table[i] = False
                return i 
        raise Exception("no more symbol!")

    def combine_leftFac(self):
        for r in [_ for _ in self.rules]:
            r.combine_leftFac()

    def eliminate_directRec(self):
        for r in [_ for _ in self.rules]: #复制一份旧的，以免有新增的
            r.eliminate_directRec()


    def eliminate_leftRec(self):
        #for i in range(self.count):
        i = 0
        while i < self.count:
            rule1 = self.rules[i]
            if i == 0:
                rule1.eliminate_directRec()
            for j in range(i):
                rule2 = self.rules[j]
                for e in [_ for _ in rule1.exprs]: #同样，由于exprs会被改变，因此我们保留一份旧的记录
                    if e.FirstIsRule(rule2):
                        lst = e.replace_All(rule2)
                        for el in lst:
                            rule1.addExpr(el) #加入替换后的规则
                        rule1.delExpr(e.str) #删除旧的规则
                rule1.eliminate_directRec()
            i += 1


    def addRule(self, line):  #我们使用language的addRule来读入一个line，转化成Rule
        newRule = Rule(line, self)
        self.table[newRule.name] = False
        self.rules.append(newRule)
        self.count += 1
        return newRule

    def showRules(self):
        for rule in self.rules:
            print(rule.name + "=" + "|".join([e.str for e in rule.exprs]))

    def getRuleByName(self, name):
        for i in range(self.count):
            if self.rules[i].name == name:
                return self.rules[i] #return this rule, a rule with one name is unique


class Expr:
    def __init__(self, Expr_Str):
        self.str = Expr_Str
        self.first = Expr_Str[0]
        self.second = Expr_Str[1:]
        self.leftR = True if 'A' <= self.first <= 'Z' else False
        self.atom = bool(not self.leftR and len(self.str) == 1 and self.first != '@')
        self.epsilon = self.first == "@"
    def replace(self, expr2):
        newStr = expr2.str + self.second
        newExpr = Expr(newStr)
        return newExpr

    def reBuild(self, Expr_Str):
        self.str = Expr_Str
        self.first = Expr_Str[0]
        self.second = Expr_Str[1:]
        self.leftR = True if 'A' <= self.first <= 'Z' else False
        self.atom = bool(not self.leftR and len(self.str) == 1 and self.first != '@')
        self.epsilon = self.first == "@"

    def FirstIsRule(self, rule):
        if self.leftR and rule.name == self.first:
            return True
        return False
    def replace_All(self, rule):
        if self.FirstIsRule(rule):
            return [self.replace(expr2) for expr2 in rule.exprs]
        return []
    def match(self, expr2):
        res = ""
        for i in range(min(len(self.str),len(expr2.str))):
            if self.str[i] == expr2.str[i]:
                res += self.str[i]
            else:
                break
        return res

def main():
    l = Language()
    print("<自动消除左递归>")
    print("请逐行输入文法，最后一行输入';'以表示文法结束")
    while True:
        oneLine = input()
        if oneLine == ";":
            break
        l.addRule(oneLine)
    print("你输入的文法是：")
    l.showRules()
    print("--------------------")
    print("提取一次公共前缀的结果是：")
    l.combine_leftFac()
    l.showRules()
    print("--------------------")
    print("消除左递归的结果是：")
    l.eliminate_leftRec()
    l.showRules()
    print("--------------------")