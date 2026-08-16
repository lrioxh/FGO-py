# Stars  Cosmos Gods  Animus    Antrum       Unbirth    Anima Animusphere
# 星の形.宙の形.神の形.我の形.天体は空洞なり.空洞は虚空なり.虚空には神ありき.
# 地を照らし,空に在り,天上の座標を示せ.
# カルディアの灯よ.
# どうか今一度,旅人の標とならん事を.
# ここで,Bgo運営の敗北を宣言する!
# .        OO---O---O-o\
# .       // \ / \ / \ \\
# .      OO   O   O   O \\
# .     // \   \ /   / \ \\
# .    oO---O---O---O---O-Oo
# .     \\ /   / \   \ / //
# .      \O   O   O   O //
# .       \\ / \ / \ / //
# .        oO---O---Oo-O
# .             ^^
# .  Grand Order/Anima Animusphere
# .     冠位指定/人理保障天球
'Full-automatic FGO Script'
from fgoConst import VERSION
__version__=VERSION
__author__='hgjazhgj'
import logging,numpy,pulp,random,re,time,threading
import fgoDevice
from itertools import permutations
from functools import wraps
from fgoDetect import Detect,XDetect
from fgoFuse import fuse
from fgoImageListener import ImageListener
from fgoLogging import getLogger,logit
from fgoMetadata import servantData,missionMat,missionTag,missionQuest
from fgoReishift import reishift
from fgoSchedule import ScriptStop,schedule
logger=getLogger('Kernel')
servantSkillOrder={444:(1,2,0)}
storySkip=False

def configure(key,value):
    global storySkip
    match key:
        case'storySkip':
            storySkip=bool(value)
            return storySkip
        case'friendSearchMaxCycles':
            value=int(value)
            if value<1:raise ValueError('friendSearchMaxCycles must be positive')
            Main.friendSearchMaxCycles=value
            return value
        case'friendAllTab':
            Next.friendAllTab=bool(value)
            return Next.friendAllTab
        case'autoFormation':
            Next.autoFormation=bool(value)
            return Next.autoFormation
        case _:return value

friendImg=ImageListener('fgoImage/friend/')
mailImg=ImageListener('fgoImage/mail/')
mutex=threading.Lock()
friendSelectionActive=threading.Event()

def serialize(lock):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            with lock:return func(*args,**kwargs)
        return wrapper
    return decorator
def guardian():
    logger=logging.getLogger('Guardian')
    prev=None
    while True:
        cache=Detect.cache
        while cache is prev:
            time.sleep(3)
            cache=Detect.cache
        if cache.isSupportFormationCondition():
            logger.info('Close Support Formation Condition')
            fgoDevice.device.touch((640,601))
        elif (
            not friendSelectionActive.is_set()
            and not cache.isChooseFriend()
            and cache.isGameTapPrompt()
        ):
            logger.info('Tap Game Screen')
            fgoDevice.device.press(' ')
        elif cache.isNetworkError():
            logger.warning('Reconnecting')
            fgoDevice.device.press('K')
        prev=cache
threading.Thread(target=guardian,daemon=True,name='Guardian').start()

def openCardSelection(maxUnknownFrames=10):
    fgoDevice.device.perform(' ',(2100,))
    unknownFrames=0
    while unknownFrames<maxUnknownFrames:
        detect=Detect(0,.3)
        if detect.isCardSelection():return
        if detect.isSkillCastFailed():
            logger.warning('Close Skill Cast Failed Before Card Selection')
            fgoDevice.device.press('J')
            schedule.sleep(1)
            unknownFrames=0
        elif detect.isTurnBegin():
            logger.warning('Card Selection Not Opened, Retry Attack')
            fgoDevice.device.perform(' ',(1000,))
            unknownFrames=0
        else:unknownFrames+=1
    raise ScriptStop('Card Selection Not Detected')

class Farming:
    def __init__(self):
        self.logger=getLogger('Farming')
        self.stop=False
    def __call__(self):
        time.sleep(100)
        while not self.stop:
            if not fgoDevice.device.available:continue
            time.sleep(self.run()+30)
    @serialize(mutex)
    def run(self):
        from fgoFarming import farming
        try:
            return farming()
        except Exception as e:
            logger.exception(e)
            return 0
farming=Farming()
threading.Thread(target=farming,daemon=True,name='Farming').start()
def setup():
    raise NotImplementedError
    if not fgoDevice.device.isInGame():
        fgoDevice.device.launch()
        while not Detect(1).isGameLaunch():pass
        while not Detect(1).isGameAnnounce():fgoDevice.device.press('\xBB')
        fgoDevice.device.press('\x08')
    elif False:...
@serialize(mutex)
def fpSummon():
    while fuse.value<30:
        if Detect().isFpContinue():fgoDevice.device.perform('MK',(600,2700))
        fgoDevice.device.press('\x08')
@serialize(mutex)
def lottery():
    Detect().setupLottery()
    count=0
    while(count:=0 if Detect().isLotteryContinue()else count+1)<5:
        for _ in range(random.randint(10,100)):fgoDevice.device.press('2')
# @serialize(mutex)
# def mining():
#     while fuse.value<30:
#         if Detect().isMining():fgoDevice.device.perform('K',(300,))
#         fgoDevice.device.perform('9Z',(300,300))
@serialize(mutex)
def mail():
    assert mailImg.flush()
    Detect().setupMailDone()
    while True:
        while any((pos:=Detect.cache.findMail(i[1]))and(fgoDevice.device.touch(pos),True)[-1]for i in mailImg.items()):
            while not Detect().isMailDone():pass
        fgoDevice.device.swipe((400,600),(400,200))
        if Detect().isMailListEnd():break
@serialize(mutex)
def synthesis():
    while True:
        fgoDevice.device.perform('8',(1000,))
        for i,j in((i,j)for i in range(4)for j in range(7)):fgoDevice.device.touch((133+133*j,253+142*i),100)
        if Detect().isSynthesisFinished():break
        fgoDevice.device.perform('  KK\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB\xBB',(800,300,300,1000,150,150,150,150,150,150,150,150,150,150,150,150,150,150,150))
        while not Detect().isSynthesisBegin():fgoDevice.device.press('\xBB')
@serialize(mutex)
def dailyFpSummon():
    while not Detect(0,1).isMainInterface():pass
    fgoDevice.device.perform(' Z',(500,2000))
    while not Detect(.5).isMainInterface():pass
    while not Detect(1.5).isFpSummon():fgoDevice.device.press('\xBC')
    fgoDevice.device.perform('JJ',(800,3000))
    while not Detect(.5).isFpContinue():fgoDevice.device.press(' ')
    fgoDevice.device.perform('\x67\x67',(1200,5000))
@serialize(mutex)
def summonHistory():
    Detect().setupSummonHistory()
    while not Detect.cache.isSummonHistoryListEnd():
        fgoDevice.device.swipe((930,500),(930,200))
        Detect(.4).getSummonHistory()
    return{'type':'SummonHistory'}|dict(zip(('value','file'),Detect.cache.saveSummonHistory()))
@serialize(mutex)
def bench(times=20,touch=True,screenshot=True):
    if not(touch or screenshot):touch=screenshot=True
    screenshotBench=[]
    for _ in range(times*screenshot):
        begin=time.time()
        fgoDevice.device.screenshot()
        screenshotBench.append(time.time()-begin)
    touchBench=[]
    for _ in range(times*touch):
        begin=time.time()
        fgoDevice.device.press('\xBB')
        touchBench.append(time.time()-begin)
    return{
        'type':'Bench',
        'touch':(sum(touchBench)-max(touchBench)-min(touchBench))*1000/(times-2)if touch else None,
        'screenshot':(sum(screenshotBench)-max(screenshotBench)-min(screenshotBench))*1000/(times-2)if screenshot else None,
    }
@serialize(mutex)
def goto(quest):
    while not Detect(0,1).isMainInterface():pass
    fgoDevice.device.press(' ')
    fgoDevice.device.perform(*((' ',(600,))if Detect(.6).isTerminal()else('S',(1500,))))
    reishift(quest)
    schedule.sleep(.5)
    for _ in range(4):
        if Detect(.4).isQuestListBegin():break
        fgoDevice.device.swipe((1000,200),(1000,600))
    while not Detect(.4).isQuestFreeContains(quest[0]):fgoDevice.device.swipe((1000,600),(1000,200))
    while not Detect(.4).isQuestFreeFirst(quest[0]):fgoDevice.device.swipe((1000,395),(1000,300))
@serialize(mutex)
def weeklyMission():
    while not Detect(0,1).isMainInterface():pass
    fgoDevice.device.perform('B',(800,))
    while not Detect(.4).isWeeklyMission():pass
    fgoDevice.device.perform('2N',(100,1000))
    Detect().setupWeeklyMission()
    while not Detect.cache.isWeeklyMissionListEnd():
        fgoDevice.device.swipe((1000,600),(1000,300))
        Detect(.4).getWeeklyMission()
    x=[pulp.LpVariable('_'.join(str(j)for j in i),lowBound=0,cat=pulp.LpInteger)for i in missionQuest]
    prob=pulp.LpProblem('WeeklyMission',sense=pulp.LpMinimize)
    prob+=pulp.lpDot(missionMat[0],x)
    for count in(count for target,minion,count in Detect.cache.saveWeeklyMission()if(logger.info(f'Add [{"|".join(target)}],{minion},{count}')or True if(coefficient:=sum((j for i in target for j,k in zip(missionMat,missionTag)if i in k and(minion or'从者'in k)),numpy.zeros(missionMat.shape[1]))).any()else logger.error(f'Invalid Target [{"|".join(target)}],{minion},{count}'))):prob+=pulp.lpDot(coefficient,x)>=count
    prob.solve(pulp.PULP_CBC_CMD(msg=False))
    logger.info(f'AP: {prob.objective.value():.0f}')
    fgoDevice.device.press('\x67')
    return[(tuple(int(i)for i in v.name.split('_')),int(v.varValue))for v in prob.variables()if v.varValue]
class ClassicTurn:
    skillInfo=[[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]],[[0,0,0,7],[0,0,0,7],[0,0,0,7]]]
    houguInfo=[[1,7],[1,7],[1,7],[1,7],[1,7],[1,7]]
    masterSkill=[[0,0,0,7],[0,0,0,7],[0,0,0,0,7]]
    def __init__(self):
        ClassicTurn.friendInfo=[[[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1]],[-1,-1]]
        self.stage=0
        self.stageTurn=0
        self.servant=[0,1,2]
        self.orderChange=[0,1,2,3,4,5]
        self.countDown=[[[0,0,0],[0,0,0],[0,0,0]],[0,0,0]]
    def __call__(self,turn):
        self.stage,self.stageTurn=[t:=Detect(.2).getStage(),1+self.stageTurn*(self.stage==t)]
        self.friend=[Detect.cache.isServantFriend(i)for i in range(3)]
        if turn==1:
            Detect.cache.setupServantDead(self.friend)
            self.stageTotal=Detect.cache.getStageTotal()
            self.servant=[6 if self.servant[i]>=6 or Detect.cache.getFieldServantClassRank(i)is None else self.servant[i]for i in range(3)]
        else:
            for i in(i for i in range(3)if self.servant[i]<6 and Detect.cache.isServantDead(i,self.friend[i])):
                self.servant[i]=max(self.servant)+1
                self.countDown[0][i]=[0,0,0]
        logger.info(f'Turn {turn} Stage {self.stage} StageTurn {self.stageTurn} {self.servant}')
        if self.stageTurn==1:Detect.cache.setupEnemyGird()
        self.dispatchSkill()
        openCardSelection()
        fgoDevice.device.perform(self.selectCard(),(300,300,2300,1300,6000))
    def dispatchSkill(self):
        self.countDown=[[[max(0,j-1)for j in i]for i in self.countDown[0]],[max(0,i-1)for i in self.countDown[1]]]
        while(s:=[(self.getSkillInfo(i,j,3),0,(i,j))for i in range(3)if self.servant[i]<6 for j in range(3)if self.countDown[0][i][j]==0 and(t:=self.getSkillInfo(i,j,0))and min(t,self.stageTotal)<<8|self.getSkillInfo(i,j,1)<=self.stage<<8|self.stageTurn and Detect.cache.isSkillReady(i,j)]+[(self.masterSkill[i][-1],1,(i,))for i in range(3)if self.countDown[1][i]==0 and self.masterSkill[i][0]and min(self.masterSkill[i][0],self.stageTotal)<<8|self.masterSkill[i][1]<=self.stage<<8|self.stageTurn]):
            _,cast,arg=min(s,key=lambda x:x[0])
            [self.castServantSkill,self.castMasterSkill][cast](*arg)
            fgoDevice.device.perform('\x08',(700,))
            while not Detect().isTurnBegin():pass
            Detect(.5)
    @logit(logger,logging.INFO)
    def selectCard(self):return''.join((lambda hougu,sealed,color,resist,critical:(fgoDevice.device.perform('\x67\x68\x69\x64\x65\x66'[numpy.argmax([Detect.cache.getEnemyHp(i)for i in range(6)])],(500,))if any(hougu)or self.stageTurn==1 else 0,['678'[i]for i in sorted((i for i in range(3)if hougu[i]),key=lambda x:self.getHouguInfo(x,1))]+['12345'[i]for i in sorted(range(5),key=(lambda x:-color[x]*resist[x]*(not sealed[x])*(1+critical[x])))]if any(hougu)else(lambda group:['12345'[i]for i in(lambda choice:choice+tuple({0,1,2,3,4}-set(choice)))(logger.debug('cardRank'+','.join(('  'if i%5 else'\n')+f'({j}, {k:5.2f})'for i,(j,k)in enumerate(sorted([(card,(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*(1+critical[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not any(sealed[i]for i in card))*(4.8*colorChain+(firstCardBonus+1.)*(3 if colorChain else 1.8)*(len({group[i]for i in card})==1)*resist[card[0]]))(len({color[i]for i in card})==1,.3*(color[card[0]]==1.1)))for card in permutations(range(5),3)],key=lambda x:-x[1]))))or max(permutations(range(5),3),key=lambda card:(lambda colorChain,firstCardBonus:sum((firstCardBonus+[1.,1.2,1.4][i]*color[j])*(1+critical[j])*resist[j]*(not sealed[j])for i,j in enumerate(card))+(not any(sealed[i]for i in card))*(4.8*colorChain+(firstCardBonus+1.)*(3 if colorChain else 1.8)*(len({group[i]for i in card})==1)*resist[card[0]]))(len({color[i]for i in card})==1,.3*(color[card[0]]==1.1))))])(Detect.cache.getCardGroup()))[1])([self.servant[i]<6 and j and(t:=self.getHouguInfo(i,0))and self.stage>=min(t,self.stageTotal)for i,j in enumerate(Detect().isHouguReady())],Detect.cache.isCardSealed(),[[.8,1.,1.1][i]for i in Detect.cache.getCardColor()],[[1.,1.7,.6][i]for i in Detect.cache.getCardResist()],[i/10 for i in Detect.cache.getCardCriticalRate()]))
    def getSkillInfo(self,pos,skill,arg):return self.friendInfo[0][skill][arg]if self.friend[pos]and self.friendInfo[0][skill][arg]>=0 else self.skillInfo[self.orderChange[self.servant[pos]]][skill][arg]
    def getHouguInfo(self,pos,arg):return self.friendInfo[1][arg]if self.friend[pos]and self.friendInfo[1][arg]>=0 else self.houguInfo[self.orderChange[self.servant[pos]]][arg]
    def castServantSkill(self,pos,skill):
        fgoDevice.device.press(('ASD','FGH','JKL')[pos][skill])
        detect=Detect(.7)
        kukulkanChoice=detect.isKukulkanSkillChoice()
        if kukulkanChoice:
            logger.info('Select Kukulkan Skill Without Critical Stars')
            fgoDevice.device.touch((640,425),700)
            detect=Detect(.7)
        targetCount=detect.getSkillTargetCount()if kukulkanChoice else 0
        if targetCount:
            target=pos+1 if skill==1 else self.getSkillInfo(pos,skill,2)or 3
            fgoDevice.device.perform(
                ['3333','2244','3234'][targetCount-1][target],(300,)
            )
        elif detect.isSkillNone():
            logger.warning(f'Skill {pos} {skill} Disabled')
            self.countDown[0][pos][skill]=999
        elif detect.isSkillCastFailed():
            self.countDown[0][pos][skill]=1
            fgoDevice.device.press('J')
            schedule.sleep(1)
        elif t:=detect.getSkillTargetCount():
            target=self.getSkillInfo(pos,skill,2)or 3
            fgoDevice.device.perform(['3333','2244','3234'][t-1][target],(300,))
    def castMasterSkill(self,skill):
        self.countDown[1][skill]=15
        fgoDevice.device.perform('Q'+'WER'[skill],(300,300))
        if self.masterSkill[skill][2]:
            if skill==2 and self.masterSkill[2][3]:
                if self.masterSkill[2][2]-1 not in self.servant or self.masterSkill[2][3]-1 in self.servant:return fgoDevice.device.perform('\xBB',(300,))
                p=self.servant.index(self.masterSkill[2][2]-1)
                fgoDevice.device.perform(('TYUIOP'[p],'TYUIOP'[self.masterSkill[2][3]-max(self.servant)+1],'Z'),(300,300,2600))
                self.orderChange[self.masterSkill[2][2]-1],self.orderChange[self.masterSkill[2][3]-1]=self.orderChange[self.masterSkill[2][3]-1],self.orderChange[self.masterSkill[2][2]-1]
                fgoDevice.device.perform('\x08',(2300,))
                while not Detect().isTurnBegin():pass
                self.friend=[Detect(.5).isServantFriend(0),Detect.cache.isServantFriend(1),Detect.cache.isServantFriend(2)]
                Detect.cache.setupServantDead(self.friend)
            elif t:=Detect(.5).getSkillTargetCount():fgoDevice.device.perform(['3333','2244','3234'][t-1][self.masterSkill[skill][2]],(300,))
class Turn:
    def __init__(self):
        self.stage=0
        self.stageTurn=0
        self.countDown=[[[0,0,0],[0,0,0],[0,0,0]],[0,0,0]]
    def __call__(self,turn):
        self.stage,self.stageTurn=[t:=Detect(.2).getStage(),1+self.stageTurn*(self.stage==t)]
        if turn==1:
            Detect.cache.setupServantDead()
            self.stageTotal=Detect.cache.getStageTotal()
            self.servant=[(lambda x:(x,)+servantData.get(x,(0,0,0,0,(0,0),((0,0),(0,0),(0,0)))))(Detect.cache.getFieldServant(i))for i in range(3)]
        else:
            for i in(i for i in range(3)if Detect.cache.isServantDead(i)):
                self.servant[i]=(lambda x:(x,)+servantData.get(x,(0,0,0,0,(0,0),((0,0),(0,0),(0,0)))))(Detect.cache.getFieldServant(i))
                self.countDown[0][i]=[0,0,0]
        logger.info(f'Turn {turn} Stage {self.stage} StageTurn {self.stageTurn} {[i[0]for i in self.servant]}')
        if self.stageTurn==1:Detect.cache.setupEnemyGird()
        self.enemy=[Detect.cache.getEnemyHp(i)for i in range(6)]
        self.dispatchSkill()
        openCardSelection()
        fgoDevice.device.perform(self.selectCard(),(300,300,2300,1300,6000))
    def dispatchSkill(self):
        self.countDown=[[[max(0,j-1)for j in i]for i in self.countDown[0]],[max(0,i-1)for i in self.countDown[1]]]
        while skill:=[(0,i,j)for i in range(3)for j in servantSkillOrder.get(self.servant[i][0],range(3))if not self.countDown[0][i][j]and self.servant[i][0]and self.servant[i][6][j][0]and Detect.cache.isSkillReady(i,j)]: # +[(1,i)for i in range(3)if self.countDown[1][i]==0]:
            for i in skill:
                if i[0]==0:
                    match self.servant[i[1]][6][i[2]]:
                        case 1,_:
                            self.castServantSkill(i[1],i[2],i[1]+1)
                            continue
                        case 2,p:
                            np=[Detect.cache.getFieldServantNp(i)if self.servant[i][0]else 100 for i in range(3)]
                            match p:
                                case 0:
                                    if any(i<100 for i in np):
                                        self.castServantSkill(i[1],i[2],0)
                                        continue
                                case 1:
                                    target=numpy.argmin(np)
                                    if np[target]<100:
                                        self.castServantSkill(i[1],i[2],target+1)
                                        continue
                                case 2:
                                    np[i[1]]=100
                                    if any(i<100 for i in np):
                                        self.castServantSkill(i[1],i[2],0)
                                        continue
                                case 3|4:
                                    if self.stageTurn>1:
                                        self.castServantSkill(i[1],i[2],0)
                                        continue
                                case 5:
                                    if np[i[1]]<100:
                                        self.castServantSkill(i[1],i[2],i[1]+1)
                                        continue
                                case _:
                                    self.castServantSkill(i[1],i[2],0)
                                    continue
                        case 3,p:
                            np=[Detect.cache.getFieldServantNp(i)if self.servant[i][0]else 0 for i in range(3)]
                            match p:
                                case 0|3|4:
                                    if any(i>=100 for i in np):
                                        self.castServantSkill(i[1],i[2],0)
                                        continue
                                case 1:
                                    target=numpy.argmax(np)
                                    if np[target]>=100:
                                        self.castServantSkill(i[1],i[2],target+1)
                                        continue
                                case 2:
                                    np[i[1]]=0
                                    if any(i>=100 for i in np):
                                        self.castServantSkill(i[1],i[2],0)
                                        continue
                                case 5:
                                    if np[i[1]]>=100:
                                        self.castServantSkill(i[1],i[2],i[1]+1)
                                        continue
                                case _:
                                    self.castServantSkill(i[1],i[2],0)
                                    continue
                        case 4|5|6,_:
                            self.castServantSkill(i[1],i[2],0)
                            continue
                        case 7,p:
                            hp=[Detect.cache.getFieldServantHp(i)if self.servant[i][0]else 999999 for i in range(3)]
                            match p:
                                case 0:
                                    if any(i<6600 for i in hp):
                                        self.castServantSkill(i[1],i[2],0)
                                        continue
                                case 1:
                                    target=numpy.argmin(hp)
                                    if hp[target]<6600:
                                        self.castServantSkill(i[1],i[2],target+1)
                                        continue
                                case 2:
                                    hp[i[1]]=999999
                                    if any(i<6600 for i in hp):
                                        self.castServantSkill(i[1],i[2],0)
                                        continue
                                case 3|4:
                                    self.castServantSkill(i[1],i[2],0)
                                    continue
                                case 5:
                                    if hp[i[1]]<6600:
                                        self.castServantSkill(i[1],i[2],i[1]+1)
                                        continue
                                case _:
                                    self.castServantSkill(i[1],i[2],0)
                                    continue
                        case 8,_:
                            if any((lambda x:x[1]and x[0]==x[1])(Detect.cache.getEnemyNp(i))for i in range(6)):
                                self.castServantSkill(i[1],i[2],i[1]+1)
                                continue
                        case 9,_:
                            if any((lambda x:x[1]and x[0]==x[1])(Detect.cache.getEnemyNp(i))for i in range(6))or Detect.cache.getFieldServantHp(i[1])<3300:
                                self.castServantSkill(i[1],i[2],i[1]+1)
                                continue
                    self.countDown[0][i[1]][i[2]]=1
                else:...
    @logit(logger,logging.INFO)
    def selectCard(self):
        cardServant=Detect.cache.getCardServant(
            [i[0]for i in self.servant if i[0]]
        )
        group=[
            next(
                (
                    pos
                    for pos,servant in enumerate(self.servant)
                    if servant[0]==no
                ),
                card+3,
            )
            for card,no in enumerate(cardServant)
        ]+[0,1,2]
        color,sealed,hougu,np,resist,critical=Detect().getCardColor()+[i[5][1]for i in self.servant],Detect.cache.isCardSealed(),Detect.cache.isHouguReady(),[Detect.cache.getFieldServantNp(i)<100 for i in range(3)],[[1,1.7,.6][i]for i in Detect.cache.getCardResist()],[i/10 for i in Detect.cache.getCardCriticalRate()]
        houguTargeted,houguArea,houguSupport=[[j for j in range(3)if hougu[j]and self.servant[j][0]and self.servant[j][5][0]==i]for i in range(3)]
        houguArea=houguArea if self.stage==self.stageTotal or sum(i>0 for i in self.enemy)>1 and sum(self.enemy)>12000 else[]
        houguTargeted=houguTargeted if self.stage==self.stageTotal or max(self.enemy)>23000+8000*len(houguArea)else[]
        hougu=[i+5 for i in houguSupport+houguArea+houguTargeted]
        if self.stageTurn==1 or houguTargeted or self.enemy[self.target]==0:
            self.target=numpy.argmax(self.enemy)
            fgoDevice.device.perform('\x67\x68\x69\x64\x65\x66'[self.target],(500,))
        self.enemy=[max(0,i-18000*len(houguArea))for i in self.enemy]
        if any(self.enemy)and self.enemy[self.target]==0:self.target=next(i for i in range(5,-1,-1)if self.enemy[i])
        for _ in houguTargeted:
            self.enemy[self.target]=max(0,self.enemy[self.target]-48000)
            if any(self.enemy)and self.enemy[self.target]==0:self.target=next(i for i in range(5,-1,-1)if self.enemy[i])
        def extraAttackWeight(card):
            positions={group[i]for i in card}
            if len(positions)!=1:return 0
            pos=next(iter(positions))
            if pos>=len(self.servant):return 0
            if self.servant[pos][0]!=444:return 1
            return max(1,sum(hp>0 for hp in self.enemy)/2)
        def evaluate(card):return(lambda chainError:(lambda colorChain:(lambda firstBonus:
                sum(
                    ((.3*bool(firstBonus&4)+.1*bool(firstBonus&1)+[1.,1.2,1.4][i]*[1,.8,1.1][color[j]])*(1+min(1,critical[j]+.2*bool(firstBonus&2)))+bool(colorChain==2))*resist[j]*(not sealed[j])
                    for i,j in enumerate(card)if j<5
                )
                +4*(len([i for i in self.enemy if i])>1)*(self.enemy[self.target]<20000)*sum(bool(i)for i in numpy.diff([group[i]for i in card if i<5]))
                +(1.8 if colorChain==-1 else 3)*(not chainError)*extraAttackWeight(card)*resist[card[0]]
                +2.3*(colorChain==0)*len({
                    group[i]
                    for i in card
                    if(
                        i<5
                        and group[i]<len(np)
                        and np[group[i]]
                    )
                })
                +3*(colorChain==1)
            )(7 if colorChain==3 else 1<<color[0]))(-1 if chainError else{(0,):0,(1):1,(2,):2,(0,1,2):3}.get(tuple(set(color[i]for i in card)),-1)))(any(sealed[i]for i in card if i<5))
        card=list(max(permutations(range(5),3-len(hougu)),key=lambda x:evaluate(hougu+list(x))))
        return''.join(['12345678'[i]for i in hougu+card+list({0,1,2,3,4}-set(card))])
    def castServantSkill(self,pos,skill,target):
        fgoDevice.device.press(('ASD','FGH','JKL')[pos][skill])
        detect=Detect(.7)
        kukulkanChoice=detect.isKukulkanSkillChoice()
        if kukulkanChoice:
            logger.info('Select Kukulkan Skill Without Critical Stars')
            fgoDevice.device.touch((640,425),700)
            detect=Detect(.7)
        targetCount=detect.getSkillTargetCount()if kukulkanChoice else 0
        if targetCount:
            target=pos+1 if skill==1 else target or 3
            fgoDevice.device.perform(
                ['3333','2244','3234'][targetCount-1][target]+'\x08',
                (300,700),
            )
        elif detect.isSkillNone():
            logger.warning(f'Skill {pos} {skill} Disabled')
            self.countDown[0][pos][skill]=999
            fgoDevice.device.press('\x08')
        elif detect.isSkillCastFailed():
            logger.warning(f'Skill {pos} {skill} Cast Failed')
            self.countDown[0][pos][skill]=1
            fgoDevice.device.press('J')
            schedule.sleep(1)
        elif t:=detect.getSkillTargetCount():
            target=f-5 if(f:=self.servant[pos][6][skill][1])in{6,7,8}else target or 3
            fgoDevice.device.perform(['3333','2244','3234'][t-1][target]+'\x08',(300,700))
        else:fgoDevice.device.perform('\x08',(700,))
        while not Detect().isTurnBegin():pass
        Detect(.5)
    def castMasterSkill(self,skill,target):
        self.countDown[1][skill]=15
        fgoDevice.device.perform('Q'+'WER'[skill],(300,300))
        if t:=Detect(.4).getSkillTargetCount():fgoDevice.device.perform(['3333','2244','3234'][t-1][target],(300,))
        while not Detect().isTurnBegin():pass
        Detect(.5)
class Battle:
    def __init__(self,turnClass=Turn,returnOnMainInterface=False):
        self.turn=0
        self.turnProc=turnClass()
        self.rainbowBox=False
        self.returnOnMainInterface=returnOnMainInterface
        self.directMainInterface=False
    def __call__(self):
        self.start=time.time()
        self.material={}
        self.directMainInterface=False
        while True:
            if Detect(0,.3).isTurnBegin():
                self.turn+=1
                self.turnProc(self.turn)
            elif self.returnOnMainInterface and Detect.cache.isMainInterface():
                self.directMainInterface=True
                logger.info('Battle Returned Directly To Main Interface')
                return True
            elif storySkip and Detect.cache.isStorySkipConfirm():
                logger.info('Skip Story')
                fgoDevice.device.press('K')
            elif Detect.cache.isSpecialDropSuspended():
                schedule.checkKizunaReisou()
                logger.warning('Kizuna Reisou')
                Detect.cache.save('fgoLog/SpecialDrop')
                fgoDevice.device.press('\x1B')
            elif not self.rainbowBox and Detect.cache.isSpecialDropRainbowBox():self.rainbowBox=True
            elif Detect.cache.isBattleFinished():
                logger.info('Battle Finished')
                self.material=Detect(.4).getMaterial()
                if self.rainbowBox:
                    logger.warning('Special Drop')
                    schedule.checkSpecialDrop()
                    Detect.cache.save('fgoLog/SpecialDrop')
                return True
            elif Detect.cache.isBattleDefeated():
                logger.warning('Battle Defeated')
                schedule.checkDefeated()
                return False
            if storySkip:
                fgoDevice.device.perform('\xBB',(100,))
                if Detect.cache.isStorySkip():fgoDevice.device.perform('\x08',(100,))
            else:fgoDevice.device.perform('\xBB\x08',(100,100))
    @property
    def result(self):
        return{
            'type':'Battle',
            'turn':self.turn,
            'time':time.time()-self.start,
            'material':self.material,
            'directMainInterface':self.directMainInterface,
        }
class Main:
    teamIndex=0
    autoFormation=False
    friendSearchMaxCycles=10
    selectFirstFriendOnListEnd=False
    friendAllTab=False
    def __init__(self,appleTotal=0,appleKind=0,battleClass=Battle):
        self.appleTotal=appleTotal
        self.appleKind=appleKind
        self.battleClass=battleClass
    @serialize(mutex)
    def __call__(self,questIndex=0,battleTotal=None):
        self.prepare()
        while True:
            self.battleProc=self.battleClass()
            while True:
                if Detect(.3,.3).isMainInterface():
                    if self.battleCount==battleTotal:return logger.info('Operation Unit Completed')
                    fgoDevice.device.press('84L'[questIndex])
                    questIndex=0
                    if Detect(1.2).isBattleContinue():fgoDevice.device.press('K')
                    elif Detect.cache.isSkillCastFailed():
                        fgoDevice.device.press('J')
                        return logger.info('No Storm Pot')
                    if Detect(.7,.3).isApEmpty()and not self.eatApple():return logger.info('Ap Empty')
                    self.chooseFriend()
                    while True:
                        detect=Detect(0,.3)
                        if detect.isSupportFormationCondition():
                            logger.info('Close Support Formation Condition')
                            fgoDevice.device.touch((640,601))
                        elif detect.isBattleFormation():
                            if detect.isFormationRestriction():
                                logger.info('Close Formation Restriction')
                                fgoDevice.device.touch((640,601),1000)
                            else:break
                    if self.teamIndex and Detect.cache.getTeamIndex()+1!=self.teamIndex:fgoDevice.device.perform('\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7A\x7B\x7C\x7D\x7E'[self.teamIndex-1],(1000,))
                    if self.autoFormation:fgoDevice.device.perform('\xDEL ',(1000,1500,1000))
                    fgoDevice.device.perform(' M ',(2000,2000,10000))
                    break
                elif Detect.cache.isBattleContinue():
                    if self.battleCount==battleTotal:
                        fgoDevice.device.press('F')
                        return logger.info('Operation Unit Completed')
                    fgoDevice.device.press('K')
                    if Detect(.7,.3).isApEmpty()and not self.eatApple():return logger.info('Ap Empty')
                    self.chooseFriend()
                    schedule.sleep(6)
                    break
                elif Detect.cache.isSkillCastFailed():
                    fgoDevice.device.press('J')
                    return logger.info('No Storm Pot')
                elif storySkip and Detect.cache.isStorySkipConfirm():
                    logger.info('Skip Story')
                    fgoDevice.device.press('K')
                elif Detect.cache.isTurnBegin():break
                elif Detect.cache.isAddFriend():fgoDevice.device.perform('X',(300,))
                elif Detect.cache.isSpecialDropSuspended():fgoDevice.device.perform('\x1B',(300,))
                if storySkip and Detect.cache.isStorySkip():fgoDevice.device.press('\x08')
                else:fgoDevice.device.press('\xBB')
            self.battleCount+=1
            logger.info(f'Battle {self.battleCount}')
            if self.battleProc():
                self._recordBattleResult()
                fgoDevice.device.perform(' '*10,(400,)*10)
            else:
                self.defeated+=1
                fgoDevice.device.perform('CIK',(500,500,500))
            schedule.checkStopLater()
    def prepare(self):
        self.start=time.time()
        self.material={}
        self.battleCount=0
        self.battleTurn=0
        self.battleTime=0
        self.defeated=0
    def _recordBattleResult(self):
        result=self.battleProc.result
        self.battleTurn+=result['turn']
        self.battleTime+=result['time']
        self.material={
            i:self.material.get(i,0)+result['material'].get(i,0)
            for i in self.material|result['material']
        }
        return result
    @property
    def result(self):return{
            'type':'Main',
            'time':time.time()-self.start,
            'battle':self.battleCount,
            'defeated':self.defeated,
            'turnPerBattle':self.battleTurn/(self.battleCount-self.defeated)if self.battleCount-self.defeated else 0,
            'timePerBattle':self.battleTime/(self.battleCount-self.defeated)if self.battleCount-self.defeated else 0,
            'material':self.material,
        }
    @logit(logger,logging.INFO)
    def eatApple(self):
        if not self.appleTotal:return fgoDevice.device.press('Z')
        if self.appleKind==3:fgoDevice.device.perform('V',(600,))
        fgoDevice.device.perform('W4K48'[self.appleKind]+'L',(600,1200))
        self.appleTotal-=1
        return self.appleTotal+1
    def _waitFriendSelected(self):
        missing=0
        while missing<5:
            if Detect(.2,.2).isChooseFriend():missing=0
            else:missing+=1
    def _selectFirstFriend(self):
        logger.warning('FriendTrace Select First Visible Support')
        fgoDevice.device.press('8')
        self._waitFriendSelected()
    @logit(logger,logging.INFO)
    def chooseFriend(self,skipStory=None):
        friendSelectionActive.set()
        try:
            return self._chooseFriend(skipStory)
        finally:
            friendSelectionActive.clear()

    def _chooseFriend(self,skipStory=None):
        if skipStory is None:skipStory=storySkip
        refresh=False
        while not Detect(0,.3).isChooseFriend():
            if Detect.cache.isSupportFormationCondition():
                logger.info('Close Support Formation Condition')
                fgoDevice.device.touch((640,601),1000)
                continue
            if Detect.cache.isBattleFormation():return
            if skipStory and Detect.cache.isStorySkipConfirm():
                logger.info('Skip Story')
                fgoDevice.device.perform('K',(1200,))
                continue
            if skipStory and Detect.cache.isStorySkip():
                logger.info('Open Story Skip Confirm')
                fgoDevice.device.perform('\x08',(800,))
                continue
            if Detect.cache.isNoFriend():
                if refresh:schedule.sleep(10)
                fgoDevice.device.perform('\xBAK',(500,1000))
                refresh=True
                continue
        if self.friendAllTab:
            logger.info('Select All Support Tab')
            fgoDevice.device.touch((700,130),1200)
            Detect(.8,.3)
        if not friendImg.flush():
            self._selectFirstFriend()
            return
        searchCycles=0
        while True:
            timer=time.time()
            while True:
                for i,j in sorted(friendImg.items()):
                    pos=Detect.cache.findFriend(j)
                    logger.warning(
                        f'FriendTrace Template={i} Position={pos}'
                    )
                    if pos is None:continue
                    logger.warning(
                        f'FriendTrace Touch Template={i} Position={pos}'
                    )
                    fgoDevice.device.touch(pos)
                    ClassicTurn.friendInfo=(lambda r:(lambda p:[
                        [[-1 if p[i*4+j]=='X'else int(p[i*4+j],16)for j in range(4)]for i in range(3)],
                        [-1 if p[i+12]=='X'else int(p[i+12],16)for i in range(2)],
                    ])(r.group())if r else[[[-1,-1,-1,-1],[-1,-1,-1,-1],[-1,-1,-1,-1]],[-1,-1]])(re.match('([0-9X]{3}[0-9A-FX]){3}[0-9X][0-9A-FX]$',i.replace('-','')[-14:].upper()))
                    self._waitFriendSelected()
                    return i
                if searchCycles>=self.friendSearchMaxCycles:
                    logger.warning(f'Friend template not found after {searchCycles} search cycles, select first visible support')
                    self._selectFirstFriend()
                    return
                if Detect.cache.isFriendListEnd():
                    if self.selectFirstFriendOnListEnd:
                        logger.warning('Friend list end reached, select first visible support')
                        self._selectFirstFriend()
                        return
                    searchCycles+=1
                    if searchCycles>=self.friendSearchMaxCycles:
                        logger.warning(f'Friend template not found after {searchCycles} search cycles, select first visible support')
                        self._selectFirstFriend()
                        return
                    break
                logger.warning(
                    f'FriendTrace Swipe Cycle={searchCycles+1}'
                )
                fgoDevice.device.swipeSlow(
                    (600,650),(600,250),1.2
                )
                searchCycles+=1
                Detect(.8,.3)
            if refresh:schedule.sleep(max(0,timer+10-time.time()))
            fgoDevice.device.perform('\xBAK',(500,1000))
            refresh=True
            while not Detect(.2).isChooseFriend():
                if Detect.cache.isNoFriend():
                    schedule.sleep(10)
                    fgoDevice.device.perform('\xBAK',(500,1000))
class Operation(list,Main):
    def __init__(self,data=(),*args,**kwargs):
        list.__init__(self,data)
        Main.__init__(self,*args,**kwargs)
    def __call__(self):
        super().prepare()
        if not self:super().__call__()
        while self:
            quest,times=self[0]
            del self[0]
            goto(quest)
            super().__call__(quest[-1],self.battleCount+times if times else None)
    def prepare(self):pass

class Next(Main):
    friendAllTab=True
    autoFormation=True
    def __init__(self,appleTotal=0,appleKind=0,skipStory=True,battleClass=Battle,friendSearchMaxCycles=5):
        super().__init__(appleTotal,appleKind,battleClass)
        self.skipStory=skipStory
        self.friendSearchMaxCycles=max(1,friendSearchMaxCycles)
        self.selectFirstFriendOnListEnd=True
    @serialize(mutex)
    def __call__(self):
        self.prepare()
        if XDetect.region!='CN':
            raise ScriptStop('Next Currently Supports CN Only')
        nextMissing=0
        unknownFrames=0
        while True:
            detect=Detect(.3,.3)
            if detect.isSupportFormationCondition():
                logger.info('Close Support Formation Condition')
                fgoDevice.device.touch((640,601),1000)
            elif detect.isAutoFormationDecide():
                logger.info('Confirm Auto Formation')
                fgoDevice.device.touch((1170,667),1000)
            elif detect.isAutoFormationConfirm():
                if self.autoFormation:
                    logger.info('Run Auto Formation')
                    fgoDevice.device.touch((930,602),1000)
                else:
                    logger.info('Cancel Auto Formation')
                    fgoDevice.device.touch((350,602),1000)
            elif detect.isBattleContinue():fgoDevice.device.perform('K',(1000,))
            elif detect.isApEmpty():
                if not self.eatApple():return logger.info('Ap Empty')
            elif detect.isBattleFinished():
                logger.info('Resume From Battle Result')
                fgoDevice.device.perform(' '*10,(400,)*10)
            elif detect.isChooseFriend():self.chooseFriend(self.skipStory)
            elif detect.isBattleFormation():
                if detect.isFormationRestriction():
                    logger.info('Close Formation Restriction')
                    fgoDevice.device.touch((640,601),1000)
                else:
                    if self.teamIndex and detect.getTeamIndex()+1!=self.teamIndex:fgoDevice.device.perform('\x70\x71\x72\x73\x74\x75\x76\x77\x78\x79\x7A\x7B\x7C\x7D\x7E'[self.teamIndex-1],(1000,))
                    fgoDevice.device.perform(' M ',(2000,2000,10000))
            elif detect.isTurnBegin():
                self.battleProc=self.battleClass()
                self.battleProc.returnOnMainInterface=True
                self.battleCount+=1
                logger.info(f'Battle {self.battleCount}')
                if self.battleProc():
                    battleResult=self._recordBattleResult()
                    if not battleResult.get('directMainInterface'):fgoDevice.device.perform(' '*10,(400,)*10)
                else:
                    self.defeated+=1
                    fgoDevice.device.perform('CIK',(500,500,500))
                schedule.checkStopLater()
            elif detect.isAddFriend():
                logger.info('End Friend Request')
                fgoDevice.device.perform('X',(1200,))
            elif detect.isSpecialDropSuspended():fgoDevice.device.perform('\x1B',(300,))
            elif detect.isMainInterface():
                unknownFrames=0
                if pos:=detect.findNext():
                    nextMissing=0
                    fgoDevice.device.touch(pos,1000)
                else:
                    nextMissing+=1
                    if nextMissing>=20:return logger.info('No Next Quest')
                continue
            elif self.skipStory and detect.isStorySkipConfirm():
                logger.info('Skip Story')
                fgoDevice.device.perform('K',(1200,))
            elif self.skipStory and detect.isStorySkip():
                logger.info('Open Story Skip Confirm')
                fgoDevice.device.perform('\x08',(800,))
            elif pos:=detect.findStoryChoice():
                logger.info('Select First Story Choice')
                fgoDevice.device.touch(pos,1200)
            else:
                unknownFrames+=1
                if self.skipStory:
                    if unknownFrames>=20:
                        return logger.warning(
                            'Unknown Next State: stop to avoid blind clicks'
                        )
                    schedule.sleep(3)
                else:
                    logger.info('Advance Story')
                    fgoDevice.device.touch((640,500),800)
                continue
            nextMissing=0
            unknownFrames=0
