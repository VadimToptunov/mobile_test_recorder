# Self-Learning ML System

> Модель учится сама на данных от всех пользователей, без участия человека

---

## 🎯 Концепция

**Проблема:** Обычные ML модели требуют ручной разметки данных для каждого приложения.

**Решение:** Краудсорсинг данных от всех пользователей + автоматическая разметка.

### Как это работает?

```
┌────────────────────────────────────────────────────────┐
│  User 1 (Flutter app)     User 2 (React Native app)   │
│          ↓                           ↓                 │
│   Собирает элементы          Собирает элементы        │
│   автоматически              автоматически             │
└─────────────┬────────────────────────┬─────────────────┘
              │                        │
              ↓                        ↓
┌─────────────────────────────────────────────────────────┐
│         Central ML Server (api.mobile-observe.dev)      │
│                                                          │
│  • Агрегирует данные от всех юзеров                     │
│  • Переобучает модель каждую неделю                     │
│  • Публикует обновленные модели                         │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ↓
              ┌────────────────────────┐
              │  Model v1.1 (updated)  │
              │  • 10K новых примеров  │
              │  • 92% → 95% accuracy  │
              └────────────────────────┘
                           │
                           ↓
┌────────────────────────────────────────────────────────┐
│  All Users: auto-download updated model                │
│  • Работает лучше с каждой неделей                     │
│  • Без ручного вмешательства                           │
└────────────────────────────────────────────────────────┘
```

---

## 🚀 Для пользователей (User Experience)

### Первый запуск

```bash
# 1. Install framework
pip install mobile-observe-test

# 2. Run first test generation
observe project fullcycle --android-source ./app/src --output ./tests/

# В консоли:
# ✅ Using universal pre-trained ML model
# 📊 Model version: 1.2.0 (trained on 50K+ elements)
# 🌍 Supports: Android, iOS, Flutter, React Native
# 
# 💡 TIP: Your usage helps improve the model for everyone!
#    Data shared: element attributes only (no app names, no text content)
#    Opt-out: observe config set ml.contribute false
```

### Автоматические обновления

```bash
# Каждую неделю при запуске
observe project fullcycle ...

# В консоли:
# 🔄 Checking for model updates...
# ✅ New model available: v1.3.0
# 📥 Downloading... [████████████] 100%
# ✅ Model updated! Accuracy improved: 92% → 95%
# 
# Changelog:
#   • Added 5K new Flutter samples
#   • Improved checkbox detection
#   • Better React Native support
```

### Ручное управление

```bash
# Проверить обновления
observe ml check-updates

# Загрузить последнюю версию
observe ml update-model

# Посмотреть статистику своих вкладов
observe ml stats

# Output:
# 📊 Your Contributions
# ─────────────────────
# • Samples collected: 2,350
# • Platforms: Android (80%), iOS (20%)
# • Uploaded: 2,350 / 2,350
# • Thank you for helping improve the model! 🎉

# Отключить сбор данных
observe config set ml.contribute false

# Включить обратно
observe config set ml.contribute true
```

---

## 🔒 Приватность (Privacy-First Design)

### Что собирается?

```json
{
  "sample_id": "a3f9e82b",
  "class_name": "androidx.compose.material.Button",
  "clickable": true,
  "focusable": true,
  "has_text": true,
  "text_length": 6,
  "bounds_width": 120,
  "bounds_height": 48,
  "platform": "android",
  "element_type": "button",
  "confidence": 0.95,
  "timestamp": "2026-01-12T10:30:00Z"
}
```

### Что НЕ собирается?

❌ **App names** - не знаем, какое приложение
❌ **Package IDs** - не знаем, кто разработчик
❌ **Actual text** - только `has_text: true` и длина
❌ **Screenshots** - никогда не собираем изображения
❌ **User data** - никакой личной информации
❌ **API calls** - только UI элементы
❌ **IP addresses** - анонимная загрузка

### Сравнение с другими инструментами

| Фича | Mobile Observe | Firebase Crashlytics | Amplitude |
|------|----------------|----------------------|-----------|
| Собирает названия приложений | ❌ | ✅ | ✅ |
| Собирает текст с экранов | ❌ | ✅ (stacktraces) | ✅ |
| Собирает screenshots | ❌ | ✅ | ❌ |
| Собирает user IDs | ❌ | ✅ | ✅ |
| Можно отключить | ✅ | ✅ | ✅ |

**Вывод:** Мы собираем МЕНЬШЕ данных, чем стандартные аналитические инструменты.

---

## 🏗️ Архитектура

### Компоненты

**1. SelfLearningCollector** - собирает данные локально

```python
from framework.ml.self_learning import SelfLearningCollector

collector = SelfLearningCollector(
    opt_in=True,  # User consent
    upload_endpoint="https://api.mobile-observe.dev/v1/ml/samples"
)

# Automatically collects during normal usage
collector.collect_from_hierarchy(hierarchy, platform="android")

# Auto-uploads when batch reaches 1000 samples
```

**2. ModelUpdater** - обновляет модели

```python
from framework.ml.self_learning import ModelUpdater

updater = ModelUpdater()

# Check for updates (happens automatically once per day)
update = updater.check_for_updates()

if update:
    updater.download_update(update)
    # Model updated to v1.3.0!
```

**3. FeedbackCollector** - собирает исправления от пользователей

```python
from framework.ml.self_learning import FeedbackCollector

feedback = FeedbackCollector()

# When user corrects ML prediction
feedback.record_correction(
    element=element_dict,
    predicted_type="text",      # ML thought it's text
    actual_type="button",       # User corrected: it's a button
    platform="ios"
)

# This correction helps retrain the model!
```

---

## 📈 Жизненный цикл модели

### Week 1: Initial Release

```
Model v1.0.0
• Trained on: 2,500 synthetic samples
• Accuracy: 87%
• Platforms: Android, iOS
• Users: 0
```

### Week 2: First User Data

```
Model v1.1.0
• New data: +5,000 real samples from 50 users
• Accuracy: 89% (+2%)
• New patterns discovered:
  - Custom Material Design components
  - Jetpack Compose buttons
• Users: 50
```

### Week 4: Growing Dataset

```
Model v1.2.0
• New data: +15,000 samples from 200 users
• Accuracy: 92% (+3%)
• Added support:
  - Flutter widgets
  - React Native components
• Users: 200
```

### Week 12: Production Ready

```
Model v1.5.0
• Total data: 50,000+ real-world samples
• Accuracy: 95% (+3%)
• Platforms: Android, iOS, Flutter, React Native
• Users: 1,000+
• User corrections: 500+ integrated
```

### Year 1: Industry Standard

```
Model v2.0.0
• Total data: 500,000+ samples from 10K+ users
• Accuracy: 98% (+3%)
• Coverage: 99.9% of all mobile UI patterns
• Zero manual labeling required
```

---

## 🔧 Интеграция в существующий код

### В ModelBuilder

```python
# framework/model_builder/builder.py

from framework.ml.self_learning import SelfLearningCollector

class ModelBuilder:
    def __init__(self, ...):
        # Initialize self-learning
        self.ml_collector = SelfLearningCollector()
    
    def build_from_events(self, events: List[Event]) -> AppModel:
        # Build model as usual
        model = self._build_model(events)
        
        # Collect training data automatically
        if self.ml_collector.opt_in:
            for screen in model.screens:
                hierarchy = self._screen_to_hierarchy(screen)
                self.ml_collector.collect_from_hierarchy(
                    hierarchy,
                    platform=model.platform.value
                )
        
        return model
```

### В CLI commands

```python
# framework/cli/project_commands.py

from framework.ml.self_learning import ModelUpdater

@project.command()
def fullcycle(...):
    # Check for model updates before starting
    updater = ModelUpdater()
    if updater.auto_update():
        click.echo("✅ ML model updated to latest version!")
    
    # Continue with normal workflow
    ...
```

---

## 🧪 Тестирование системы

### Локальный режим (без сервера)

```bash
# 1. Генерируем тестовые данные
observe ml generate-test-samples --count 1000 --output test_samples.json

# 2. Собираем в локальный кэш (не загружаем)
observe config set ml.contribute false  # Disable uploads
observe config set ml.local_cache_only true

# 3. Используем framework как обычно
observe project fullcycle --android-source ./app/src --output ./tests/

# 4. Проверяем собранные данные
ls ml_cache/training_samples/
# batch_a3f9e82b.json  (1000 samples)

# 5. Анализируем собранные данные
observe ml analyze-cache
# Output:
# 📊 Local Training Cache
# • Batches: 5
# • Total samples: 5,000
# • Platform distribution:
#   - Android: 80% (4,000)
#   - iOS: 20% (1,000)
# • Element types:
#   - button: 1,200
#   - input: 800
#   - text: 1,500
#   ...
```

### Режим разработки (mock server)

```bash
# 1. Запускаем локальный mock server
cd ml_server_mock/
python mock_server.py
# Server running on http://localhost:8000

# 2. Настраиваем endpoint
observe config set ml.upload_endpoint http://localhost:8000/v1/ml/samples

# 3. Включаем uploads
observe config set ml.contribute true

# 4. Используем framework
observe project fullcycle ...

# 5. Проверяем, что данные загрузились
curl http://localhost:8000/v1/ml/samples/stats
# {
#   "total_batches": 3,
#   "total_samples": 3000,
#   "last_upload": "2026-01-12T11:45:00Z"
# }
```

---

## 🌍 Production Server (будущее)

### Требования к серверу

```yaml
# Infrastructure
- Endpoint: https://api.mobile-observe.dev
- Backup: https://ml.mobile-observe.dev
- CDN: CloudFlare (для скачивания моделей)
- Database: PostgreSQL (метаданные)
- Storage: S3 (training samples, models)

# API Endpoints
POST /v1/ml/samples          # Upload training batch
GET  /v1/ml/models/latest    # Get latest model metadata
GET  /v1/ml/models/{version} # Download specific model version
POST /v1/ml/feedback         # Upload user corrections

# Authentication
- API key (для загрузки данных)
- Public download (модели доступны всем)

# Privacy
- No logging of IP addresses
- No user tracking
- GDPR compliant
- Можно запросить удаление своих данных
```

### Training Pipeline

```python
# ml_server/training_pipeline.py

def weekly_retrain():
    """Runs every Sunday at 2 AM UTC"""
    
    # 1. Collect new samples from last week
    new_samples = db.query_samples(since=last_week)
    print(f"New samples: {len(new_samples)}")
    
    # 2. Merge with existing dataset
    full_dataset = merge_datasets(existing_dataset, new_samples)
    
    # 3. Clean and validate
    clean_dataset = validate_and_clean(full_dataset)
    
    # 4. Train new model
    model = train_universal_model(clean_dataset)
    
    # 5. Evaluate
    metrics = evaluate_model(model, test_set)
    print(f"Accuracy: {metrics['accuracy']:.1%}")
    
    # 6. If better than current, publish
    if metrics['accuracy'] > current_model_accuracy:
        publish_model(model, version="1.3.0")
        notify_users("New model available!")
    
    # 7. Generate changelog
    generate_changelog(old_model, new_model)
```

---

## 💡 Альтернативы (если нет сервера)

### Вариант 1: P2P (peer-to-peer)

Пользователи обмениваются training samples напрямую через торрент-подобную систему.

**Плюсы:**
- Не нужен центральный сервер
- Децентрализованно

**Минусы:**
- Сложнее реализовать
- Нет контроля качества

### Вариант 2: GitHub Releases

Модели и datasets публикуются как GitHub Releases.

```bash
# Download latest model
curl -L https://github.com/yourusername/mobile-observe/releases/latest/download/universal_model.pkl \
  -o ml_models/universal_element_classifier.pkl
```

**Плюсы:**
- Бесплатно
- Простая интеграция
- Version control

**Минусы:**
- Нет автоматической aggregation данных
- Нужно вручную переобучать модель

### Вариант 3: Federated Learning

Модель обучается локально у каждого пользователя, только веса обновляются.

**Плюсы:**
- Максимальная приватность
- Не нужно передавать данные

**Минусы:**
- Очень сложная реализация
- Требует много ресурсов на клиенте

---

## 🚀 Roadmap

### Phase 1: Foundation (Done ✅)
- [x] Universal pre-trained model
- [x] Synthetic dataset generation
- [x] Basic ML classification

### Phase 2: Self-Learning (Current)
- [ ] SelfLearningCollector implementation
- [ ] ModelUpdater implementation  
- [ ] FeedbackCollector implementation
- [ ] Local caching and batching
- [ ] Privacy-first data anonymization

### Phase 3: Infrastructure (Future)
- [ ] Production API server
- [ ] Automated training pipeline
- [ ] Model versioning and rollback
- [ ] A/B testing for model updates
- [ ] User dashboard (contributions stats)

### Phase 4: Advanced Features (Future)
- [ ] Multi-language model (Rust core?)
- [ ] Real-time model updates
- [ ] Federated learning support
- [ ] Custom model fine-tuning UI
- [ ] Model marketplace (community models)

---

## 📚 References

- **Privacy by Design**: https://www.privacybydesign.foundation/
- **Federated Learning**: https://federated.withgoogle.com/
- **GDPR Compliance**: https://gdpr.eu/
- **ML Model Versioning**: https://dvc.org/

---

## 💬 FAQ

**Q: Могу ли я отключить сбор данных?**  
A: Да, в любой момент: `observe config set ml.contribute false`

**Q: Можно ли посмотреть, какие данные собираются?**  
A: Да, они хранятся локально в `ml_cache/training_samples/`. Можешь изучить любой файл.

**Q: А если я хочу использовать только свою модель?**  
A: Можешь обучить свою: `observe ml train --data my_data.json --output my_model.pkl`

**Q: Поддерживается ли офлайн режим?**  
A: Да, модель работает локально. Интернет нужен только для обновлений.

**Q: Сколько занимает модель?**  
A: ~5-10 MB (одна модель для всех платформ)

**Q: Как часто обновляется модель?**  
A: Планируется еженедельно, но можно реже/чаще в зависимости от объема данных.

**Q: Что если сервер недоступен?**  
A: Framework продолжит работать с локальной моделью. Данные сохранятся локально и загрузятся позже.

**Q: Можно ли контрибьютить только для конкретной платформы (например, только iOS)?**  
A: Да, можно настроить: `observe config set ml.contribute_platforms ios`

**Q: А если я нашел баг в модели?**  
A: Можешь исправить прогноз командой `observe ml correct` или создать issue на GitHub.
