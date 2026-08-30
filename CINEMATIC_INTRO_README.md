# Кинематографическая заставка «Гуляй-Поле» — HOI4 v1.19.2

**Автор:** iziwavez  
**Стандарт:** AAA Photorealistic & PDX Technical Guidelines Compliance  
**Версия игры:** Hearts of Iron IV v1.19.2

> **Аудит 26.08.2026 — заставка восстановлена.** Обнаружена и устранена
> причина исчезновения фона и фотографий в окне (см. раздел «Аудит»).
> Все текстуры окна пересобраны через `tools/build_intro.sh`.

## Художественная концепция

Мрачный исторический нуар, ретроспективные архивные фотоматериалы 1918–1934 гг., состаренная бумага, угольно-черные и темно-коричневые тона. Элегантная золотая кайма и инкрустированные рамки высокого разрешения в стиле элитных модальных окон HOI4.

### Композиция экрана (900×700, centered)

1. **Левый верхний угол (30,30):** Исторический фотопортрет Нестора Ивановича Махно в суровом черно-белом исполнении с барочной золотой окантовкой (156×210, `GFX_portrait_nestor_makhno_intro` + `GFX_political_leader_frame_gold`).
2. **Правый блок:**
   - Сепированная фотокарточка махновской конницы на марше (550,108 — 320×160, `GFX_intro_makhno_cavalry`).
   - Военная карта Юга Украины, Екатеринославской губернии периода Гражданской войны (550,302 — 320×260, `GFX_intro_ukraine_map`).
3. **Центральная колонка (210,86):** история Вольной республики одним локализованным текстовым полем `GULYAIPOLE_EPIC_INTRO_TEXT` (шрифт `hoi_16mbs`, `maxWidth = 320`, `maxHeight = 540`, вертикальная прокрутка `standardtext_slider`). Анимированная лента титров и режим переключения — см. раздел «Аудит» (удалены).
4. **Кнопка «Вольному воля!» (340,635):** золотое тиснение, `GFX_button_221x34`, `GULYAIPOLE_START_BUTTON`, shortcut ENTER; центрирована по окну.

### Аудиосопровождение

Автоматическое воспроизведение `voice.ogg` выполняет скрытое событие
`glp_cinematic_intro.1`: его `immediate`-блок вызывает
`sound_effect = gulyaipole_intro_voice` и `scoped_play_song = gulyaipole_intro_voice_music`.
Вся базовая фоновая музыка игры (`base_music`) снабжена модификатором
`factor = 0` при активном флаге `glp_show_cinematic_intro`, что полностью
исключает наложение музыки поверх голоса рассказчика.

- **Исходник:** `sound/voice.ogg` (OGG Vorbis, 44.1 kHz, 1 ch, ~2:45; мастер
  `voice.mp3` 2.5 МБ). **Текст рассказчика:** полный эпический пролог (Парижская
  эмиграция 1934 → возрождение Вольной Республики в 1936 → четыре пути →
  «Ведите Гуляй-Поле к свободе — или погибните вместе с ней!»). Решением автора
  оставлена исходная дорожка; тестовые дубли альтернативных дикторов отклонены.
  Фраза «Внимание! Говорит Гуляй-Поле!» использовалась только в демо-прослушиваниях
  голосов и в озвучку не входит.
- Прежняя 157-секундная озвучка сохранена в `tools/_legacy_voice/` для истории.
- **Звуковая регистрация:** `sound/gulyaipole_sounds.asset` → категория `Voices` + низкоуровневый `sound` + `soundeffect` с именем `gulyaipole_intro_voice`.
- **Музыкальная регистрация:** `music/gulyaipole.asset` и `music/gulyaipole_songs.txt`; копия `music/voice.ogg` обеспечивает радио-воспроизведение.

В сборке используется валидный OGG Vorbis `sound/voice.ogg` (44.1 kHz, Vorbis).
Аудит проверяет всю цепочку автозапуска: `on_startup` → скрытое событие →
`sound_effect` → зарегистрированный OGG-файл.

## Архитектура файлов

```
/interface/gulyaipole_intro_custom.gui  — единое окно 900×700, centered, подложка-бумага
/interface/gulyaipole_intro.gfx         — декоративные спрайты:
    GFX_intro_bg                        -> gfx/interface/intro/gulyaipole_intro_bg.dds (900×700 DXT1, состаренная бумага)
    GFX_tiled_bg_dark / GFX_tiled_bg_dark_tiled -> та же текстура (общая с оверрайдом политического окна)
    GFX_gold_inner_border               -> gfx/interface/intro/gulyaipole_gold_inner_border.dds (900×700 DXT5, барочная кайма, прозрачный центр)
    GFX_portrait_nestor_makhno_intro    -> gfx/leaders/GLP/Portrait_GLP_Makhno_Intro_large.dds (156×210, ч/б)
    GFX_political_leader_frame_gold     -> gfx/interface/intro/gulyaipole_portrait_frame_gold.dds (166×220 DXT5, барочный пояс 14 px)
    GFX_intro_ukraine_map               -> gfx/interface/intro/gulyaipole_ukraine_map.dds (320×260 DXT1, сепия карта)
    GFX_intro_makhno_cavalry            -> gfx/interface/intro/gulyaipole_cavalry.dds (320×160 DXT1, сепия конница)

/sound/gulyaipole_sounds.asset            — регистрация sound/soundeffect
/sound/voice.ogg                          — озвучка для sound_effect (OGG)
/music/gulyaipole.asset                   — регистрация voice.ogg как music asset
/music/gulyaipole_songs.txt               — отдельная станция с высоким весом
/music/voice.ogg                          — копия для music asset

/localisation/russian/gulyaipole_intro_text_l_russian.yml — локализация (BOM, l_russian)
/localisation/english/gulyaipole_intro_text_l_english.yml — английская версия

/common/scripted_guis/gulyaipole_intro_gui.txt — scripted GUI, visible по флагу
/events/GulyaipoleCinematicIntro.txt          — скрытое событие: флаг + sound_effect
/common/on_actions/GLP_on_actions.txt         — on_startup вызывает событие для GLP
/common/decisions/GLP_decisions.txt           — решение GLP_replay_cinematic_intro вызывает событие

/tools/build_intro.sh                       — сборка текстур окна (см. ниже)
```

## Текстуры — генерация (`tools/build_intro.sh`)

Все текстуры окна пересобираются скриптом из ПРАВИЛЬНЫХ исходников
(требуется ImageMagick 6.9 + python3/Pillow; на выходе — контроль
размеров/формата/содержания):

- `gfx/interface/_src_tiled_bg_dark.png` (1024×1024) — тёмная состаренная
  бумага, уголь, grain, noir → `gulyaipole_intro_bg.dds` 900×700 DXT1
  (центральный кроп + `modulate 160,102,108`: подъём яркости, тёплый сдвиг;
  **без `-tint`** — в ImageMagick 6.9 он на низкой насыщенности затемняет
  картинку втрое).
- `gfx/interface/_src_gold_inner_border.png` (1168×912) — барочная золотая
  рамка, baroque filigree → `gulyaipole_gold_inner_border.dds` 900×700 DXT5
  (flood-fill превращает «фейковую шахматку» центра и чёрные углы в настоящий
  alpha=0; кайма затухает от края: 28 px сплошной пояс + градиент до 72 px,
  чтобы не перекрывать текст и фото).
- Та же барочная рамка, масштаб 166×220 → `gulyaipole_portrait_frame_gold.dds`
  DXT5; оставляется только внешний пояс 14 px (проём 138×192 прозрачен),
  портрет 156×210 читается в проёме.
- Фото (конница, карта) и ч/б портрет Батьки — **не пересобираются**:
  аудиторной декодировкой DDS подтверждено, что текущие файлы годны.

### НЕ использовать (деградированные промежуточные исходники)

`tools/_gfx_src/{gold_inner_border_clean,portrait_frame_gold_final,intro_bg_clean}.png`
— артефакты автоматической «чистки» фона (тонкие линии, 90 %+ прозрачности /
почти чёрный фон). Именно они легли в основу сломанных текстур 26.08.2026.
Сборка идёт строго из `_src_*` исходников выше.

## Логика показа

1. `on_startup` (GLP) вызывает скрытое событие `glp_cinematic_intro.1`
2. Событие ставит флаг и вызывает
   `sound_effect = gulyaipole_intro_voice` → играет `sound/voice.ogg`
3. `scripted_gui = gulyaipole_cinematic_intro` видит флаг и показывает
   `gulyaipole_cinematic_intro_window` по центру
4. Игрок читает текст (прокрутка), озвучка идёт ~2:45
5. Кнопка «Вольному воля!» → `clr_country_flag = glp_show_cinematic_intro`
   (+ старые режимные флаги `glp_intro_manual_mode` / `glp_intro_crawl_mode`
   для совместимости с сохранениями) → окно закрывается, далее `glp_news.100` (газета)
6. Решение «Пересмотреть вступление» в категории анархических мер позволяет открыть окно снова

## Аудит 26.08.2026: «Пропал фон, фотографии» — причины и исправления

**Симптом:** в окне заставки исчезали фон, портрет, фото конницы и карта;
оставались только заголовок, подписи и кнопки (ванильные спрайты).

**Диагностика** (полная цепочка: gui → gfx → dds → scripted gui → события →
локализация → звук; DDS декодировались независимо — ImageMagick/Pillow):

1. **Кайма окна и рамка портрета были собраны из деградированных «clean»
   исходников** — `gulyaipole_gold_inner_border.dds` (94,8 % прозрачных
   пикселей) и `gulyaipole_portrait_frame_gold.dds` (89,7 %) — декор был
   невидим, окно читалось как «голое» чёрное поле.
   *Исправлено:* пересборка из `gfx/interface/_src_gold_inner_border.png`
   (flood-fill альфа + затухание каймы, см. выше).
2. **Фон был почти чёрным** (`intro_bg_clean.png`, средняя яркость ~14 %) —
   панель не отделялась от тёмного фона игры. *Исправлено:* пересборка из
   `_src_tiled_bg_dark.png` с подъёмом яркости (средняя ~19 %).
3. **Анимированная лента титров `GFX_intro_text_crawl`** (spriteType с блоком
   `animation` в `gulyaipole_intro.gfx`) — источник «исчезновения» спрайтов
   всего файла: с ней в игре не отрисовывались и `GFX_intro_bg`, и
   фотографии. Лента была удалена (дизайн подтверждён ранее собранным
   вариантом: история — обычным локализованным текстовым полем), вместе с
   кнопкой-переключателем режимов и её scripted-localisation
   (`common/scripted_localisation/GLP_intro_loc.txt`), текстурами
   `gulyaipole_text_{base,mask,crawl}.dds` и неиспользуемой копией
   `gulyaipole_tiled_bg_dark.dds`.
4. Проверено и подтверждено годным: `gulyaipole_cavalry.dds`,
   `gulyaipole_ukraine_map.dds`, `Portrait_GLP_Makhno_Intro{,_large}.dds`
   (реальный сепийный/ч/б контент, корректные заголовки DXT1/DXT5/ARGB);
   скриптовая цепочка `on_startup → glp_cinematic_intro.1 → sound_effect +
   scoped_play_song` (регистрации в `sound/gulyaipole_sounds.asset`,
   `music/gulyaipole.asset`, `music/*songs.txt`); все локализационные ключи
   окна присутствуют в `l_russian`/`l_english` (BOM на месте); решение
   повтора `GLP_replay_cinematic_intro` целено.

**Итог:** `tools/glp_audit.py` — 0 ошибок (1 предсуществующее предупреждение
о совпадающих .ogg в `music/`).

## Соответствие ТЗ

- [x] Мрачный нуар, архивные фото 1918–1934, состаренная бумага, угольно-черные тона
- [x] Золотая кайма высокого разрешения (барочная, с прозрачным центром)
- [x] Левый верхний угол — портрет Махно ч/б с золотой окантовкой
- [x] Правый блок — фото конницы + карта
- [x] Центр — текст с вертикальной прокруткой (прозрачная подложка)
- [x] Кнопка «Вольному воля!» с золотым тиснением, ENTER
- [x] Аудио voice.ogg из voice.mp3, автовоспроизведение
- [x] Файлы по указанным путям
- [x] AAA Photorealistic & PDX Guidelines Compliance (DDS без мип-мап, BOM в локализации, правильные размеры портретов)
- [x] Audit: 0 errors

## Дальнейшее улучшение

- Добавить виньетку и film grain overlay как отдельный спрайт с `alwaystransparent = yes`
- При желании вернуть кинематографичный режим титров — только через отдельное
  текстурированное окно-слой (не спрайтом с `animation` в общем .gfx), чтобы
  не повторить регрессию п. 3 аудита.
