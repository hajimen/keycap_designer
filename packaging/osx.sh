#!/bin/sh
rm -rf dist
pyinstaller --clean packaging/keycap-designer.spec
mkdir dist/.vscode
cp packaging/settings.json dist/.vscode
cp packaging/app.sh packaging/edit.sh dist
cp ReadMe.md dist
cp LICENSE dist
chmod a+x dist/*.sh
cp -r content font layout dist/
cd dist
mkdir tmp
zip -r ../keycap-designer-osx.zip * .vscode
