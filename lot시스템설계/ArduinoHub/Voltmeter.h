#pragma once // 이 헤더 파일은 한 번만(once) include; #pragma(pragmatic, 개선하는)

#define DEF_VOLT_PORT	(A0)

// 헤더 파일 이름과 클래스 이름을 동일하게 만듦(권고)
// 객체(object): 문제를 풀기 위한 자료 구조를 가진 코드의 기본 구조
class Voltmeter // 클래스(객체의 설계도) 정의 -> 객체 만들기
{
public: // 아래 코드는 모두 public member
	// 생성자(constructor): 클래스 이름과 동일한 이름 사용
	Voltmeter(void) { setPort(DEF_VOLT_PORT); }
	// 파괴자(destructor): 클래스 이름과 동일한 이름 사용; 함수명 앞에 ~를 사용
	~Voltmeter() {}
	// 생성자는 인스턴스가 생길 때(new) 호출; 파괴자 함수는 인스턴스가 파괴될 때(delete) 호출
	// 인스턴스(instance): 클래스를 생성한 결과물

	// public method(멤버 함수): class 외부에서 호출할 수 있는 함수
	void setPort(int nPort) { m_nPort = nPort; } // const 붙이면 안됨: m_nPort가 변경되고 있음
	int getVoltStep(void) const { return analogRead(m_nPort); } // const 의미: 현재 method는 property를 변경하지 않음(constant)
	double getVolt(void) const { return 5. / 1023. * getVoltStep(); } // 현재 전압값을 반환

private: // 아래 코드는 모두 private member(class 외부에서 접근 불가능, class 내부에서만 접근 가능)
	// private property(멤버 변수)
	int m_nPort; // m_: member란 뜻
};