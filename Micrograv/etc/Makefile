
all: etcmodule.so
.PHONY: all

clean:
	rm *.o *.so

.PHONY: clean

etcmodule.so: etc.c tamura.o
#	g77 -c tatide.f
#	gcc -c tatide.c
	gcc -c etc.c
	gcc -shared etc.o tamura.o -o etcmodule.so -lm

test: testETC.c tatide.c tamura.o
#	g77 -c tatide.f
	gcc -c tatide.c
	gcc -c testETC.c
	gcc -o testETC testETC.o tatide.o tamura.o -lf2c -lm

tatide.c: tatide.f
	f2c tatide.f

tamura.o: tamura.c
	gcc -c tamura.c
