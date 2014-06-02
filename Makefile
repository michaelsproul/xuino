# Installer for Xuino.
# Run `sudo make install` to install.

# The directory to use as the filesystem root.
DESTDIR = ""

# The directory to install the main xuino components in.
XUINO_DIR = ${DESTDIR}/usr/share/xuino

# The desired path for the xuino binary (it will be symlinked to $XUINO_DIR/xuino.py)
XUINO_BIN = ${DESTDIR}/usr/bin/xuino

# The location of Python 3's site packages.
# A symlink is created in this folder so that xuino can be imported by other python programs.
SITE_PACKAGES = ${DESTDIR}/usr/lib/python3.4/site-packages

install: uninstall
	@echo 'Installing...'
	@# Install xuino files
	@mkdir -p $(XUINO_DIR)
	@cp -r * $(XUINO_DIR)
	@# Install xuino binary
	@chmod +x $(XUINO_DIR)/xuino.py
	@mkdir -p `dirname $(XUINO_BIN)`
	@ln -s $(XUINO_DIR)/xuino.py $(XUINO_BIN)
	@# Install xuino python package
	@mkdir -p $(SITE_PACKAGES)
	@ln -s $(XUINO_DIR)/xuino.py $(SITE_PACKAGES)/xuino.py
	@echo 'Done!'

uninstall:
	@echo 'Uninstalling...'
	@rm -rf $(XUINO_DIR)
	@rm -f $(XUINO_BIN)
	@rm -f $(SITE_PACKAGES)/xuino.py
	@echo 'Done!'

.PHONY: install update uninstall
