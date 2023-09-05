rd /s /q dist
rd /s /q build
pyinstaller packaging/keycap-designer.spec
mkdir dist\.vscode
copy packaging\settings.json dist\.vscode
copy packaging\app.bat dist
copy packaging\edit.bat dist
copy ReadMe.md dist
copy LICENSE dist
xcopy /i content dist\content
xcopy /i content\starter-kit dist\content\starter-kit
xcopy /i font dist\font
xcopy /i layout dist\layout
cd dist
zip -r ../keycap-designer-win.zip *
