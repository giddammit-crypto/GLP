# NEXT.MD — передача разработки следующему ИИ-агенту

**Проект:** GLP «Гуляйполе: Вольна Територія — Анархія есть мать порядка» — мод
для Hearts of Iron IV **1.19.2** (обязательно DLC *La Résistance* — идеология
`anarchism`). Страна-минор: **GLP** (Вольная Территория, 12 стейтов, 1936).

---

## 0. Контекст и правила работы (читать первым)

- **Состояние:** аудит `python3 tools/glp_audit.py` → **0 ошибок, 1 предупреждение**
  (музыка-плейсхолдер — отдельный отложенный пакет, решение пользователя).
  `git diff --check` — чисто.
- **Ключевые документы:**
  - `GAMEPLAY_READINESS.md` — роадмап фаз A–H, капы баланса, приоритеты (A/B/C/D/E **закрыты** — итерации 13–17; **F/G/H — впереди**).
  - `AUDIT_REPORT.md` — история итераций (11–19): что найдено/сделано/принято.
  - `README.md` — описание мода и ключевые решения.
- **Конвенции:**
  - ВХОД в шаг: аудит зелёный. ВЫХОД из шага: аудит зелёный + негативные тесты
    новых инвариантов (поломку вводят → аудит ловит → откатывают).
  - Каждая итерация → новый раздел `AUDIT_REPORT.md` (найдено / сделано / приёмка /
    «остаточные ограничения (честно)») + буллит в `README.md` + пометка в
    `GAMEPLAY_READINESS.md` при закрытии фазы.
  - Кодировки: `.txt`/`.gfx`/`.gui` — **UTF-8 без BOM**; `.yml` локализации —
    **UTF-8 с BOM**, заголовок `l_russian:` / `l_english:`.
  - **Без плейсхолдеров.** TSV-таблицы в `tools/` — единый источник правды
    (иконки, search_filters, картинки).
  - Запреты (регрессии, уже были):
    - НЕ создавать `set_oob`-файлы/эффекты в середине игры — эффект заменяет **всю** армию.
    - НЕ добавлять второй топ-уровневый блок `spriteTypes` в `.gfx` (ломает парсинг — пропадают ВСЕ спрайты файла).
    - НЕ использовать `effectFile`/`animation = {}` внутри `spriteType` (неподдерживаемые поля 1.19; `effectFile` валиден только в `progressbartype`).
    - Локализационные ключи опций событий не должны конфликтовать с `<id>.d` (desc): опции `.a .b .c`, четвёртая — буква, НЕ `.d` (в коде мода используется `.w`).
  - Аудит на момент передачи: **21 проверка** (14 исходных + 15 слоты духов + 16
    дипломатика + 17 пейсинг + 18 решения-анти-фарм + 19 equipment-ключи 1.19 +
    20 безопасность парсера .gfx + 21 модуль Испании).

---

## 1. СПРИНТ 6 (Фаза F, P2) — События и персонажи

Каркас уже есть (см. `events/GLP_diplomacy.txt`, namespace `glp_crisis`):
`glp_crisis.10` (Григорьев, запускается `on_startup` +220 дн.), `glp_crisis.20`
(Задов vs Волин — **ничем НЕ запускается**), `glp_crisis.30` (туберкулёз Махно,
+900 дн.), `glp_crisis.40` (бунт Семёнова, 120 дн. после фокуса
`GLP_old_enemies_unite`). Задачи:

1. **Кризис Григорьева (1936–37):** довести `glp_crisis.10` до развилки:
   - лояльность → флаг + стаб/ВС;
   - мятеж → утрата части стейтов (transfer_state в SOV или новый ванильный тег) ИЛИ «примирение» ценой стаб;
   - казнь → `retire_character = GLP_ataman_grigoriev` (**обязательно** с
     `has_character = GLP_ataman_grigoriev` — персонаж мог быть убит ранее).
   Запуск: текущий `on_startup` +220 дн. — сохранить; добавить `available`-условие
   (война/угроза) по желанию.
2. **Задов vs Волин:** `glp_crisis.20` повесить на развилку судов/террора —
   запускать событием-сигналом после фокусов `GLP_libertarian_civil_courts` /
   `GLP_decree_on_black_terror` (и после `GLP_zadov_intelligence_network`);
   варианты с казнью/ссылкой одного из персонажей (guard'ы `has_character`).
   Флаги `GLP_zadov_ascendant`/`GLP_volin_ascendant` уже ставятся.
3. **Туберкулёз Батька (late crisis):** `glp_crisis.30` — от смерти до
   наследования. Валидный минимальный сценарий: Махно умирает →
   `retire_character = GLP_nestor_makhno` (country_leader!) → событие-выбор
   нового лидера (кандидаты: Потёмкин/Григорьев — им нужно добавить блок
   `country_leader = { ideology = anarchism ... }` + портреты уже есть)
   ИЛИ «Совет Атаманов» (страна без одного лидера — crisis-ивент со стаб).
   ВНИМАНИЕ: смена country_leader — самый тяжёлый механически путь; проверить
   в игре (Sprint 8).
4. **Цепочка недоверия белых:** флаг `GLP_allied_white_emigres` (ставится
   фокусом `GLP_old_enemies_unite`) → ступени: `glp_crisis.40` (бунт Семёнова,
   уже есть) расширить до 2–3 событий-ступеней с флагами ступеней.
- **Новые инварианты аудита (добавить):** каждый `glp_crisis.*` запущен
  (id встречается в on_actions/фокусах/событиях), каждая казнь guard'ится
  `has_character`, флаги событий чистятся/идемпотентны.
- **Принятие:** каждая развилка меняет состав персонажей/флаги; RU/EN-локал.
  всех новых текстов; аудит зелёный + негативные тесты.

---

## 2. СПРИНТ 7 (Фаза G, P2) — AI

1. **`ai_strategy_plans`** для 4 дипломатических путей — файл
   `common/ai_strategy_plans/GLP_ai_strategy_plans.txt` существует (35 строк),
   расширить: планы под пути SOV/GER/ENG/«Вольному воля» (цели:
   antagonize/defend/focus на соседей).
2. **`ai_will_do` фокусов:** сейчас плоские `factor = 1..10`. Добавить
   модификаторы: `has_war`, `threat`, запасы снаряжения, `stability < 0.4`.
   Приоритет — ветки, которые ИИ реально пройдёт (военная + дипломатическая
   развилка).
3. **Реактивные соседи** через `on_actions` (НЕ переписывать ванильные деревья):
   частично уже сделано (`add_ai_strategy` в `glp_diplo.21–26`,
   `glp_soviet_anarchy_resentment` после майских дней). Добавить реакции
   POL/ROM/TUR на пакты и на агрессию GLP.
- **Принятие:** ИИ-Гуляйполе (обычная сложность) за 1936–38 выбирает один из
  4 путей, использует рейды/трофеи; `ai_strategy_plans` ссылаются только на
  существующие типы/цели (добавить проверку в аудит).

---

## 3. СПРИНТ 8 (Фаза H) — Верификация и релиз

1. **В-игровой чек-лист** (единственный шаг, где нужен человек/игра):
   - **Заставка:** 1:1 со скриншотом (координаты — раздел 4), озвучка ~2:45
     звучит, кнопка «Вольному воля!» (ENTER) стартует кампанию.
   - **Фон меню:** конная колонна махновцев (не ванильный фон).
   - **1936:** доступно ≥ 2 веток из 28; ультиматум Москвы ~июнь 1936
     (варианты: дань/отказ → wargoal SOV на 227/226/221); ивент Испании
     ~20.07.1936 (3 выбора; после выбора «Братья зовут» — бригада в армии).
   - **1937.6:** «Майские дни» (с КРО — CNT у власти; без — подавление и
     скрытие «Испанского маршрута»).
   - **1938.2:** решение «Черноморско-Іберійскій пактъ» → фракция
     «Чёрный Интернационал», духи у GLP и SPR.
   - **1941 (Барбаросса):** стек духов в пределах капов (conscription ≤ 0.35
     без хунты, cav-атака ≤ 0.40, фабрики ≤ 0.50 — см. раздел 0/капы).
   - **Трофеи:** победа в бою → снаряжение в запасах; при 4000+ л/с и
     технологиях — дивизия «Трофейный отряд РПА».
   - **Испания:** смена `set_politics` SPR **в ходе** гражданской войны не
     ломает войну (ожидаемо: смена правительства, война продолжается).
   - **Потёмкин:** генерал в списке с 1936, портреты (крупный/малый) отрисованы,
     черты «Мастер пехотных боёв»/«Фидель Атамана» в описании.
2. **Релиз:** обновить `mod_page/` (лендинг), `tools/build_thumbnail.sh`
   (карточка 512×512 < 1 МБ), `descriptor.mod` → **1.4.0**, git-тег.
3. **Музыка:** 11 одинаковых `.ogg`-заглушек в `music/` — отдельный пакет,
   пользователь отложил решение (варианты: свои OGG / процедурная / убрать
   раздел). Не трогать без запроса.

---

## 4. Заставка (интро Махно): ЧТО СДЕЛАНО И КАК ДИАГНОСТИРОВАТЬ

### 4.1. Что сделано (2026-08-26, итерация 18, см. AUDIT_REPORT.md)

**Корневая причина обоих симптомов** («фон и фото пропали», «фон меню
изменился») — **парсер Clausewitz не загружал `.gfx`-файл мода**: все
спрайты файла пропадали, а тексты (`instantTextBoxType`) и ванильные кнопки
(`GFX_button_*`) оставались. Два независимых дефекта из последнего коммита
перед итерацией 18:
1. `interface/gulyaipole_intro.gfx` — spriteType с **неподдерживаемыми
   полями** `effectFile` + подблок `animation = { ... }` (в `spriteType` 1.19
   их нет; до коммита анимированная лента титров была **убрана по ТЗ** —
   см. старый комментарий в .gfx).
2. `interface/frontendmainviewbg.gfx` — **два топ-уровневых блока
   `spriteTypes = { }`** (второй добавляли для перекрывания логотипа Paradox).

**Фикс:**
- `gulyaipole_intro.gfx`: единый блок `spriteTypes`; анимированный спрайт
  удалён (текст — `instantTextBoxType` с `standardtext_slider`, как на
  эталонном скриншоте); все статические спрайты на месте.
- **Раскладка 1:1 по эталонному скриншоту** (окно **1024×768**,
  `interface/gulyaipole_intro_custom.gui`, один `containerWindowType`):
  - фон: `background = { quadTextureSprite = "GFX_intro_bg" }` (1024×768 DXT1);
  - золотая кайма: iconType (0,0) 1024×768 `GFX_gold_inner_border` (DXT5);
  - портрет Махно: (30,30) 156×210 `GFX_portrait_nestor_makhno_intro` +
    рамка (25,25) 166×220 `GFX_political_leader_frame_gold`; подпись
    (25,248) `GULYAIPOLE_MAKHNO_CAPTION` = «Нестор Махно, 1921»;
  - текст: (240,30) 310×620, шрифт `hoi_16mbs`, `GULYAIPOLE_EPIC_INTRO_TEXT`,
    `scrollbarType = standardtext_slider`;
  - конница: (580,230) 320×150 `GFX_intro_makhno_cavalry` + подпись (580,386);
  - карта: (580,400) 320×260 `GFX_intro_ukraine_map` + подпись (580,664)
    «Екатеринославская губерния, 1919»;
  - кнопка: (402,700) 220×34 `GFX_button_221x34`, `GULYAIPOLE_START_BUTTON`
    = «Вольному воля!», shortcut ENTER.
  - Заголовок/субзаголовок и toggle-кнопка «режима чтения» УДАЛЕНЫ
    (на эталонном скриншоте их нет).
- Текстуры пересобраны под 1024×768: `gfx/interface/intro/gulyaipole_intro_bg.dds`
  (DXT1), `gulyaipole_gold_inner_border.dds` (DXT5); мастера —
  `tools/_gfx_src/intro_bg_1024.png` / `gold_inner_border_1024.png`
  (реbuild: `convert <мастер> -compress DXT1|DXT5 DDS:...`, см. итерацию 18).
- **Озвучка не тронута** (цепочка, покрыта аудитом
  `check_cinematic_intro_voice`): `on_startup` (GLP) → скрытое событие
  `glp_cinematic_intro.1` (`events/GulyaipoleCinematicIntro.txt`) →
  `sound_effect = gulyaipole_intro_voice` → `sound/voice.ogg` (~2:45, OGG
  Vorbis 44.1 кГц) + `scoped_play_song`; ванильная музыка гасится
  `music_station`-модификатором `factor = 0` при флаге
  `glp_show_cinematic_intro`. Окно показывает scripted GUI
  `common/scripted_guis/gulyaipole_intro_gui.txt` по флагу; старт кампании —
  `start_campaign_button_click` (clr флагов + `scoped_play_song = GLP_ms_yablochko`).
- **Фон главного меню:** файл `gfx/interface/frontendmainviewbg.dds`
  (1920×1440 DXT1) — вариант 1 «Степь, конная колонна махновцев»
  (выбор: `tools/select_menu_background.sh 1|2|3|4`, опции в
  `gfx/interface/menu_options/`). Привязан к **двум** именам спрайта
  (`GFX_frontend_bg` **и** `GFX_frontendmainviewbg`) в едином блоке
  `spriteTypes` файла `interface/frontendmainviewbg.gfx` — фон отрисовывается,
  как бы ванильный frontend не обращался. `effectFile` из блока убран
  (неподдерживаемое поле).

### 4.2. Диагностика, если после теста появятся ошибки

| Симптом в игре | Причина | Что чинить |
|---|---|---|
| Тексты/кнопки видны, **фон и фото пропали** | не загрузился `.gfx` (парсер) | `python3 tools/glp_audit.py` → `check_gfx_parse_safety`; ровно ОДИН `spriteTypes`-блок; нет `effectFile`/`animation = {}` внутри `spriteType`; имена спрайтов в GUI = имена в `.gfx` |
| **Нет озвучки** | разрыв звуковой цепи | аудит `check_cinematic_intro_voice`; вручную: `sound/gulyaipole_sounds.asset` (имена `gulyaipole_intro_voice_file`/`gulyaipole_intro_voice`), `sound/voice.ogg` стартует с `OggS`, событие содержит `sound_effect`, `on_actions` вызывает `glp_cinematic_intro.1` |
| **Ванильный фон меню** | не прочитан `frontendmainviewbg.gfx` ИЛИ битый DDS | тот же `check_gfx_parse_safety` + `check_screens` (1920×1440, DXT1/DXT5); два имени спрайта (`GFX_frontend_bg` + `GFX_frontendmainviewbg`) должны быть в одном `spriteTypes`-блоке |
| Текст «???» | символы вне атласа шрифта `hoi_16mbs` | в `GULYAIPOLE_EPIC_INTRO_TEXT` (локализация `gulyaipole_intro_text_l_*.yml`) оставить только атласные символы; коды цвета `§W`/`§!` — разрешены |
| Окно не по центру / тянется | несовпадение размеров | окно GUI = 1024×768 = размеры текстур фона/каймы; координаты элементов — раздел 4.1 |
| Кайма/фон «плавают» | `alwaystransparent = yes` на кайме; `clipping = yes` в окне | не снимать без необходимости |

Быстрая пересборка текстур заставки из мастеров (ImageMagick):
```
convert tools/_gfx_src/intro_bg_1024.png          -compress DXT1 DDS:gfx/interface/intro/gulyaipole_intro_bg.dds
convert tools/_gfx_src/gold_inner_border_1024.png -compress DXT5 DDS:gfx/interface/intro/gulyaipole_gold_inner_border.dds
```

---

## 5. ИСПАНИЯ — продолжение разработки

### 5.1. Готово (итерация 19, модуль «Иберийский пожар и Чёрный Интернационал»)

Файлы (новые): `events/GLP_spain_crisis.txt`, `events/GLP_barcelona_may_days.txt`,
`events/GLP_black_international.txt`, `common/decisions/GLP_spain_decisions.txt`,
`common/decisions/categories/GLP_spain_categories.txt`,
`common/ideas/GLP_black_international_ideas.txt`,
`common/unit_leader/GLP_spanish_traits.txt`,
`common/opinion_modifiers/GLP_spain_opinions.txt`,
`localisation/russian|english/GLP_spain_crisis_l_*.yml` (+4 строки в
`tools/idea_pictures.tsv`, хуки `on_civil_war_start`/`on_day` в
`common/on_actions/GLP_on_actions.txt`, шаблон бригады в `history/units/GLP_1936.txt`).

Механика: `glp_spain.1` (3 курса; запуск по флагу `glp_spain_war_active` из
on_actions) → «Испанский маршрут» (3 контрабандных маршрута 65/85/95%,
кулдауны 90 дн.) + КРО Задова (флаг `glp_kro_barcelona`) → `glp_barcelona.1`
(май 1937; с КРО — CNT у власти → `glp_black_international_path`; без —
подавление → `glp_spanish_programs_shut` скрывает маршруты) → пакт
(фракция «Чёрный Интернационал», духи `GLP_idea_catalan_wolfram_syndicate_workshops`
/ `GLP_idea_ukrainian_coal_and_grain`). Черта `GLP_spanish_tempering` выдаётся
решением `GLP_spain_brigade_homecoming` (Белаш, Каретник). Аудит —
`check_spain_module` (проверка 21).

### 5.2. Осталось

1. **В-игровая верификация** (Sprint 8, чек-лист в разделе 3) — главное:
   `set_politics`/`set_popularities` у SPR **в ходе** гражданской войны
   (ожидаемо: смена режима, война продолжается; если ломает — перевести на
   `set_popularities` только + opinion-механики).
2. **Отложено по дизайну** (не баг): отдельный анархистский тег CNT-FAI с
   автономиями Каталонии/Арагона (полная страна — отдельная крупная задача);
   реальные ресурсы пакта (вольфрам/уголь) — нацдухи в 1.19 ресурсы не
   выдают, зачтено производственными бонусами (задокументировано в локации).
3. **Возможные расширения** (по запросу пользователя): новости о потере
   конвоев, вторая группа КРО, исторические даты-якоря (1936.7.17 — старт
   войны уже зашит в `on_day 1936.7.20` со страховкой).

---

## 6. Новое в последнем срезе (для ориентира)

**Атаман Олег Потёмкин** (`GLP_oleg_potemkin`) — новый корпусный командир,
рекрутится с 1936:
- `common/characters/GLP_characters.txt` — portraits (large/small) +
  `corps_commander`: `traits = { infantry_expert aggressive_assaulter
  GLP_potemkin_infantry_master GLP_potemkin_black_fidele }`, skills 3/4/3/3/2.
- `common/unit_leader/GLP_potemkin_traits.txt` — 2 уникальные черты
  (gui_row 4): «Мастер пехотных боёв» (инф. атака/оборона +10%, breakthrough
  +5%, мораль +5%) и «Фидель Атамана» (мораль +5%, опыт +5%, org-loss
  −5%) — «главный приверженец Батьки Махно, мастер пехотных боёв».
- Портреты по стандартам (пайплайн `tools/build_portraits.sh`, идемпотентен):
  `gfx/leaders/GLP/Portrait_GLP_Oleg_Potemkin_large.dds` (156×210 ARGB),
  `Portrait_GLP_Oleg_Potemkin.dds` (88×119 DXT5),
  `gfx/interface/ideas/idea_GLP_Oleg_Potemkin.dds` (65×67 DXT5, ванильная
  рамка министра). Спрайты — в `interface/GLP_portraits.gfx`.
- Локализация — в `GLP_characters_l_*.yml` (имя + черты + описания, RU/EN).
- **Важно:** оригинальное фото Потёмкина не сохранилось на диске — мастер
  `gfx/leaders/GLP/_src_oleg_potemkin.jpg` **регенерирован генератором по
  описанию фото** (папаха, серо-зелёная гимнастёрка, шашка, патронташ,
  пулевые отверстия). Если появится оригинал — заменить мастер и
  перезапустить `bash tools/build_portraits.sh`.

---

## 7. Чек-лист входа для первого шага

```
cd /path/to/GLP
python3 tools/glp_audit.py        # ожидается: 0 ошибок, 1 предупреждение (музыка)
git diff --check                  # ожидается: чисто
```
Затем — Спринт 6 (раздел 1) → 7 (раздел 2) → 8 (раздел 3), каждый с
негативными тестами новых инвариантов и итерацией в AUDIT_REPORT.md.
