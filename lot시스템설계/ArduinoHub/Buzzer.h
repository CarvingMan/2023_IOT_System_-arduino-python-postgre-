#pragma once

#define DEF_BUZZER_PORT	(8)

enum NoteType
{
	NT_DO = 523, NT_RE = 587, NT_MI = 659, NT_FA = 698, NT_SOL = 784, NT_LA = 880, NT_SI = 988
};

class Buzzer
{
public:
	Buzzer(void) { setPort(DEF_BUZZER_PORT); }
	~Buzzer() {}

	void setPort(int nPort) { m_nPort = nPort; }
	void setup(void) { initBuzzer(); }
	void play(int nNote, int nTime)
	{
		tone(m_nPort, nNote, nTime);
		delay(nTime);
	}

private:
	int m_nPort;

	void initBuzzer(void)
	{
		pinMode(m_nPort, OUTPUT);
	}
};