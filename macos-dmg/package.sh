#!/bin/bash
#
# Package script for Gaphor.
#
# Thanks: http://stackoverflow.com/questions/1596945/building-osx-app-bundle

set -euo pipefail

# Also fix $INSTALLDIR/MacOS/gaphor in case this number changes
APP=Gaphor.app
INSTALLDIR=$APP/Contents
LIBDIR=$INSTALLDIR/lib

LOCALDIR=/usr/local

function log() {
  echo $* >&2
}

libffi_path="$(brew ls libffi | grep pkgconfig | xargs dirname)"
echo "Adding libffi pkg-config path ${libffi_path} to \$PKG_CONFIG_PATH"
export PKG_CONFIG_PATH="${libffi_path}:${PKG_CONFIG_PATH:-}"

rm -rf Gaphor.app Gaphor-*.dmg Gaphor-*-macos.zip

mkdir -p ${INSTALLDIR}/MacOS
mkdir -p ${INSTALLDIR}/Resources

cp Info.plist ${INSTALLDIR}
cp PkgInfo ${INSTALLDIR}
cp gaphor ${INSTALLDIR}/MacOS
cp gaphor.icns ${INSTALLDIR}/Resources

log "Building venv for app bundle..."

python3 -m venv --prompt Gaphor.app --copies ${INSTALLDIR}

source ${INSTALLDIR}/bin/activate

function rel_path {
  echo $1 | sed 's#/usr/local/Cellar/[^/]*/[^/]*/##'
}

{
  brew deps gtk+3
  echo "python"
  brew deps python
} | sort | uniq -u |\
while read dep
do
  log "Scanning Homebrew files for $dep"
  brew list -v $dep
done |\
grep -v '^find ' |\
while read f
do
  echo "$(rel_path $f) $f"
done |\
grep '^lib/\|share/gir-1.0/\|share/locale/\|Frameworks/' |\
while read rf f
do
  log "Adding ${INSTALLDIR}/${rf}"
  mkdir -p "${INSTALLDIR}/$(dirname $rf)"
  test -L "$f" || cp $f "${INSTALLDIR}/${rf}"
done

# grep -v '^[^/]* ' |\
# grep -v '^share/doc/' |\
# grep -v '^share/gtk-doc/' |\
# grep -v '^share/gettext/' |\
# grep -v '^share/emacs/' |\
# grep -v '^share/man/' |\
# grep -v '^include/' |\

# # Check with Homebrew which version to pick
# cp /usr/local/lib/libgtk-3.0.dylib ${INSTALLDIR}/lib
# cp /usr/local/lib/libgobject-2.0.0.dylib ${INSTALLDIR}/lib


# Modules, config, etc.
# for dir in etc/fonts etc/gtk-3.0 lib/gtk-3.0 lib/gdk-pixbuf-2.0 lib/girepository-1.0 share/gir-1.0 share/themes/Default/gtk-3.0; do
#   mkdir -p ${INSTALLDIR}/$dir
#   cp -r ${LOCALDIR}/$dir/* ${INSTALLDIR}/$dir
# done


# Somehow files are writen with mode 444
find $INSTALLDIR -type f -exec chmod u+w {} \;

function resolve_deps {
  local lib=$1
  local dep
  otool -L $lib | grep -e "^.$LOCALDIR/" |\
      while read dep _; do
    echo $dep
  done
}

function fix_paths {
  local lib=$1
  log Fixing $lib
  for dep in `resolve_deps $lib`; do
    #log Fixing `basename $lib`
    log "|  $dep"
    install_name_tool -change $dep @executable_path/../lib/`basename $dep` $lib
  done
}

{
  find $INSTALLDIR -type f -name '*.so'
  find $INSTALLDIR -type f -name '*.dylib'
} |\
while read lib
do
  fix_paths $lib
done

cp /usr/local/bin/gdk-pixbuf-query-loaders ${INSTALLDIR}/bin
fix_paths ${INSTALLDIR}/bin/gdk-pixbuf-query-loaders
log "Installing Gaphor in ${INSTALLDIR}..."

pip install ../dist/gaphor-*.tar.gz

# Package it up!

VERSION=`find . -name 'gaphor*egg' | sed -e 's|.*/gaphor-||' -e 's|-py.*egg$||'`
zip -r Gaphor-$VERSION-macos.zip $APP
hdiutil create -srcfolder $APP Gaphor-$VERSION.dmg
