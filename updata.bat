@echo off
echo 执行中

python manager.py

git add .

git commit -m "chore: article update %DATE%T%TIME%"

git push -u origin main

echo 按任意键退出
pause >nul
