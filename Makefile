
.PHONY: all install clean uninstall

DESTDIR=
PREFIX=/usr/local

CP=cp
INSTALL=install
LN=ln
MKDIR=mkdir -p
PYTHON=python3
RM=rm -f -v

all:

install:
	$(MKDIR) "$(DESTDIR)$(PREFIX)/share/danmaku2ass"
	$(INSTALL) -Dm0755 danmaku2ass.py "$(DESTDIR)$(PREFIX)/share/danmaku2ass"
	$(CP) -R locale "$(DESTDIR)$(PREFIX)/share/danmaku2ass/"
	$(MKDIR) "$(DESTDIR)$(PREFIX)/bin"
	$(LN) -s "$(PREFIX)/share/danmaku2ass/danmaku2ass.py" "$(DESTDIR)$(PREFIX)/bin/danmaku2ass"

clean:
	$(RM) -R __pycache__

uninstall:
	$(RM) -R "$(DESTDIR)$(PREFIX)/bin/danmaku2ass" "$(DESTDIR)$(PREFIX)/share/danmaku2ass"

