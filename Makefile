all:
	/usr/bin/env python3 src/run.py

clean:
	find . -name __pycache__ -exec rm -rf {} \; 2>/dev/null

