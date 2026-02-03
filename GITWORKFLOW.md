# Gitflow Workflow для Telegram Dating Bot

## Ветки в проекте

### Основные ветки

**main** (или master) - продуктивная ветка
- Содержит стабильный код, который работает в продакшене
- Только готовые функционалы, прошедшие тестирование
- Merge из ветки develop только через Pull Request

**develop** - ветка разработки
- Основная ветка для разработки новых функций
- Содержит последние изменения для следующего релиза
- Merge из feature веток

### Временные ветки

feature/* - ветки для новых функций
```
git checkout -b feature/user-authentication
git checkout -b feature/matching-algorithm
```

bugfix/* - ветки для исправления ошибок в продакшене
```
git checkout -b bugfix/photo-upload-failure
```

hotfix/* - срочные исправления в продакшене
```
git checkout -b hotfix/critical-security-fix
```

## Процесс работы

### Разработка новой функции

1. Создать ветку от develop:
```bash
git checkout develop
git pull origin develop
git checkout -b feature/new-feature-name
```

2. Разработка изменений в ветке feature:
```bash
git add .
git commit -m "Add new feature: description"
```

3. Запушить ветку в GitHub:
```bash
git push origin feature/new-feature-name
```

4. Создать Pull Request на GitHub из feature в develop
5. Пройти код-ревью и объединить (merge)

### Исправление бага

1. Для бага в продакшене (main):
```bash
git checkout main
git pull origin main
git checkout -b bugfix/bug-description
```

2. Для бага в разработке (develop):
```bash
git checkout develop
git pull origin develop
git checkout -b feature/bugfix-description
```

3. После исправления - создать PR

### Срочное исправление (hotfix)

1. Создать ветку от main:
```bash
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix
```

2. Исправить проблему и создать PR в main
3. После слияния - перенести исправление в develop

## Команды для работы

### Просмотр веток
```bash
git branch -a              # Все ветки
git branch                 # Локальные ветки
git status                # Текущий статус
```

### Слияние изменений
```bash
git checkout develop
git pull origin develop
git merge feature/new-feature-name
git push origin develop
```

### Удаление веток
```bash
# После слияния PR
git branch -d feature/new-feature-name         # Удалить локальную
git push origin --delete feature/new-feature-name  # Удалить удаленную
```

### Решение конфликтов при merge

1. Если возник конфликт при merge:
```bash
git checkout develop
git merge feature/new-feature-name
# Исправить конфликты в файлах
git add .
git commit -m "Merge feature/new-feature-name (resolve conflicts)"
git push origin develop
```

## Правила коммитов

### Стиль сообщений

```
<тип>: <краткое описание>

<полное описание (опционально)>

<ссылки на issues (опционально)>
```

### Типы коммитов

- **feat** - новая функция
- **fix** - исправление бага
- **docs** - изменения в документации
- **style** - форматирование кода (без изменения логики)
- **refactor** - рефакторинг кода
- **perf** - оптимизация производительности
- **test** - добавление тестов
- **chore** - обновление зависимостей, конфигурации

### Примеры

```
feat: add user authentication via Telegram

Users can now sign in using their Telegram accounts,
which improves security and simplifies onboarding.

Closes #123
```

```
fix: resolve photo upload timeout error

The upload timeout was increased from 30s to 60s
to handle slower network connections.
```

```
refactor: improve database service class

Extracted user operations into separate methods
for better testability and maintainability.
```

## Безопасная работа в ветках

### Перед началом работы
```bash
git pull origin develop      or    git pull origin main
```

### Перед созданием PR
```bash
# Обновить ветку develop перед merge
git checkout develop
git pull origin develop
git checkout feature/new-feature
git merge develop
```

### Защита веток (настройки на GitHub)

**main** ветка:
- Require pull request before merging (требуется PR)
- Require status checks to pass before merging (тесты)
- Include administrators (админы могут миновать проверки)

**develop** ветка:
- Require pull request before merging (требуется PR)
- Require approvals (требуется 1 approval)

## Пример рабочей сессии

### Сценарий: Добавление новой функции "Фильтр по возрасту"

```bash
# 1. Переключиться на develop и обновить
git checkout develop
git pull origin develop

# 2. Создать feature ветку
git checkout -b feature/age-filter

# 3. Разработка
# ... работаем над кодом ...
git add .
git commit -m "feat: add age filter for user profiles"

# 4. Пуш и создание PR
git push origin feature/age-filter
# Создать PR на GitHub: feature/age-filter -> develop

# 5. После одобрения PR
git checkout develop
git pull origin develop
git branch -d feature/age-filter
```

## Полезные ссылки

- Репозиторий: https://github.com/rusvrn8/telegram-dating-bot
- Документация GitHub: https://docs.github.com
- Gitflow руководство: https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow
