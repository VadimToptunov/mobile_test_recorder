#!/bin/bash
# Быстрый старт - применение всех улучшений

echo "🚀 Mobile Test Recorder - Применение улучшений"
echo "=============================================="
echo

# Проверка текущей ветки
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null)
echo "📍 Текущая ветка: $CURRENT_BRANCH"
echo

if [ "$CURRENT_BRANCH" != "feature/production-ready-improvements" ]; then
    echo "⚠️  Вы не на ветке улучшений!"
    echo "   Переключитесь: git checkout feature/production-ready-improvements"
    echo
    read -p "Переключиться автоматически? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout feature/production-ready-improvements
    else
        exit 1
    fi
fi

echo "✅ Проверка улучшений..."
python verify_improvements.py

if [ $? -ne 0 ]; then
    echo
    echo "❌ Проверка не прошла! Исправьте ошибки перед merge."
    exit 1
fi

echo
echo "🎯 Выберите вариант merge:"
echo "1) Fast-forward merge (рекомендуется)"
echo "2) Merge commit (сохраняет историю)"
echo "3) Squash merge (один чистый коммит)"
echo "4) Отмена"
echo

read -p "Ваш выбор (1-4): " choice

case $choice in
    1)
        echo "📦 Fast-forward merge..."
        git checkout main
        git merge feature/production-ready-improvements
        ;;
    2)
        echo "📦 Merge commit..."
        git checkout main
        git merge --no-ff feature/production-ready-improvements -m "Merge production-ready improvements"
        ;;
    3)
        echo "📦 Squash merge..."
        git checkout main
        git merge --squash feature/production-ready-improvements
        git commit -m "feat: production-ready improvements

✅ Fix all critical errors (imports, security, types)
🆕 Add CI/CD pipeline, pre-commit hooks, security module
⚡ Implement Rust core fallback (16-90x speedup)
📚 Add comprehensive documentation"
        ;;
    4)
        echo "❌ Отменено"
        exit 0
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    echo
    echo "✅ Merge завершен успешно!"
    echo
    echo "🎯 Следующие шаги:"
    echo
    echo "1. Настроить environment:"
    echo "   cp .env.example .env"
    echo "   nano .env"
    echo
    echo "2. Установить pre-commit hooks:"
    echo "   pip install pre-commit"
    echo "   pre-commit install"
    echo
    echo "3. Запустить тесты:"
    echo "   pytest tests/ -v"
    echo
    echo "4. Собрать Rust core (опционально):"
    echo "   cd rust_core && pip install maturin && maturin develop --release"
    echo
    echo "5. Проверить CLI:"
    echo "   observe info"
    echo "   observe health"
    echo
    echo "🎉 Готово! Проект готов к production!"
else
    echo
    echo "❌ Merge failed! Проверьте конфликты."
    echo "   git status"
    echo "   git diff"
fi
