
#pragma once

#include "StringTok.h"
#include "Voltmeter.h"
#include "LightSensor.h"
#include "MyServo.h"
//#include "DcMotor.h"
#include "RgbLed.h"
#include "Buzzer.h"

class ArduinoHub
{
public:
	ArduinoHub(void) {}
	~ArduinoHub() {}

	void setup(void) // actuator �ʱ�ȭ
	{
		m_myServo.setup();
		//m_dcMotor.setup();
		m_rgbLed.setup();
		m_buzzer.setup();
	}

	void start(void)
	{
		while (1) // 무한 반복
		{
			m_stInput.appendSerial();
			if (m_stInput.hasLine()) // 명령어 정상 입력
				exeCmd(); // 명령어 실행
		}
	}

	void exeCmd(void)
	{
		//Serial.println("input = [" + m_stInput.toString() + "]");
		String sToken = m_stInput.cutToken().toString();
		//Serial.println("token #1 = [" + sToken + "]");
		if (sToken == "get") exeGet();
		else if (sToken == "set") exeSet();
		else m_stInput.cutLine(); // 잘못된 명령 -> 현재 줄을 삭제
	}

	void exeGet(void) // get 명령어 실행
	{
		// 1. 전압 읽기: get(#1) volt(#2)
		// 2-1. 조도 상태 읽기 : get(#1) light(#2)
		// 2-2. 조도 스텝 읽기 : get(#1) lightstep(#2)
		String sToken = m_stInput.cutToken().toString();
		//Serial.println("token #2 = [" + sToken + "]");
		if (sToken == "volt") exeVolt();
		else if (sToken == "light") exeLight();
		else if (sToken == "lightstep") exeLightStep();
		else m_stInput.cutLine();
	}

	void exeVolt(void)
	{
		double volt = m_voltmeter.getVolt();
		Serial.println(String(volt, 10)); // Serial에 출력
	}

	void exeLight(void)
	{
		int nLightState = m_lightSensor.getLightState();
		String sLightState = m_lightSensor.lightStateToStr(nLightState);
		Serial.println(sLightState);
	}

	void exeLightStep(void)
	{
		int nLightState = m_lightSensor.getLightStep();
		Serial.println(nLightState);
	}

	void exeSet(void) // set 명령어 실행
	{
		// 3-1. 서보 모터 구동: set servo #pos (#pos: 각도를 숫자(#)로 입력)
		// 3-2. DC 모터 구동 : set dcmotor #pos(#pos: 각도를 숫자(#)로 입력)
		// 4. 3색 LED 출력 : set led color(color : 색깔 문자열)
		// 5. 부저 출력 : set buzzer note #delay(note: 음정 문자열, #delay : 음 지속 시간을 msec)
		String sToken = m_stInput.cutToken().toString();

		if (sToken == "servo") exeServo();
		else if (sToken == "led") exeLed();
		else if (sToken == "buzzer") exeBuzzer();
		else m_stInput.cutLine();
	}


	void exeServo(void) {
		String sToken = m_stInput.cutToken().toString();

		int nToken = sToken.toInt();

		if (nToken >= 0 && nToken <= 180) { //형변환 한 토큰이 0 이상 180 이하이면,
			m_myServo.move(nToken);
		}
		else m_stInput.cutLine();
	}
	
	// led 설정
	void exeLed(void)
	{
		String sToken = m_stInput.cutToken().toString();

		if (sToken == "red")
		{
			m_rgbLed.turnRed(true);
			
		}
		else if(sToken == "green")
		{
			m_rgbLed.turnGreen(true);
			
		}
		else if(sToken == "blue")
		{
			m_rgbLed.turnBlue(true);
			
		}
		else if (sToken == "yellow")
		{
			m_rgbLed.turnRgb(CT_YELLOW);
			
		}
		else if (sToken == "pink")
		{
			m_rgbLed.turnRgb(CT_PINK);
			
		}
		else if (sToken == "cyan")
		{
			m_rgbLed.turnRgb(CT_CYAN);
			
		}
		else if (sToken == "white")
		{
			m_rgbLed.turnRgb(CT_WHITE);
		}
		else if (sToken == "black")
		{
			m_rgbLed.turnRgb(CT_BLACK);
		}
		else m_stInput.cutLine();
	}


	void exeBuzzer(void) {
		//String sToken = m_stInput.cutToken().toString();
		int nNote = exeNote(); // 정수값을 받음 이미 exeNote()에서 한번 cut 해서 하나 남음
		String sToken = m_stInput.cutToken().toString();
		//if(sToken.toInt > 0 ) 만약에 숫자가 아니라 문자열로 적었다면? 아스키 코드값이 형 변환 되어서 난리난다.

		int nDelay = sToken.toInt();
		
		if (nDelay > 0 && nDelay <= 10000) { //아스키 코드 값이 형 변환되어 너무 오래하는 것을 방지
			m_buzzer.play(nNote, nDelay);
		}
		else m_buzzer.play(nNote, 1000); // 값이 정확하지 않을 시에는 1000밀리초로 통일한다. 0으로 입력해도 무한으로 들린다.
	}

	int exeNote()
	{
		String sToken = m_stInput.cutToken().toString();
		if (sToken == "do") {
			return NT_DO;
		}
		else if (sToken == "re")
		{
			return NT_RE;
		}
		else if (sToken == "mi")
		{
			return NT_MI;
		}
		else if (sToken == "fa")
		{
			return NT_FA;
		}
		else if (sToken == "sol")
		{
			return NT_SOL;
		}
		else if (sToken == "la")
		{
			return NT_LA;
		}
		else if (sToken == "si")
		{
			return NT_SI;
		}
		else m_stInput.cutLine();

	}


private:
	StringTok m_stInput;
	Voltmeter m_voltmeter;
	LightSensor m_lightSensor;
	MyServo m_myServo;
	//DcMotor m_dcMotor;
	RgbLed m_rgbLed;
	Buzzer m_buzzer;
};