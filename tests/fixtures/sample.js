import { readFile } from "fs";

class Animal {
  constructor(name) {
    this.name = name;
  }

  speak() {
    return "";
  }
}

class Dog extends Animal {
  speak() {
    return "Woof";
  }
}

function greet(name) {
  return `Hello, ${name}`;
}
