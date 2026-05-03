package main

import "fmt"

type Animal struct {
	Name string
}

func (a *Animal) Speak() string {
	return ""
}

type Dog struct {
	Animal
}

func (d *Dog) Speak() string {
	return "Woof"
}

func Greet(name string) string {
	return fmt.Sprintf("Hello, %s", name)
}
