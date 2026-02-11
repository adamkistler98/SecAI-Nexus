all: build_c build_java

build_c:
	mkdir -p bin
	gcc -o bin/c_scanner src/c/scanner.c -Wall

build_java:
	mkdir -p bin
	javac -d bin src/java/LogAnalyzer.java

clean:
	rm -rf bin/*
