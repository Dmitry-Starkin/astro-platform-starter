# Astro Platform Starter с Приложениями

[Live Demo](https://astro-platform-starter.netlify.app/)

Современный стартер на основе Astro.js, React, Tailwind CSS и [Netlify Core Primitives](https://docs.netlify.com/core/overview/#develop) с готовыми приложениями.

## 🚀 Включенные Приложения

### 1. **Todo Manager** (`/todos`)
- ✅ Добавление и удаление задач
- ✅ Отметка как выполненные/невыполненные
- ✅ Фильтрация (все/активные/завершённые)
- ✅ Локальное сохранение данных
- ✅ Статистика по задачам

### 2. **Заметки** (`/notes`)
- 📋 Создание и редактирование заметок
- 🔍 Поиск по заметкам
- 💾 Автоматическое сохранение
- 📊 Статистика по заметкам
- 🕐 Отслеживание времени создания/изменения

### 3. **Калькулятор** (`/calculator`)
- 🧮 Базовые арифметические операции (+, -, ×, ÷)
- 📱 Современный дизайн в стиле iOS
- ⌨️ Поддержка процентов и смены знака
- 🎨 Красивые анимации и переходы

### 4. **Обзор приложений** (`/apps`)
- 📱 Галерея всех доступных приложений
- 🔧 Информация о технологиях
- 🚀 Быстрые ссылки

## 🛠 Технологический стек

- **Frontend**: Astro 5 + React 18 + TypeScript
- **Стили**: Tailwind CSS 4
- **Хостинг**: Netlify
- **Данные**: LocalStorage (для демо)
- **UI**: Современный responsive дизайн

## 📋 Команды

Все команды выполняются из корневой директории проекта:

| Команда                   | Действие                                         |
| :------------------------ | :----------------------------------------------- |
| `npm install`             | Устанавливает зависимости                        |
| `npm run dev`             | Запускает dev сервер на `localhost:4321`         |
| `npm run build`           | Собирает продакшн версию в `./dist/`             |
| `npm run preview`         | Предпросмотр собранной версии                    |
| `npm run astro ...`       | CLI команды Astro                               |

## 🏗 Структура проекта

```
/
├── public/
├── src/
│   ├── components/
│   │   ├── TodoApp.tsx      # Компонент Todo Manager
│   │   ├── NotesApp.tsx     # Компонент заметок
│   │   ├── Calculator.tsx   # Компонент калькулятора
│   │   └── ...
│   ├── layouts/
│   │   └── Layout.astro     # Основной layout
│   ├── pages/
│   │   ├── index.astro      # Главная страница
│   │   ├── todos.astro      # Страница Todo Manager
│   │   ├── notes.astro      # Страница заметок
│   │   ├── calculator.astro # Страница калькулятора
│   │   ├── apps.astro       # Обзор приложений
│   │   └── ...
│   └── styles/
│       └── globals.css      # Глобальные стили
└── package.json
```

## 🚀 Развертывание на Netlify

[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/netlify-templates/astro-platform-starter)

## 💻 Локальная разработка

### Требования
- [Node.js](https://nodejs.org/) v18.14+
- (опционально) [nvm](https://github.com/nvm-sh/nvm) для управления версиями Node.js

### Установка

1. Клонируйте репозиторий и установите зависимости:
```bash
git clone <your-repo>
cd <your-repo>
npm install
```

2. Запустите dev сервер:
```bash
npm run dev
```

3. Откройте [http://localhost:4321](http://localhost:4321) в браузере

### Для полной функциональности Netlify (опционально):

```bash
npm install netlify-cli@latest -g
netlify link
netlify dev
```

## 🎨 Кастомизация

### Добавление нового приложения:

1. Создайте компонент в `src/components/`
2. Создайте страницу в `src/pages/`
3. Добавьте ссылку в `src/components/Header.astro`
4. Обновите `src/pages/apps.astro`

### Стилизация:
- Глобальные стили: `src/styles/globals.css`
- Конфигурация Tailwind: `@import 'tailwindcss'` в globals.css
- Компонентные стили: inline в React компонентах

## 📝 Лицензия

MIT License - смотрите файл LICENSE для деталей.
