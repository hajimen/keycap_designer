#!/bin/sh
rm -rf dist build
pyinstaller packaging/keycap-designer.spec
mkdir dist/.vscode
cp packaging/settings.json dist/.vscode
cp packaging/app.sh packaging/edit.sh dist
cp ReadMe.md dist
cp LICENSE dist
chmod a+x packaging/*.sh
cp -r content font layout dist/
cd dist
zip -r ../keycap-designer-osx.zip * .vscode
