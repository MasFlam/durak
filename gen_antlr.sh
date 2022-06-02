#!/bin/sh

ANTLR_JAR=antlr/antlr-4.10.1-complete.jar

rm -r src/durak/grammar

cd antlr

java -jar ../"$ANTLR_JAR" DurakLexer.g4 -Dlanguage=Python3 -no-listener -visitor -o ../src/durak/grammar
java -jar ../"$ANTLR_JAR" DurakParser.g4 -Dlanguage=Python3 -no-listener -visitor -o ../src/durak/grammar
