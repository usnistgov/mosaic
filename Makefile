RM=rm -rf

all: depend math-iface

clean: clean-depend clean-math-iface

# build dependencies
depend:
	bash dependencies/.scripts/build-numpy-sh
	bash dependencies/.scripts/build-scipy-sh
	bash dependencies/.scripts/build-zmq-sh
	bash dependencies/.scripts/build-pyzmq-sh
	bash dependencies/.scripts/build-matplotlib-sh
	bash dependencies/.scripts/build-lmfit-sh
	bash dependencies/.scripts/build-uncertainties-sh
	bash dependencies/.scripts/build-nose-sh
	bash dependencies/.scripts/set-env-sh

math-iface:
	cp mathematica/MathInterface.m ~/Library/Mathematica/Applications/
	
clean-math-iface:
	rm ~/Library/Mathematica/Applications/MathInterface.m
	
clean-depend:
	$(RM) dependencies/lib dependencies/bin dependencies/include dependencies/man dependencies/share dependencies/ticpp/.obj
	sh dependencies/.scripts/unset-env-sh
