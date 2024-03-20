from serial import Serial
import time # time 모듈을 수입: 시간 관련 함수의 집합체
import psycopg2
# 통계 처리
import statistics as stat # statistics의 별명을 stat
import matplotlib.pyplot as plt #matlab하고 비슷한 그래프 그릴때 씀
#pandas
import pandas.io.sql as psql


# public 멤버(클래스 외부에서 편하게 접근 가능): __이름__
# private 멤버(클래스 외부에서 접근 불가능(?), 특별한 부호 붙이면 접근 가능): __이름
class PythonHub: # 클래스(객체의 설계도), 인스턴스(클래스로 만든 실체, 클래스로 만든 변수) 구별
    # Private 멤버: __로 시작하는 변수나 함수
    __defComName = 'COM7'
    __defComBps = 9600
    __defWaitTime = 0.5 # 단위: 초

    # Public 정적 멤버: 항상 위에 정의 -> 위에 정의되어야 밑에서 접근(호출) 가능
    def waitSerial(): # self가 없음 -> 클래스의 정적(static) 멤버: 인스턴스 멤버에 접근하지 않음
        time.sleep(PythonHub.__defWaitTime) # 단위: 초; 클래스 멤버에 접근할 때는 클래스명.(PythonHub.)

    def wait(delaySec):
        time.sleep(delaySec)
    
    # 생성자(constructor): 이름은 __init__로 고정
    def __init__(self, comName = __defComName, comBps = __defComBps): # comName: Serial 이름, comBps: Serial 속도
        #print('생성자 호출됨')
        # 멤버 변수 생성: 변수를 선언하지 않고 self.으로 변수를 추가; self는 클래스(PythonHub)로 만든 인스턴스에 접근하기 위한 키워드
        # Serial 클래스의 인스턴스 생성 -> self.ard에 할당
        self.ard = Serial(comName, comBps) # C++ 경우: Serial ard;
        self.clearSerial() # Serial 입력 버퍼 초기화
        self.clearVoltTuple() # 전압과 측정시간을 위한 튜플공간 
        self.clearLightTuple() # light 튜플공간 초기화
        self.conn = None #DB의 connection
        self.cur = None #DB의 cursor
    # 소멸자(destructor): 이름은 __del__으로 고정
    def __del__(self):
        #print('소멸자 호출됨')
        if self.ard.isOpen(): # Serial이 열려(open)있는가?
            self.ard.close() # Serial을 닫음(close)
        
    # Serial 메소드(멤버 함수)
    def writeSerial(self, sCmd): # 인스턴스 접근하기 위한 self 추가
        btCmd = sCmd.encode()
        nWrite = self.ard.write(btCmd) # 인스턴스의 멤버인 ard에 접근: self.ard
        self.ard.flush()
        return nWrite
    def readSerial(self):
        nRead = self.ard.in_waiting
        if nRead > 0:
            btRead = self.ard.read(nRead)
            sRead = btRead.decode()
            return sRead
        else: return ''
    def clearSerial(self): # Serial 버퍼를 비우는 메소드
        PythonHub.waitSerial()
        self.readSerial()
    def talk(self, sCmd):
        return self.writeSerial(sCmd + '\n')
    def listen(self):
        PythonHub.waitSerial() # 클래스의 정적 멤버인 waitSerial() 호출
        sRead = self.readSerial()
        return sRead.strip()
    def talkListen(self, sCmd):
        self.talk(sCmd)
        return self.listen()

   # DB 메소드
    def connectDb(self):
        self.conn = psycopg2.connect(host='localhost', database='kijun', user='postgres', password='password', port='5432') # DB connection 얻기
        self.cur = self.conn.cursor() # connection의 cursor(커서)
    def closeDb(self):
        self.cur.close()
        self.conn.close()
    def writeDb(self, cmd): # DB에 명령어 cmd 쓰기
        sCmd = str(cmd) # string으로 type casting
        self.cur.execute(sCmd) # cursor에 명령어(SQL) 실행
        self.conn.commit() # connection에 기록하기 -> cursor 명령어를 DB가 실행
    
    #전압계 메소드
    def getVolt(self):
        try:
            sVolt = self.talkListen('get volt')
            volt = float(sVolt) #문자열 sVolt를 float(double)으로 변셔
            return volt
        except: # try 부분에서 에러가 발생한 경우 실행되는 코드
            print('Serial error!')
            return -1

    def addVoltToTuple(self):
        volt = self.getVolt()
        measTime = time.time() #현재시간 읽기: 에포크 타임(기원후 시간, epoch time)
        if volt >= 0: #측정성공
            self.volts += (volt,)# 원소 하나인 튜플은 마지막에 , 추가
            self.voltTimes += (measTime,)
            return True
        else: return False #측정 실패
        

    
    def clearVoltTuple(self):
        self.volts = () #전압 측정값ㅇ르 담은 튜플; (): 현재 변수를 tuple로 초기화
        self.voltTimes = () #전압 측정 시간을 담은 tuple(튜플)

    def printVoltTuple(self):
        for(volt, measTime) in zip(self.volts, self.voltTimes):
            print(f'volt = {volt} @ time = {time.ctime(measTime)}') ##f: formatted string을 의미; {...} 안을 코드로 인식해 실행 -> 그 결과는 문자열로 반환
        #{...}안을 코드로 인식해 실행 -> 그 결과는 문자열로 반환; ctime(): char time -> 현재 애포크 타임을 보기 편한 문자열 시간으로 변경


    def sampleVoltTuple(self, nCount, delay): # delay 주기로 nCount개의 전압 측정값을 샘플링 -> 샘프링 결과는 volt, voltTimes 튜플에 저장
          # for i in range(nCount):
           #    print(self.addVoltToTuple())
            #   PythonHub.wait(nDelay)
        i = 0 
        while i < nCount:
            bResult = self.addVoltToTuple()
            print(bResult)
            PythonHub.wait(delay)
            if bResult: i += 1 #성공시에만 증가


    #plot
    def getVoltMean(self):#전압의 평균
        return stat.mean(self.volts)
    def getVoltVariance(self):
        return stat.variance(self.volts)#분산
    def getVoltStdev(self):#전압의 표준편차
        return stat.stdev(self.volts)
    def getVoltMedian(self):#전압의 중앙값
        return stat.median(self.volts)
    def plotVoltTuple(self):
        plt.plot(self.voltTimes, self.volts)
        plt.show()
    
    def countVoltTable(self):
        self.connectDb()
        self.writeDb('SELECT COUNT(*) FROM volt_table')
        nCount = self.cur.fetchone()[0]
        self.closeDb()
        return nCount

    
    def insertOneVoltTable(self):# 전압 측정값 하나를 DB에 추가
        self.connectDb()
        volt = self.getVolt()
        measTime = time.time() #현재시간 읽기: 에포크 타임(기원후 시간, epoch time)
        if volt >= 0: #측정성공
            self.writeDb(f'INSERT INTO volt_table(meas_time, volt) VALUES({measTime}, {volt})')
            self.closeDb()
            return True
        else: 
            self.closeDb()
            return False #측정 실패
        
    def clearVoltTable(self):# DB에 저장된 전압 측정값을 삭제
        self.connectDb()
        self.writeDb('TRUNCATE volt_table')
        self.closeDb()


    def saveVoltTupleIntoTable(self): #volts, voltTimes 튜플을 DB에 저장; volts, voltTimes는 clear
        self.connectDb()
        for(volt, measTime) in zip(self.volts, self.voltTimes):
            self.writeDb(f'INSERT INTO volt_table(meas_time, volt) VALUES({measTime}, {volt})')
        self.closeDb()
        self.clearVoltTuple()
        
    def loadVoltTupleFromTable(self): #DB에서 정보를 가져와서, volts, voltTimes튜플에 추가
        self.connectDb()
        self.writeDb('SELECT meas_time, volt FROM volt_table')# SQL에 0번은 meas_time, 1번은 volt
        result = self.cur.fetchall() # 튜플을 원소로 가진 리스트
        for tuple in result:
            self.volts += (tuple[1],)# 원소 하나인 튜플은 마지막에 , 추가
            self.voltTimes += (tuple[0],)
               
        self.closeDb()

    def writeHtmlVoltTuple(self):
        html = '<table width="100%" border="1"><thead><tr><th>번호</th><th>전압 측정값</th><th>측정 일시</th></tr></thead>'
        i = 1
        for (volt, voltTime) in zip(self.volts, self.voltTimes):
            html += f'<tr><td>{i}</td><td>{volt} V</td><td>{time.ctime(voltTime)}</td></tr>'
            i += 1
        html += '</table>'
        return html
   
    
    
    #조도측정 메소드
    def getLight(self):
        try:
            sLight = self.talkListen('get light')
            return sLight 
        except: # try 부분에서 에러가 발생한 경우 실행되는 코드
            print('Serial error!')
            return -1

    def getLightStep(self):
        try:
            sLightStep = self.talkListen('get lightstep')
            lightStep = int(sLightStep)
            return lightStep
        except:
            print('Serial error!')
            return -1

    def insertOneLightTable(self):# 전압 측정값 하나를 DB에 추가
        self.connectDb()
        light = self.getLight()
        lightStep = self.getLightStep()
        measTime = time.time() #현재시간 읽기: 에포크 타임(기원후 시간, epoch time)
        if lightStep >= 0: #측정성공
            self.writeDb(f"INSERT INTO light_table(meas_time, light, light_step) VALUES({measTime}, '{light}', {lightStep})")
            # 문자열이라 '{light}'
            self.closeDb()
            return True
        else: 
            self.closeDb()
            return False #측정 실패

    def countLightTable(self):
        self.connectDb()
        self.writeDb('SELECT COUNT(*) FROM light_table')
        nCount = self.cur.fetchone()[0]
        self.closeDb()
        return nCount
    
    def clearLightTable(self):# DB에 저장된 전압 측정값을 삭제
        self.connectDb()
        self.writeDb('TRUNCATE light_table')
        self.closeDb()


    def addLightToTuple(self):
        light = self.getLight()
        lightStep = self.getLightStep()
        measTime = time.time() #현재시간 읽기: 에포크 타임(기원후 시간, epoch time)
        if lightStep >= 0: #측정성공
            self.lights += (light,)# 원소 하나인 튜플은 마지막에 , 추가
            self.lightSteps += (lightStep,)# 원소 하나인 튜플은 마지막에 , 추가
            self.lightTimes += (measTime,)
            return True
        else: return False #측정 실패
    def clearLightTuple(self):
        self.lights = () #조도 측정값ㅇ르 담은 튜플; (): 현재 변수를 tuple로 초기화
        self.lightSteps = () #조도전압 측정 시간을 담은 tuple(튜플)
        self.lightTimes = () #조도전압 측정 시간을 담은 tuple(튜플)

    
    def printLightTuple(self):
        for(light, lightStep ,measTime) in zip(self.lights,self.lightSteps, self.lightTimes):
            print(f'light = {light}@ lightStep = {lightStep} @ time = {time.ctime(measTime)}')
            ##f: formatted string을 의미; {...} 안을 코드로 인식해 실행 -> 그 결과는 문자열로 반환
        #{...}안을 코드로 인식해 실행 -> 그 결과는 문자열로 반환; ctime(): char time -> 현재 애포크 타임을 보기 편한 문자열 시간으로 변경

        
    def sampleLightTuple(self, nCount, delay):
        i = 0 
        while i < nCount:
            bResult = self.addLightToTuple()
            print(bResult)
            PythonHub.wait(delay)
            if bResult: i += 1 #성공시에만 증가
    def saveLightTupleIntoTable(self):
        self.connectDb()
        for(light,lightStep, measTime) in zip(self.lights, self.lightSteps, self.lightTimes):
            self.writeDb(f"INSERT INTO light_table(meas_time, light, light_step) VALUES({measTime}, '{light}', {lightStep})")
            # 문자열이라 '{light}'
        self.closeDb()
        self.clearLightTuple()
    def loadLightTupleFromTable(self):
        self.connectDb()
        self.writeDb('SELECT meas_time, light, light_step FROM light_table')# SQL에 0번은 meas_time, 1번은 light , 2번은 light_step
        result = self.cur.fetchall() # 튜플을 원소로 가진 리스트
        for tuple in result:
            self.lightTimes += (tuple[0],)
            self.lights += (tuple[1],)# 원소 하나인 튜플은 마지막에 , 추가
            self.lightSteps += (tuple[2],)# 원소 하나인 튜플은 마지막에 , 추가
        self.closeDb()

    
    #plot
    def getLightStepMean(self):#전압의 평균
        return stat.mean(self.lightSteps)
    def getLightStepVariance(self):
        return stat.variance(self.lightSteps)#분산
    def getLightStepStdev(self):#전압의 표준편차
        return stat.stdev(self.lightSteps)
    def getVoltMedian(self):#전압의 중앙값
        return stat.median(self.volts)
    def plotLightStepTuple(self):
        plt.plot(self.lightTimes, self.lightSteps)
        plt.show()

    #조도 html 테이블 문서작성
    def writeHtmlLightTuple(self):
        html = '<table width="100%" border="1"><thead><tr><th>번호</th><th>현재 조도상태</th><th>조도 측정값</th><th>측정 일시</th></tr></thead>'
        i = 1
        for (light, lightStep,lightTime) in zip(self.lights, self.lightSteps, self.lightTimes):
            html += f'<tr><td>{i}</td><td>{light}</td><td>{lightStep}</td><td>{time.ctime(lightTime)}</td></tr>'
            i += 1
        html += '</table>'
        return html
    

    # Servo 메소드
    def setServoMove(self, ang):# amg만큼 각도 회전
        try:
            nAng = int(ang)# 변수 ang -> int로 변정(type casting)
            sAng = str(nAng)# int nAnf-> 문자열로 지정
            self.talk('set servo ' + sAng)
        except:
            print('각도 설정 오류')


    # LED 메소드
    def setLedColor(self, color):# color : yellow, pink, red, green, blue, cyan, black, white
        try:
            if ((type(color) == int) or (type(color) == float)):
                print('색상 설정 오류')
            else:
                self.talk('set led ' + color)
        except Exception as e :
             print('예외발생이름: {}'.format(type(e)))
             print('예외발생이름: {}'.format(e))


    # Buzzer 메소드
    def setBuzzerNote(self, note, delay):# note음을 delay만큼 소리낸다
        try:
            if ((type(note) == int) or (type(note) == float)):
                print('note 설정 오류')
            else:
                nDelay = int(delay)# 변수 delay -> int로 변정(type casting) 오류리 except
                sDelay = str(nDelay)# int nAnf-> 문자열로 지정
                self.talk('set buzzer {} {}'.format(note,sDelay)) #공백을 기준으로 token하기에 format사용
        except:
            print('delay 설정 오류')




  # 데이터베이스에서 데이터를 가져와서 pandas DataFrame으로 변환
    def getTableData(self, tableName):
        self.connectDb()
        df = psql.read_sql(f'SELECT * FROM {tableName}',self.conn)
        self.closeDb()
        return df

    # 전압 통계 출력
    def describeVoltTable(self):
        volt_df = self.getTableData('volt_table')
        self.vSer = volt_df['volt']
        self.vMean = self.vSer.mean()#평균
        self.vMed = self.vSer.median()#중앙값
        self.vVar = self.vSer.var()#분산
        self.vStd = self.vSer.std()#표준편차
        print("=== 전압 통계 ===")
        print(f'평균 : {self.vMean}')
        print(f'중앙값 : {self.vMed}')
        print(f'분산 : {self.vVar}')
        print(f'평균 : {self.vStd}')

    # 조도 통계 출력
    def describeLightTable(self):
        light_df = self.getTableData('light_table')
        self.lSer = light_df['light_step']
        self.lMean = self.lSer.mean()#평균
        self.lMed = self.lSer.median()#중앙값
        self.lVar = self.lSer.var()#분산
        self.lStd = self.lSer.std()#표준편차
        print("=== 조도 통계 ===")
        print(f'평균 : {self.lMean}')
        print(f'중앙값 : {self.lMed}')
        print(f'분산 : {self.lVar}')
        print(f'평균 : {self.lStd}')

