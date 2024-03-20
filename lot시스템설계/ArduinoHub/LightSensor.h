#pragma once

#include "Voltmeter.h"

#define DEF_LIGHT_PORT	(A1) // default값 정의

enum LightState // 열거형(enumeration) 상수 정의
{
	LS_BRIGHT = 350, LS_AMBIENT = 700, LS_DARK = 900
};

class LightSensor : public Voltmeter // Voltmeter 클래스를 public으로 상속받아(:) LightSensor 클래스 구현
{
public:
	LightSensor(void) { setPort(DEF_LIGHT_PORT); } // setPort()는 LightSensor에 정의되지 않음; setPort()는 부모 클래스인 Voltmeter에 정의
	~LightSensor() {}

	int getLightStep(void) const { return getVoltStep(); }
	LightState getLightState(void) const
	{
		int nLight = getLightStep();
		if (nLight <= LS_BRIGHT) return LS_BRIGHT;
		else if (nLight <= LS_AMBIENT) return LS_AMBIENT;
		else return LS_DARK;
	}
	String lightStateToStr(LightState nState) const
	{
		switch (nState)
		{
		case LS_BRIGHT: return "bright";
		case LS_AMBIENT: return "ambient";
		default: return "dark";
		}

	}

private:
};
