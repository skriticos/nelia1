all:
	/usr/bin/env python3 src/run.py

test:
	/usr/bin/env python3 src/run_test.py

clean:
	rm -rf ~/.config/nelia1
	find . -name __pycache__ -exec rm -rf {} \;

