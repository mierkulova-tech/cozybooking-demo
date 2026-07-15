

Write-Host "Настраиваю git-фильтр для очистки комментариев..."

git config filter.stripcomments.clean "python strip_comments.py"

git config filter.stripcomments.smudge "cat"

Write-Host "Готово. Применяю фильтр к уже отслеживаемым файлам..."

git add --renormalize .

Write-Host ""
Write-Host "Готово! Дальше работай как обычно:"
Write-Host "  git add ."
Write-Host "  git commit -m '...'"
Write-Host "  git push"
Write-Host ""
Write-Host "Комментарии останутся только у тебя на диске."
Write-Host "Проверить, что реально уйдёт в GitHub, можно так:"
Write-Host "  git show :apps/listings/models/apartment.py"
