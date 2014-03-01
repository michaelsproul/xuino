# Installer for Xuino.
# Run `sudo make install` to install.

# The directory to install the main xuino components in.
DEST = /usr/share/xuino

# The desired path for the xuino binary (it will be symlinked to $DEST/xuino)
XUINO_BIN = /usr/bin/xuino

# The location of Python 3's site packages.
# A symlink is created in this folder so that xuino can be imported by other python programs.
SITE_PACKAGES = /usr/lib/python3.3/site-packages

install:
	@echo 'Installing...'
	@mkdir -p $(DEST)
	@cp -r * $(DEST)
	@chmod +x $(DEST)/xuino.py
	@ln -s $(DEST)/xuino.py $(XUINO_BIN)
	@ln -s $(DEST)/xuino.py $(SITE_PACKAGES)/xuino.py
	@echo 'Done!'

update: uninstall install

uninstall:
	@echo 'Uninstalling...'
	@rm -rf $(DEST)
	@rm -f $(XUINO_BIN)
	@rm -f $(SITE_PACKAGES)/xuino.py
	@echo 'Done!'

.PHONY: install update uninstall
