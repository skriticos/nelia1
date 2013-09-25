all: clean
	/usr/bin/env python3 src/run.py

debug: clean
	/usr/bin/env python3 src/run.py -debug

clean:
	rm -rf ~/.config/nelia1
	find . -name __pycache__ -exec rm -rf {} \; || true

