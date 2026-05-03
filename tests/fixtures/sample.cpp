#include <string>

// Regular class
class Animal {
public:
    Animal(const std::string& name);
    virtual std::string speak();
    std::string getName();
};

// DLL-export macro class (common in game engines, frameworks)
class MY_API Log {
public:
    static void Init();
    static void Shutdown();
    static Log& GetInstance();
    void Write(const std::string& msg);
};
