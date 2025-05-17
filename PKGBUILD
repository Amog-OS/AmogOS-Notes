# Maintainer: techtimefor
pkgname=amogos-notes-git
pkgver=1.0.alpha
pkgrel=1
pkgdesc="A modern, feature-rich notes app designed for AmogOS — lightweight, fast, and efficient."
arch=('i686' 'x86_64' 'armv7h' 'aarch64' 'pentium4' 'i486')
url="https://github.com/Amog-OS/AmogOS-Notes"
license=('GPL')
depends=('python' 'python-pyqt6' 'python-pyqt6-sip' 'python-beautifulsoup4' 'pyinstaller')
makedepends=('git')
source=("$pkgname-$pkgver.tar.gz::https://github.com/Amog-OS/AmogOS-Notes/archive/refs/heads/main.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$srcdir/AmogOS-Notes-main"

    pyinstaller --name=amogos-notes --onefile main.py --icon=images/Amogus.png
}

package() {
    cd "$srcdir/AmogOS-Notes-main"

    install -Dm755 "dist/amogos-notes" "$pkgdir/usr/bin/amogos-notes"
    install -Dm644 "images/Amogus.png" "$pkgdir/usr/share/pixmaps/amogos-notes.png"

    install -Dm644 /dev/stdin "$pkgdir/usr/share/applications/amogos-notes.desktop" <<EOF
[Desktop Entry]
Name=AmogOS Notes
Exec=amogos-notes
Icon=amogos-notes
Type=Application
Categories=Utility;
EOF
}
