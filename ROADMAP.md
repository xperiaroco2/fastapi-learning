# Mriya AI Core — Roadmap і прогрес

Це файл **стану**. Правила роботи лежать у `CLAUDE.md`.

**Як користуватись:**
- Claude читає цей файл на старті кожної сесії, звіряє з кодом на диску і продовжує з першого невідміченого кроку в розділі «Зараз».
- Крок відмічається `[x]` тільки після перевірки на диску або в запущеному стеку, а не зі слів.
- Після кожного кроку оновлюється рядок «Наступна дія» і дата.

**Останнє оновлення:** 2026-10-15 (Slice #1 закрито, відкрито Slice #3)

**Наступна дія:** на ПК: `git pull`, перевірити коміт Slice #1 (1.8) і що стек ПК живий; потім крок 3.0. На ноутбуці лишилось: `score_probe.py`, скопіювати `data/parsed/`.

---

## Перенесення на ноутбук (разове)

На цьому ПК:
- [x] Зафіксувати версію Qdrant у `docker-compose.yml`: `qdrant/qdrant:v1.19.1`
- [x] Зробити snapshot колекції `my_knowledge_e5` і завантажити файл: `data/snapshots/e5.snapshot`, 78 МБ, sha256 збігається з Qdrant (`38ec6507…`). Переносити руками, не через git
- [x] Закомітити й запушити всі зміни (`qdrant.py`, `config.py`, `ingest_parsed.py`, `ingest_raw.py`, `score_probe.py`, `docker-compose.yml`, `CLAUDE.md`, `ROADMAP.md`)
- [x] Скопіювати `.env` безпечним шляхом (флешка або менеджер паролів; не git, не чат)
- [ ] Скопіювати `data/parsed/` (14 МБ, 145 `.md` + `_manifest.json`) і файл snapshot. `data/parsed` — єдина копія платного парсингу

На ноутбуці:
- [ ] `git clone` / `git pull`, покласти `.env` і `data/parsed/` на місце (код і `.env` є, `data/parsed/` ще немає)
- [x] `docker compose up -d --build`: усі сервіси running, `/health` ok, Alembic `925e46e3d2df`
- [x] `uv sync` (dry-run без змін)
- [x] Відновити колекцію зі snapshot (Qdrant API: upload snapshot). Має бути 13 335 точок у `my_knowledge_e5`. Запасний варіант: переіндексувати з `data/parsed` (~20–25 хв). Перевірено: count 13 335, 384 dims, Cosine
- [x] Зареєструвати юзера, створити учня (Postgres на ноутбуці порожній)
- [ ] Перевірити: `score_probe.py` → борщ 0 результатів, домашка 5

---

## Зараз: Slice #3. LangGraph: питання вчителя

**Проблема:** вчитель питає не про учня, а про правила («скільки годин підвищення кваліфікації на рік?»). `Case` вимагає учня, а prompt аналізу кейсу на таке відповідає «уточніть, хто учень» (run `65c611f7`). Для уточнювальних питань потрібна памʼять.
**Інструмент:** LangGraph: `StateGraph`, умовні ребра, checkpointer.
**Gate:**
1. Питання, відповідь на яке є в корпусі: відповідь цитує `source_file`, у Phoenix видно вузли графа.
2. Питання, якого немає в корпусі: чесне «не знайдено», без вигаданої відповіді.
3. Уточнення в тому самому thread спирається на попередню відповідь (checkpointer).

- [ ] **3.0** Baseline для 3b: `json_validate_failed` / `tool_use_failed` → `invalid_output` у `handle_llm_errors` (зараз `unknown_error`). Без цього не буде цифри «до» для циклу самовиправлення
- [ ] **3.1** Дизайн на папері, без коду: state графа (поля), вузли, ребра, де зберігається питання й відповідь (Postgres), як воркер запускає граф. Відкрите рішення: окремий `POST /questions` чи один вхід із router «кейс / питання». Claude ревʼюїть до коду
- [ ] **3.2** Retrieval із джерелами: `AIRetrieval.search` повертає текст чанка разом із `source_file` (одна форма результату, mock теж). Закриває борг «чанки з роздільниками й `source_file`»
- [ ] **3.3** Мінімальний граф без HTTP: `retrieve` → (0 чанків → `not_found`) / (є чанки → `answer` з цитатами). Запуск скриптом на 2 питаннях із `score_probe.py`: одне з корпусу, одне ні
- [ ] **3.4** Збереження і HTTP: модель + міграція, route ставить job у чергу, воркер запускає граф, `GET` повертає статус і відповідь. Власник — `teacher_id` з `get_current_user`, чуже → 404
- [ ] **3.5** Памʼять: checkpointer, `thread_id`, уточнювальне питання
- [ ] **3.6** Gate: три traces у Phoenix, потім ревʼю
- [ ] **3.7** Закомітити slice

---

## Готово

### Slice #1. Retrieval + structured output — gate пройдено 2026-10-15

**Інструмент:** Qdrant, multilingual embeddings, поріг score, Groq strict JSON.
**Gate:** один Groq trace у Phoenix, де в chain input є релевантний чанк, і один опис «ні про що», який завершується `COMPLETED` з `grounded=False`.

- [x] **1.0** `Case.student_id` знову `NOT NULL` (міграція `925e46e3d2df`, 12 тестових кейсів без учня видалено)
- [x] **1.1** Ingest сам створює колекцію: `from_documents([], ...)` один раз до циклу
- [x] **1.2** `source_file` береться з `_manifest.json` (назва PDF), ID детерміновані через `uuid5`
- [x] **1.3** Модель `intfloat/multilingual-e5-small` з префіксами `passage: ` (ingest) і `query: ` (`qdrant.py`); повна переіндексація: 13 335 точок у `my_knowledge_e5`
- [x] **1.4** Замір score (`scripts/score_probe.py`): релевантні ≥ ~0.862, не на тему ≤ 0.836 (сирий cosine). Пастка: `similarity_search_with_relevance_scores` перераховує score як `(1 + s) / 2`
- [x] **1.5** Поріг `retrieval_score_threshold = 0.85` у `Settings`, `asimilarity_search(..., score_threshold=...)`. Перевірено у воркері: домашка → 5 чанків, борщ → 0
- [x] **1.6** `groq.py`: `with_structured_output(..., method="json_schema", strict=True)`. `prompts.py`: правило «3–5 кроків, без нумерації, гіпотеза про учня». Готово, коли 5 runs поспіль `COMPLETED` без `tool_use_failed`. Перевірено: 7 з 8 runs `COMPLETED`, останні 5 поспіль; у кожному Phoenix span `strict: true`; нумерації в кроках немає. 1 run `FAILED` (`json_validate_failed`, `maxItems: got 6`), див. «Борг»
- [x] **1.7** Gate: два traces у Phoenix, потім ревʼю. Після чистого ревʼю Claude закриває slice тут і в `CLAUDE.md`
  - Trace 1 є: run `6333293f`, 7 чанків про увагу й математику в `related_info`. Відповідь була англійською; після правила «Відповідай виключно українською» run `d0a1cf0a` українською
  - Trace 2: Run `93a77be1` (борщ, учень із профілем): `FAILED`, `json_validate_failed` (`missing properties: grounded`). У `failed_generation` модель привʼязала борщ до дробів із профілю: план «рахувати дроби в рецепті борщу». Після правила «`grounded=True` лише коли факт пояснює проблему учня» run `7f90bfcb`: `COMPLETED`, `grounded=f`, 0 чанків, гіпотеза «у описі немає проблеми учня». Але `action_plan` — рецепт борщу (знахідка ревʼю). Після правила про кроки-уточнення run `65c611f7`: `COMPLETED`, `grounded=f`, 3 кроки «уточнити, хто учень / яка проблема / як давно». Ревʼю чисте: `ruff` ok, `pyright` 0 errors, решта знахідок у «Борг»
- [ ] **1.8** Закомітити slice (Дмитро пушить 2026-10-15; перевірити `git log` на старті наступної сесії)

Відомі обмеження (не блокують gate): у корпусі мало документів про булінг і мовну адаптацію; частина чанків — HTML-таблиці й списки прізвищ, і такі чанки можуть пройти поріг. Від них захищає правило в prompt «використовуй чанк, тільки якщо він стосується кейсу».

---

## Борг (не блокує gate, робиться пізніше)

- [ ] `groq.BadRequestError` (`tool_use_failed`, `json_validate_failed`) у `handle_llm_errors` → правильна причина замість `unknown_error`. Strict-режим Groq не обмежує `maxItems` під час генерації, а перевіряє вже готовий JSON: 1 з 8 runs повернув 6 кроків (шостий `""`) → 400 → `unknown_error`. Потім ще 1: відсутній `grounded` (`required`). Разом 2 з 11. Рішення: зараз мапінг в `invalid_output` (щоб рахувати частоту), retry — циклом у Slice #3b. Мапінг став кроком 3.0
- [ ] Завантаження моделі embeddings винести з event loop (arq `on_startup` або `asyncio.to_thread`)
- [ ] Retriever span у Phoenix з `run_id`; `run_id` у логах `retrieval_failed` і `analysis_success`
- [ ] Чанки в prompt з роздільниками й `source_file`
- [x] Один system prompt; `None` не рендериться (сервіс передає `academic_profile or ""`, `analyse.py:43`)
- [ ] `datetime.now(UTC)`; заповнювати `started_at`, `execution_time_ms`, `tokens_used`
- [x] Ingest розділено на `ingest_parsed.py` (index з `data/parsed`) і `ingest_raw.py` (LlamaParse)
- [ ] `ingest_raw.py`: перевірка `.endswith(".md")` на `:34` відкидає всі PDF, тож скрипт нічого не робить. І він має зберігати `.md` + запис у `_manifest.json` у `data/parsed`, а не індексувати напряму (інакше платний парсинг знову живе тільки в Qdrant)
- [ ] Опис без проблеми учня (борщ) проходить як кейс; prompt лише чесно каже про це в `hypothesis`. Рішення: Slice #3b
- [ ] `temperature=0.3` захардкоджено в `groq.py`; перенести в settings
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
- **Примітка:** 2026-10-15 Дмитро обрав #3 раніше за #2. Свідома черговість: дані неповнолітніх поки без ownership.

### Slice #3b. LangGraph: цикл самовиправлення для `analyse_case`
- **Проблема:** strict-режим Groq не гарантує схему: 2 з 12 runs → `json_validate_failed` (`maxItems`, відсутній `grounded`); опис не про учня (борщ) проходить як кейс.
- **Інструмент:** LangGraph: вузол `validate` повертає моделі текст помилки, ліміт спроб; вузол перевірки «чи є тут проблема учня».
- **Gate:** частка `invalid_output` до (baseline з 3.0) і після на однаковій кількості runs. Простий retry — це `with_retry`, LangGraph для нього не потрібен.

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
