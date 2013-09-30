
.PHONY: all install clean uninstall

PREFIX=/usr/local

CP=cp
INSTALL=install
MKDIR=mkdir -p
PYTHON=python3
RM=rm -f -v

all:

install:
	$(INSTALL) -Dm0755 danmaku2ass.py "$(PREFIX)/bin/danmaku2ass"
	$(MKDIR) "$(PREFIX)/share"
	$(CP) -R locale "$(PREFIX)/share/"

clean:
	$(RM) danmaku2ass.pyo

uninstall:
	$(RM) "$(PREFIX)/bin/danmaku2ass"
	$(RM) "$(PREFIX)/share/locale/"*"/LC_MESSAGES/danmaku2ass."*

