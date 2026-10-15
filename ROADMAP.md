# Mriya AI Core — Roadmap і прогрес

Це файл **стану**. Правила роботи лежать у `CLAUDE.md`.

**Як користуватись:**
- Claude читає цей файл на старті кожної сесії, звіряє з кодом на диску і продовжує з першого невідміченого кроку в розділі «Зараз».
- Крок відмічається `[x]` тільки після перевірки на диску або в запущеному стеку, а не зі слів.
- Після кожного кроку оновлюється рядок «Наступна дія» і дата.

**Останнє оновлення:** 2026-10-15 (перевірка перед переїздом)

**Наступна дія:** перенести роботу на ноутбук (розділ нижче), потім крок 1.6 (strict-вивід Groq).

---

## Перенесення на ноутбук (разове)

На цьому ПК:
- [x] Зафіксувати версію Qdrant у `docker-compose.yml`: `qdrant/qdrant:v1.19.1`
- [x] Зробити snapshot колекції `my_knowledge_e5` і завантажити файл: `data/snapshots/e5.snapshot`, 78 МБ, sha256 збігається з Qdrant (`38ec6507…`). Переносити руками, не через git
- [ ] Закомітити й запушити всі зміни (`qdrant.py`, `config.py`, `ingest_parsed.py`, `ingest_raw.py`, `score_probe.py`, `docker-compose.yml`, `CLAUDE.md`, `ROADMAP.md`)
- [ ] Скопіювати `.env` безпечним шляхом (флешка або менеджер паролів; не git, не чат)
- [ ] Скопіювати `data/parsed/` (14 МБ, 145 `.md` + `_manifest.json`) і файл snapshot. `data/parsed` — єдина копія платного парсингу

На ноутбуці:
- [ ] `git clone` / `git pull`, покласти `.env` і `data/parsed/` на місце
- [ ] `docker compose up -d --build`
- [ ] `uv sync`
- [ ] Відновити колекцію зі snapshot (Qdrant API: upload snapshot). Має бути 13 335 точок у `my_knowledge_e5`. Запасний варіант: переіндексувати з `data/parsed` (~20–25 хв)
- [ ] Зареєструвати юзера, створити учня (Postgres на ноутбуці порожній)
- [ ] Перевірити: `score_probe.py` → борщ 0 результатів, домашка 5

---

## Зараз: Slice #1. Retrieval + structured output

**Інструмент:** Qdrant, multilingual embeddings, поріг score, Groq strict JSON.
**Gate:** один Groq trace у Phoenix, де в chain input є релевантний чанк, і один опис «ні про що», який завершується `COMPLETED` з `grounded=False`.

- [x] **1.0** `Case.student_id` знову `NOT NULL` (міграція `925e46e3d2df`, 12 тестових кейсів без учня видалено)
- [x] **1.1** Ingest сам створює колекцію: `from_documents([], ...)` один раз до циклу
- [x] **1.2** `source_file` береться з `_manifest.json` (назва PDF), ID детерміновані через `uuid5`
- [x] **1.3** Модель `intfloat/multilingual-e5-small` з префіксами `passage: ` (ingest) і `query: ` (`qdrant.py`); повна переіндексація: 13 335 точок у `my_knowledge_e5`
- [x] **1.4** Замір score (`scripts/score_probe.py`): релевантні ≥ ~0.862, не на тему ≤ 0.836 (сирий cosine). Пастка: `similarity_search_with_relevance_scores` перераховує score як `(1 + s) / 2`
- [x] **1.5** Поріг `retrieval_score_threshold = 0.85` у `Settings`, `asimilarity_search(..., score_threshold=...)`. Перевірено у воркері: домашка → 5 чанків, борщ → 0
- [ ] **1.6** `groq.py`: `with_structured_output(..., method="json_schema", strict=True)`. `prompts.py`: правило «3–5 кроків, без нумерації, гіпотеза про учня». Готово, коли 5 runs поспіль `COMPLETED` без `tool_use_failed`
- [ ] **1.7** Gate: два traces у Phoenix, потім ревʼю. Після чистого ревʼю Claude закриває slice тут і в `CLAUDE.md`
- [ ] **1.8** Закомітити slice

Відомі обмеження (не блокують gate): у корпусі мало документів про булінг і мовну адаптацію; частина чанків — HTML-таблиці й списки прізвищ, і такі чанки можуть пройти поріг. Від них захищає правило в prompt «використовуй чанк, тільки якщо він стосується кейсу».

---

## Борг (не блокує gate, робиться пізніше)

- [ ] `groq.BadRequestError` (`tool_use_failed`) у `handle_llm_errors` → правильна причина замість `unknown_error`
- [ ] Завантаження моделі embeddings винести з event loop (arq `on_startup` або `asyncio.to_thread`)
- [ ] Retriever span у Phoenix з `run_id`; `run_id` у логах `retrieval_failed` і `analysis_success`
- [ ] Чанки в prompt з роздільниками й `source_file`; не рендерити `None` у prompt; злити два system prompt-и
- [ ] `datetime.now(UTC)`; заповнювати `started_at`, `execution_time_ms`, `tokens_used`
- [x] Ingest розділено на `ingest_parsed.py` (index з `data/parsed`) і `ingest_raw.py` (LlamaParse)
- [ ] `ingest_raw.py`: перевірка `.endswith(".md")` на `:34` відкидає всі PDF, тож скрипт нічого не робить. І він має зберігати `.md` + запис у `_manifest.json` у `data/parsed`, а не індексувати напряму (інакше платний парсинг знову живе тільки в Qdrant)
- [ ] `.env.example` з усіма змінними без секретів
- [ ] 174 PDF у `data/raw` ніколи не парсились (безкоштовно: `pymupdf4llm`)
- [ ] Phoenix `project_name="my-llm-app"` → назва проєкту

---

## Далі: Roadmap «проблема → інструмент»

Кожен slice існує, бо в репо вже видно проблему, яку він вирішує. Мінімальний scope, без production-фіч.

### Slice #2. Ownership учнів
- **Проблема:** будь-який вчитель бачить і використовує будь-якого учня (дані неповнолітніх).
- **Інструмент:** FastAPI + SQLAlchemy, власник у кожному запиті.
- **Scope:** `Student.teacher_id`, міграція, фільтр у всіх запитах, 404 для чужого учня.
- **Примітка:** можна поміняти місцями з #3, якщо потрібна мотивація. Рішення за Дмитром.

### Slice #3. LangGraph
- **Проблема:** вчителі ставлять питання, які не є кейсами; для уточнень потрібна памʼять.
- **Інструмент:** LangGraph: router (кейс чи питання), гілка питань із цитатами й чесним «не знайдено», checkpointer memory.
- **Scope:** спочатку одне питання, потім памʼять. Без UI.

### Slice #4. Neo4j
- **Проблема:** накази МОН змінюють і скасовують один одного; retrieval повертає нечинні документи.
- **Інструмент:** Neo4j graph RAG, ребра `AMENDS` / `CANCELS`.
- **Scope:** кілька десятків документів зі звʼязками, перевіреними вручну.

### Slice #5. LlamaIndex
- **Проблема:** chunking ігнорує структуру (HTML-таблиці, порожні чанки); ingest привʼязаний до LangChain.
- **Інструмент:** LlamaIndex ingest/indexing.
- **Scope:** порівняння пошуку на тих самих 7 запитах із `score_probe.py`.

### Slice #6. Pandas → PySpark
- **Проблема:** у кейсах немає фактів про оцінки й відвідуваність.
- **Scope:** синтетичні дані, агрегати в `academic_profile`.

### Slice #7. Unsloth
- **Проблема:** корпус змішує методички зі списками журі й переможців.
- **Scope:** розмітити кілька сотень чанків, fine-tune маленького класифікатора, фільтр у retrieval за типом.
