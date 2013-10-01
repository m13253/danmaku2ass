
.PHONY: all install clean uninstall

DESTDIR=
PREFIX=/usr/local

CP=cp
INSTALL=install
MKDIR=mkdir -p
PYTHON=python3
RM=rm -f -v

all:

install:
	$(INSTALL) -Dm0755 danmaku2ass.py "$(DESTDIR)$(PREFIX)/bin/danmaku2ass"
	$(MKDIR) "$(DESTDIR)$(PREFIX)/share"
	$(CP) -R locale "$(DESTDIR)$(PREFIX)/share/"

clean:
	$(RM) -R __pycache__

uninstall:
	$(RM) "$(DESTDIR)$(PREFIX)/bin/danmaku2ass"
	$(RM) "$(DESTDIR)$(PREFIX)/share/locale/"*"/LC_MESSAGES/danmaku2ass."*

