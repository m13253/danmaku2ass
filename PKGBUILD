# PKGBUILD file for Arch Linux packaging
# Contributor: Star Brilliant <echo bTEzMjUzQGhvdG1haWwuY29tCg== | base64 -d>

pkgname=danmaku2ass-git
pkgver=0
pkgrel=1
pkgdesc="Convert comments from Niconico/AcFun/bilibili to ASS format"
arch=('any')
url="https://github.com/m13253/danmaku2ass"
license=('GPL3')
depends=('python>=3')
makedepends=('git')
provides=('danmaku2ass')
conflicts=('danmaku2ass')
source=('danmaku2ass::git+https://github.com/m13253/danmaku2ass.git')
md5sums=('SKIP')

pkgver() {
  cd "$srcdir/danmaku2ass"
  git log -1 --format="%cd" --date=short | tr -d -
}

build() {
  cd "$srcdir/danmaku2ass"
  make
}

package() {
  cd "$srcdir/danmaku2ass"
  make install DESTDIR="$pkgdir" PREFIX=/usr
}
