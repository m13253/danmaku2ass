
.PHONY: all install clean uninstall

DESTDIR=
PREFIX=/usr/local

CP=cp
INSTALL=install
LN=ln
MKDIR=mkdir -p
PYTHON=python3
RM=rm -f -v
MSGFMT=msgfmt

all:
	for pofiles in en ja zh_CN zh_TW; do \
		$(MSGFMT) "po/$$pofiles.po" -o "po/$$pofiles.mo" ; \
	done

install:
	$(MKDIR) "$(DESTDIR)$(PREFIX)/share/danmaku2ass"
	$(INSTALL) -m0755 danmaku2ass.py "$(DESTDIR)$(PREFIX)/share/danmaku2ass/danmaku2ass.py"
	for locale in en ja zh_CN zh_TW; do \
		$(MKDIR) "$(DESTDIR)$(PREFIX)/share/locale/$$locale/LC_MESSAGES" ; \
		$(CP) "po/$$locale.mo" "$(DESTDIR)$(PREFIX)/share/locale/$$locale/LC_MESSAGES/danmaku2ass.mo" ; \
	done
	$(MKDIR) "$(DESTDIR)$(PREFIX)/bin"
	$(LN) -sf "$(PREFIX)/share/danmaku2ass/danmaku2ass.py" "$(DESTDIR)$(PREFIX)/bin/danmaku2ass"

clean:
	$(RM) -R __pycache__
	$(RM) po/*.mo

uninstall:
	$(RM) -R "$(DESTDIR)$(PREFIX)/bin/danmaku2ass" "$(DESTDIR)$(PREFIX)/share/danmaku2ass"

