.PHONY: compile, retreive, clean

default: retreive

compile:
	javac -cp twitter4j-core-3.0.3.jar:twitter4j-async-3.0.3.jar:twitter4j-media-support-3.0.3.jar:twitter4j-stream-3.0.3.jar client/*.java 

retreive: compile
	java -cp .:twitter4j-core-3.0.3.jar:twitter4j-async-3.0.3.jar:twitter4j-media-support-3.0.3.jar:twitter4j-stream-3.0.3.jar client/Main

clean:
	rm -f *.class
