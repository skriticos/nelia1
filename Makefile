all: clean
	/usr/bin/env python3 src/run.py

debug: clean
	/usr/bin/env python3 src/run.py -debug

clean:
	rm -rf ~/.config/nelia1
	find . -name __pycache__ -exec rm -rf {} \; || true

# package:
# 	# orig, folder, debian edits
# 	dpkg-buildpackage -us -uc -S
# 	sudo pbuilder --build nelia1_1.0-2.dsc
# 	/var/cache/pbuilder/result/nelia1_1.0*
