# Installer for Squid
# Run `sudo make install` to install

# The directory to install the main squid components in.
DEST = /usr/share/squid

# The desired path for the squid binary (it will be symlinked to $DEST/squid)
SQUID_BIN = /usr/bin/squid

# The location of Python 3's site packages.
# A symlink is created in this folder so that squid can be imported by other python programs.
SITE_PACKAGES = /usr/lib/python3.3/site-packages

install:
	@echo 'Installing...'
	@mkdir -p $(DEST)
	@cp -r * $(DEST)
	@chmod +x $(DEST)/squid.py
	@ln -s $(DEST)/squid.py $(SQUID_BIN)
	@ln -s $(DEST)/squid.py $(SITE_PACKAGES)/squid.py
	@echo 'Done!'

update: uninstall install

uninstall:
	@echo 'Uninstalling...'
	@rm -rf $(DEST)
	@rm -f $(SQUID_BIN)
	@rm -f $(SITE_PACKAGES)/squid.py
	@echo 'Done!'

.PHONY: install update uninstall
