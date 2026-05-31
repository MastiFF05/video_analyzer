# Video Content Analysis

Проект для анализа видео на наличие потенциально нежелательного или деструктивного контента.

## Возможности
- загрузка и обработка видео;
- извлечение кадров;
- предобработка изображений для OCR;
- распознавание текста на кадрах;
- анализ ключевых кадров через мультимодальную модель;
- сохранение результатов в JSON.

## Требования
- Python 3.9+
- API-ключ OpenRouter

## Установка
```bash
git clone <repo_url>
cd <repo_name>
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Настройка
Создайте файл `.env` в корне проекта:

```env
YOUR_OPENROUTER_API_KEY=your_key_here
```

## Запуск
Запустите нужный скрипт проекта, например:

```bash
python src/modules/pz7.py
```
