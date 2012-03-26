crossflip.exe: crossflip.cpp 
	g++ -o crossflip.exe crossflip.cpp -O3

.PHONY : tags
tags:
	rm -f tags
	ctags -R .

.PHONY : clean
clean:
	find . -type f | sed -n '/\~$$/p; /\.pyc$$/p; /\.swp$$/p' | xargs rm -f 
	rm -f *.stackdump
	rm -f tags
	rm -f crossinput.txt crossoutput.txt crossflip.exe
