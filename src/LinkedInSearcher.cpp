#include <iostream>

using namespace std;

int main() {
	system("@echo off");
	system("cd /D %~dp0");
	system("pip install -r src/requirements.txt");
	system("cls");
	system("python src/Main.py");
	system("ping 127.0.0.1 -n 100 > nul");
	system("@echo off");
}