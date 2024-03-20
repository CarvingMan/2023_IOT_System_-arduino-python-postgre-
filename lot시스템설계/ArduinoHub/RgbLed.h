#pragma once

#define DEF_PORT_R	(5)
#define DEF_PORT_G	(6)
#define DEF_PORT_B	(7)
#define RED_BIT		(1)	// 001
#define GREEN_BIT	(2)	// 010
#define BLUE_BIT	(4)	// 100

// CT_YELLOW == 3 = 1+2+0
// CT_PINK == 5 = 1+0+4
// CT_CYAN == 6 = 0+2+4
// CT_WHITE == 7 = 1+2+4
enum ColorType
{
	CT_BLACK = 0, CT_RED, CT_GREEN, CT_YELLOW, CT_BLUE, CT_PINK, CT_CYAN, CT_WHITE
};

class RgbLed
{
public:
	RgbLed(void) { setPort(DEF_PORT_R, DEF_PORT_G, DEF_PORT_B); } // 생성자
	~RgbLed() {}	// 소멸자, 파괴자

	void setPort(int nPortR, int nPortG, int nPortB)
	{
		m_nPortR = nPortR, m_nPortG = nPortG, m_nPortB = nPortB;
	}
	void setup(void) { initLed(); }
	void turnRed(bool bOn)
	{
		if (bOn) digitalWrite(m_nPortR, HIGH);
		else digitalWrite(m_nPortR, LOW);
	}
	void turnGreen(bool bOn)
	{
		if (bOn) digitalWrite(m_nPortG, HIGH);
		else digitalWrite(m_nPortG, LOW);
	}
	void turnBlue(bool bOn)
	{
		if (bOn) digitalWrite(m_nPortB, HIGH);
		else digitalWrite(m_nPortB, LOW);
	}
	void turnRgb(int nColor) // nColor: 0~7
	{
		int nR = nColor & RED_BIT; // &: 2진수용 비트 단위 AND 연산자
		int nG = nColor & GREEN_BIT;
		int nB = nColor & BLUE_BIT;
		turnRed((nR) ? true : false);
		turnGreen((nG) ? true : false);
		turnBlue((nB) ? true : false);
	}

private:
	int m_nPortR, m_nPortG, m_nPortB; // RGB 포트

	void initLed(void)
	{
		pinMode(m_nPortR, OUTPUT);
		pinMode(m_nPortG, OUTPUT);
		pinMode(m_nPortB, OUTPUT);
	}
};