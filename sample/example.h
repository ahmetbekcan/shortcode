#pragma once
#include <string>

class RABBIT_API Log {
public:
    static void Init();
    static void Shutdown();

    static Log& GetLogger();
    void Write(const std::string& msg);
};

class PlainClass {
public:
    void DoSomething();
};
