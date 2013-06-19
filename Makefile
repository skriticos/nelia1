all:
	/usr/bin/env python3 src/run.py

clean:
	rm -rf ~/.config/nelia1
	find . -name __pycache__ -exec rm -rf {} \;

.PHONY: test
test:
	/usr/bin/env python3 test/test_mpushbutton.py

