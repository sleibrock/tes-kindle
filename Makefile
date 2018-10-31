PY=python
MAIN=main.py
PIP=pip
RM=rm
OUT=out

setup:
	$(PIP) install -r requirements.txt

run:
	$(PY) $(MAIN)

test:
	$(PY) $(MAIN) -t

clean:
	$(RM) -f out 


archive:
	zip out

# end
