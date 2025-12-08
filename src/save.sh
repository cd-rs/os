rm *.bak
quarto render
git add -A
git commit -a -m "scripted autocommit"
git push
