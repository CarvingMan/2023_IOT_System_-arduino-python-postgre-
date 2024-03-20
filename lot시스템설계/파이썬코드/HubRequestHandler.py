from http.server import SimpleHTTPRequestHandler
import time
from urllib import parse

class HubRequestHandler(SimpleHTTPRequestHandler): # SimpleHTTPRequestHandler를 상속받아 HubRequestHandler 클래스를 구현
    def do_GET(self): #GET요청을 처리하기 위한 메소드 (오버라이딩)
        print(self.path)
        result = parse.urlsplit(self.path)
        if result.path == '/': self.writeHome() # 홈
        elif result.path == '/meas_one_volt': self.writeMeasOneVolt()
        elif result.path == '/sample_volt': self.writeSampleVolt(result.query)
        elif result.path == '/clearVoltTable': self.writeClearVoltTable() #volt table clear
        elif result.path == '/meas_one_light': self.writeMeasOneLight()
        elif result.path == '/sample_light': self.writeSampleLight(result.query)
        elif result.path == '/clearLightTable': self.writeClearLightTable() #light table clear
        elif result.path == '/servo_move_0': self.writeServoMove(0)
        elif result.path == '/servo_move_90': self.writeServoMove(90)
        elif result.path == '/servo_move_180': self.writeServoMove(180)
        elif result.path == '/servo_move': self.writeCustomServoMove(result.query) # 자유이동
        elif result.path == '/led': self.writeSetLed(result.query) # led
        elif result.path == '/buzzer': self.writeBuzzer(result.query) # buzzer 
        else: self.writeNotFound() # 페이지가 없음
    def writeHead(self, nStatus): # response의 header
        self.send_response(nStatus)
        self.send_header('content-type', 'text/html') # 속성(attribute), 값 순으로 입력
        self.end_headers()
    def writeHtml(self, html):
        self.wfile.write(html.encode()) # html(유니코드) -> 바이트로 변경(encode() 함수 역할)
    def writeHome(self): # 홈용 HTLM을 쓰기
        self.writeHead(200) # 200: 성공
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>Python Web Server</title>'
        html += '</head><body style="background-color: rgb(246, 205, 199);">'
        html += '<div><center><h1>IOT시스템설계 페이지</hl></center>'
        html += '<center><h6>작성자: 손기준</h6></center></div>'
        html += '''<div style="display: flex; justify-content: center; align-items: center; 
        background-color: rgb(255, 223, 219); height:450px">''' #아이템 중앙정렬
        html += '''<img style="width: 400px; height: auto;" 
        src="https://linearmicrosystems.com/wp-content/uploads/2020/01/shutterstock_1027460860.jpg"></div>''' #이미지 사이즈 조절
        html += '</body></html>'
        self.writeHtml(html)
    def writeNotFound(self):
        self.writeHead(404) # 404: not found
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>페이지 없음</title>'
        html += '</head><body>'
        html += f'<div><h3>{self.path}에 대한 페이지는 존재하지 않습니다.</h3></div>'
        html += '</body></html>'
        self.writeHtml(html)
   
    #volt관련 메소드드
    def writeMeasOneVolt(self):
        self.writeHead(200) # 200: 성공
        nTime = time.time()
        bResult = self.server.gateway.insertOneVoltTable() # gateway == PythonHub의 인스턴스
        if bResult: sResult = '성공'
        else: sResult = '실패'
        nMeasCount = self.server.gateway.countVoltTable()
        self.server.gateway.clearVoltTuple()
        self.server.gateway.loadVoltTupleFromTable()
        self.server.gateway.describeVoltTable() #평균,중앙값,분산,표준편차 계산
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>전압 한 번 측정</title>'
        html += '</head><body style="background-color: rgb(255, 223, 219);">'
        html += f'<div><h5>측정 시간: {time.ctime(nTime)}</h5></div>'
        html += f'<div><p>전압 측정이 {sResult}했습니다.</p>'
        html += f'<p>현재까지 {nMeasCount}번 측정했습니다.</div>'
        html += self.server.gateway.writeHtmlVoltTuple()
        
        html += '<div style="margin-top:5%;"><h2>전체 측정결과</h2>'
        html += f'<p> 평균: {self.server.gateway.vMean}<br>'
        html += f'<p> 중앙값: {self.server.gateway.vMed}<br>'
        html += f'<p> 분산: {self.server.gateway.vVar}<br>'
        html += f'<p> 표준편차: {self.server.gateway.vStd}<br></div>'
        html += '</body></html>'
        self.writeHtml(html)
    def writeSampleVolt(self, qs):
        self.writeHead(200) # 200: 성공
        qdict = parse.parse_qs(qs)
        nCount = int(qdict['count'][0])
        delay = float(qdict['delay'][0])
        self.server.gateway.clearVoltTuple()
        nTime = time.time()
        self.server.gateway.sampleVoltTuple(nCount, delay)
        self.server.gateway.saveVoltTupleIntoTable()
        nMeasCount = self.server.gateway.countVoltTable()
        self.server.gateway.loadVoltTupleFromTable()
        self.server.gateway.describeVoltTable() #평균,중앙값,분산,표준편차 계산
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>전압 여러 번 측정</title>'
        html += '</head><body style="background-color: rgb(255, 223, 219);">'
        html += f'<div><h5>측정 시간: {time.ctime(nTime)}</h5></div>'
        html += f'<div><p>전압을 {nCount}번 샘플링했습니다.</p>'
        html += f'<p>현재까지 {nMeasCount}번 측정했습니다.</div>'
        html += self.server.gateway.writeHtmlVoltTuple()
        html += '<div style="margin-top:5%;"><h2>전체 측정결과</h2>'
        html += f'<p> 평균: {self.server.gateway.vMean}<br>'
        html += f'<p> 중앙값: {self.server.gateway.vMed}<br>'
        html += f'<p> 분산: {self.server.gateway.vVar}<br>'
        html += f'<p> 표준편차: {self.server.gateway.vStd}<br></div>'
        html += '</body></html>'
        self.writeHtml(html)
    def writeClearVoltTable(self):
        self.writeHead(200)#200:성공
        nTime = time.time()
        self.server.gateway.clearVoltTable() #voltTable 튜플들 삭제
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>voltTable 삭제</title>'
        html += '</head><body style="background-color: rgb(255, 223, 219);">'
        html += '<div style="display: flex; flex-direction:column; justify-content: center; align-items: center;">' # 아이템 중앙정렬
        html += f'<h3>삭제 시간: {time.ctime(nTime)}</h3>'
        html += '<p>voltTable를 삭제했습니다.</p>'
        html += '</body></html>' #버튼 클릭시 input태그의 value를 가져오고 window객체의 location함수를 통하여 이동
        self.writeHtml(html)

    #light관련 메소드
    def writeMeasOneLight(self):
        self.writeHead(200) # 200: 성공
        nTime = time.time()
        bResult = self.server.gateway.insertOneLightTable() # gateway == PythonHub의 인스턴스
        if bResult: sResult = '성공'
        else: sResult = '실패'
        nMeasCount = self.server.gateway.countLightTable()
        self.server.gateway.clearLightTuple() #이전 튜플 삭제
        self.server.gateway.loadLightTupleFromTable()
        self.server.gateway.describeLightTable() #평균,중앙값,분산,표준편차 계산
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title> 조도 한 번 측정</title>'
        html += '</head><body style="background-color: rgb(255, 223, 219);">'
        html += f'<div><h5>측정 시간: {time.ctime(nTime)}</h5></div>'
        html += f'<div><p>조도 측정이 {sResult}했습니다.</p>'
        html += f'<p>현재까지 {nMeasCount}번 측정했습니다.</div>'
        html += self.server.gateway.writeHtmlLightTuple()
        
        html += '<div style="margin-top:5%;"><h2>전체 측정결과</h2>'
        html += f'<p> 평균: {self.server.gateway.lMean}<br>'
        html += f'<p> 중앙값: {self.server.gateway.lMed}<br>'
        html += f'<p> 분산: {self.server.gateway.lVar}<br>'
        html += f'<p> 표준편차: {self.server.gateway.lStd}<br></div>'
        html += '</body></html>'
        self.writeHtml(html)
    def writeSampleLight(self, qs):
        self.writeHead(200) # 200: 성공
        qdict = parse.parse_qs(qs)
        nCount = int(qdict['count'][0])
        delay = float(qdict['delay'][0])
        self.server.gateway.clearLightTuple()
        nTime = time.time()
        self.server.gateway.sampleLightTuple(nCount, delay)
        self.server.gateway.saveLightTupleIntoTable()
        nMeasCount = self.server.gateway.countLightTable()
        self.server.gateway.loadLightTupleFromTable()
        self.server.gateway.describeLightTable() #평균,중앙값,분산,표준편차 계산
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>조도 여러 번 측정</title>'
        html += '</head><body style="background-color: rgb(255, 223, 219);">'
        html += f'<div><h5>측정 시간: {time.ctime(nTime)}</h5></div>'
        html += f'<div><p>조도을 {nCount}번 샘플링했습니다.</p>'
        html += f'<p>현재까지 {nMeasCount}번 측정했습니다.</div>'
        html += self.server.gateway.writeHtmlLightTuple()
        html += '<div style="margin-top:5%;"><h2>전체 측정결과</h2>'
        html += f'<p> 평균: {self.server.gateway.lMean}<br>'
        html += f'<p> 중앙값: {self.server.gateway.lMed}<br>'
        html += f'<p> 분산: {self.server.gateway.lVar}<br>'
        html += f'<p> 표준편차: {self.server.gateway.lStd}<br></div>'
        html += '</body></html>'
        self.writeHtml(html)
    def writeClearLightTable(self):
        self.writeHead(200)#200:성공
        nTime = time.time()
        self.server.gateway.clearLightTable() #voltTable 튜플들 삭제
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>lightTable 삭제</title>'
        html += '</head><body style="background-color: rgb(255, 223, 219);">'
        html += '<div style="display: flex; flex-direction:column; justify-content: center; align-items: center;">' # 아이템 중앙정렬
        html += f'<h3>삭제 시간: {time.ctime(nTime)}</h3>'
        html += '<p>lightTable를 삭제했습니다.</p>'
        html += '</body></html>' #버튼 클릭시 input태그의 value를 가져오고 window객체의 location함수를 통하여 이동
        self.writeHtml(html)
    
    # servo관련 메소드
    def writeServoMove(self, ang):
        self.writeHead(200)#200:성공
        nTime = time.time()
        self.server.gateway.setServoMove(ang)
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>모터 이동</title>'
        html += '</head><body style="background-color: rgb(255, 223, 219);">'
        html += '<div style="display: flex; flex-direction:column; justify-content: center; align-items: center;">' # 아이템 중앙정렬
        html += f'<h3>이동 시작 시간: {time.ctime(nTime)}</h3>'
        html += f'<p>모터를 {ang}도 위치로 이동했습니다.</p>'
        html += '<h5>사용자 각도 설정</h5>'
        # 입력 타입 number 0~180으로 제한
        html += f'<div><input type="number" id="angle" placeholder="0~180내의 각도를 입력" min="0" max="180" step="1" value="{ang}">'  
        html += '<button onclick="move()">이동</button></div></div>'
        html += '<script>'
        html += 'function move() {'
        html += 'var angle = document.getElementById("angle").value;'
        html += 'var currentHost = window.location.hostname;'
        html += 'var currentPort = window.location.port;'
        html += 'window.location.href = "http://" + currentHost + ":" + currentPort + "/servo_move?ang=" + angle;'
        html += '}'
        html += '</script></body></html>' #버튼 클릭시 input태그의 value를 가져오고 window객체의 location함수를 통하여 이동
        self.writeHtml(html)

    def writeCustomServoMove(self, qs):
        qdict = parse.parse_qs(qs)
        nAng = int(qdict['ang'][0])
        if 0 <= nAng <= 180:
            self.writeServoMove(nAng) #쿼리스트링의 각도만큼 이동
        else:
             # 유효하지 않은 각도에 대한 응답 전송
            self.writeHead(404) # 404: not found
            html = '<html><head>'
            html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
            html += '<title>각도오류</title>'
            html += '</head><body style="background-color: rgb(255, 223, 219);">'
            html += f'<div><h3>0~180의 각도설정만 유효합니다.</h3></div>'
            html += '</body></html>'
            self.writeHtml(html)
        
    #led 메소드
    def writeSetLed(self,qs):
        qdict = parse.parse_qs(qs)
        color = qdict['color'][0]
        self.writeHead(200)#200:성공
        nTime = time.time()
        self.server.gateway.setLedColor(color)
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>led 설정</title>'
        html += '</head><body style="background-color: rgb(255, 223, 219);">'
        html += '<div style="display: flex; flex-direction:column; justify-content: center; align-items: center;">' # 아이템 중앙정렬
        html += f'<h3>점등 시간: {time.ctime(nTime)}</h3>'
        html += f'<p>led를 {color}색상으로 설정했습니다.</p>'
        html += '<h5>사용자 led 설정</h5>'
        html += ''' <select id="colors" name="colors"> 
        <option value="red">Red</option>
        <option value="green">Green</option>
        <option value="blue">Blue</option>
        <option value="yellow">Yellow</option>
        <option value="pink">Pink</option>
        <option value="cyan">Cyan</option>
        <option value="black">Black</option>
        <option value="white">White</option>
        </select>''' #option태그 사용
        html += ' <button onclick="setLedColor()">설정</button>'
        html += '<script>'
        html +='function setLedColor() {'
        html += 'var optionColor = document.getElementById("colors").value;'
        html += 'var currentHost = window.location.hostname;'
        html += 'var currentPort = window.location.port;'
        html += 'window.location.href = "http://" + currentHost + ":" + currentPort + "/led?color=" + optionColor;'
        html += '}'
        html += '</script></body></html>' #버튼 클릭시 select태그의 option value를 가져오고 window객체의 location함수를 통하여 이동
        self.writeHtml(html)

    #buzzer
    def writeBuzzer(self, qs):
        qdict = parse.parse_qs(qs)
        note = qdict['note'][0]
        nDelay = int(qdict['delay'][0])
        self.writeHead(200)#200:성공
        self.server.gateway.setBuzzerNote(note,nDelay)
        html = '<html><head>'
        html += '<meta http-equiv="content-type" content="text/html" charset="UTF-8">'
        html += '<title>Buzzer 설정</title>'
        html += '</head><body style="background-color: rgb(255, 223, 219);">'
        html += '<div style="display: flex; flex-direction:column; justify-content: center; align-items: center;">' # 아이템 중앙정렬
        html += f'<h3>울림 시간: {nDelay}</h3>'
        html += f'<p>Buzzer를 {note}음으로 설정했습니다.</p>'
        html += '<h5>사용자 Buzzer 설정</h5>'
        html += '<div style="display:flex">'
        html += '''<button onclick="buzz('do')">도</button><button onclick="buzz('re')">레</button>
        <button onclick="buzz('mi')">미</button><button onclick="buzz('fa')">파</button>
        <button onclick="buzz('sol')">솔</button><button onclick="buzz('la')">라</button>
        <button onclick="buzz('si')">시</button>'''#음계버튼
        html += '<script>'
        html += 'function buzz(note){'
        html += 'var currentHost = window.location.hostname;'
        html += 'var currentPort = window.location.port;'
        html += 'window.location.href = "http://" + currentHost + ":" + currentPort + "/buzzer?note="+note+"&delay=200";'
        html += '}'
        html += '</script></body></html>' #버튼 클릭시 해당 note로 울림
        self.writeHtml(html)
        