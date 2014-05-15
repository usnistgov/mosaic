RM=rm -rf

all: depend math-iface

clean: clean-math-iface

# build dependencies
depend:
	sh dependencies/build-deps-sh

math-iface:
	cp mathematica/nanoporeAnalysis.m ~/Library/Mathematica/Applications/

tests:
	sh install-test-sh
	
clean-math-iface:
	rm ~/Library/Mathematica/Applications/nanoporeAnalysis.m
	
