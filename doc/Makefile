cur_dir = $(shell pwd)

all: html

html:
	echo cur_dir: $(cur_dir)
	export PYTHONPATH=$$PYTHONPATH:$(cur_dir):$(cur_dir)/../; sphinx-build -b html -d _build/doctrees . _build/html > .stdout 2> .stderr 

