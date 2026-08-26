# Кинематографическая заставка «Гуляй-Поле» — HOI4 v1.19.2

**Автор:** Амброзиев О.А.  
**Стандарт:** AAA Photorealistic & PDX Technical Guidelines Compliance  
**Версия игры:** Hearts of Iron IV v.1.19.2

## Художественная концепция

Мрачный исторический нуар, ретроспективные архивные фотоматериалы 1918–1934 гг., состаренная бумага, угольно-черные и темно-коричневые тона. Элегантная золотая кайма и инкрустированные рамки высокого разрешения в стиле элитных модальных окон HOI4.

### Композиция экрана (900×700, centered)

1. **Левый верхний угол (30,30):** Исторический фотопортрет Нестора Ивановича Махно в суровом черно-белом исполнении с золотой окантовкой (156×210, `GFX_portrait_nestor_makhno_intro` + `GFX_political_leader_frame_gold`)
2. **Правый блок:**
   - Военная карта Юга Украины, Екатеринославской губернии периода Гражданской войны (550,304 — 320×260, `GFX_intro_ukraine_map`)
   - Сепированная фотокарточка махновской конницы на марше (550,110 — 320×160, `GFX_intro_makhno_cavalry`)
3. **Центрально-левая зона (x=210, y=86):** история Вольной республики обычным текстом — локализованное поле `GULYAIPOLE_EPIC_INTRO_TEXT` (шрифт `hoi_16mbs`, `maxWidth = 320`, `maxHeight = 540`, ползунок `standardtext_slider`). Рендерится штатным шрифтом игры, ограничен maxWidth/maxHeight и clipping — текст не выходит за пределы окна; длинная история листается ползунком под голос рассказчика. Анимированная лента титров удалена по ТЗ (аудит запрещает её остатки).
4. **Кнопка «Начать» (340,635):** Золотое тиснение, `GFX_button_221x34`, `GULYAIPOLE_START_BUTTON` = «Вольному воля!», shortcut ENTER — единственная кнопка окна.

### Аудиосопровождение

Автоматическое воспроизведение `voice.ogg` выполняет скрытое событие
`glp_cinematic_intro.1`: его `immediate`-блок вызывает
`sound_effect = gulyaipole_intro_voice` и `scoped_play_song = gulyaipole_intro_voice_music`.
Вся базовая фоновая музыка игры (`base_music`) снабжена модификатором
`factor = 0` при активном флаге `glp_show_cinematic_intro`, что полностью
исключает наложение музыки поверх голоса рассказчика.

- **Исходник:** `sound/voice.ogg` (OGG Vorbis, 44.1 kHz, 1 ch, ~2:45; мастер `voice.mp3` 2.5 МБ) — полный эпический пролог (Парижская эмиграция 1934 → возрождение Вольной Республики в 1936 → четыре пути → «Ведите Гуляй-Поле к свободе — или погибните вместе с ней!»). Решением автора оставлена исходная дорожка; тестовые дубли альтернативных дикторов отклонены. Фраза «Внимание! Говорит Гуляй-Поле!» использовалась только в демо-прослушиваниях голосов и в озвучку не входит.
- **Текст рассказчика:** полный эпический пролог (Парижская эмиграция 1934 → возрождение Вольной Республики в 1936 → четыре пути → «Ведите Гуляй-Поле к свободе — или погибните вместе с ней!»).
- Прежняя 157-секундная озвучка сохранена в `tools/_legacy_voice/` для истории.
- **Звуковая регистрация:** `sound/gulyaipole_sounds.asset` → категория `Voices` + низкоуровневый
  `sound` + `soundeffect` с именем `gulyaipole_intro_voice`.
- **Музыкальная регистрация:** `music/gulyaipole.asset` и
  `music/gulyaipole_songs.txt`; копия `music/voice.ogg` обеспечивает радио-воспроизведение.

В сборке используется валидный OGG Vorbis `sound/voice.ogg` (44.1 kHz, Vorbis). Аудит проверяет
всю цепочку автозапуска: `on_startup` → скрытое событие → `sound_effect` →
зарегистрированный OGG-файл.

## Архитектура файлов

```
/interface/gulyaipole_intro_custom.gui  — единое окно 900×700, centered, тёмная tiled-подложка
/interface/gulyaipole_intro.gfx         — декоративные спрайты:
    GFX_gold_inner_border                 -> gfx/interface/intro/gulyaipole_gold_inner_border.dds (900×700 DXT5, прозрачный центр, золотая кайма)
    GFX_portrait_nestor_makhno_intro      -> gfx/leaders/GLP/Portrait_GLP_Makhno_Intro_large.dds (156×210 ARGB, ч/б)
    GFX_political_leader_frame_gold       -> gfx/interface/intro/gulyaipole_portrait_frame_gold.dds (166×220 DXT5)
    GFX_intro_ukraine_map                 -> gfx/interface/intro/gulyaipole_ukraine_map.dds (320×260 DXT1, сепия карта)
    GFX_intro_makhno_cavalry              -> gfx/interface/intro/gulyaipole_cavalry.dds (320×160 DXT1, сепия конница)

/sound/gulyaipole_sounds.asset            — регистрация sound/soundeffect
/sound/voice.ogg                         — озвучка для sound_effect (OGG)
/music/gulyaipole.asset                  — регистрация voice.ogg как music asset
/music/gulyaipole_songs.txt              — отдельная станция с высоким весом
/music/voice.ogg                         — копия для music asset

/localisation/russian/gulyaipole_intro_text_l_russian.yml — локализация (BOM, l_russian)
/localisation/english/gulyaipole_intro_text_l_english.yml — английская версия

/common/scripted_guis/gulyaipole_intro_gui.txt — scripted GUI, visible по флагу;
    единственная кнопка — «Вольному воля!»
/events/GulyaipoleCinematicIntro.txt      — скрытое событие: флаг + sound_effect
/common/on_actions/GLP_on_actions.txt     — on_startup вызывает событие для GLP
/common/decisions/GLP_decisions.txt       — решение GLP_replay_cinematic_intro вызывает событие
```

## Текстуры — генерация

Исходники сгенерированы как AAA photorealistic через `generate_image`:

- `_src_tiled_bg_dark.png` — тёмная состаренная бумага, уголь, grain, noir
- `_src_gold_inner_border.png` — золотая инкрустированная рамка, baroque filigree
- `_src_makhno_intro.png` — ч/б портрет Махно, 1919, stern, papakha
- `_src_ukraine_map.png` — военная карта Екатеринославской губернии, сепия, Cyrillic, topographic
- `_src_makhno_cavalry.png` — конница на марше, dusty steppe, black flags, tachanka

Конвертация в DDS через ImageMagick 6.9 (как в `tools/build_*.sh`):

```bash
convert src.png -resize WxH -define dds:compression=dxt1/dxt5 -define dds:mipmaps=0 DDS:out.dds
```

- Портреты: 156×210 ARGB (large) + 88×119 DXT5 (medium) — соответствует SPEC_LARGE / SPEC_MEDIUM
- Фоны: 512×512 DXT1, без мип-мап
- Рамки: 900×700 DXT5 с альфа-каналом (прозрачный центр)

## Логика показа

1. `on_startup` (GLP) вызывает скрытое событие `glp_cinematic_intro.1`
2. Событие ставит флаг и вызывает
   `sound_effect = gulyaipole_intro_voice` → играет `sound/voice.ogg`
3. `scripted_gui = gulyaipole_cinematic_intro` видит флаг и показывает
   `gulyaipole_cinematic_intro_window` по центру
4. Игрок читает историю (текстовое поле с прокруткой, не выходит за
   пределы окна) под голос рассказчика и нажимает кнопку
5. Кнопка «Вольному воля!» → `clr_country_flag = glp_show_cinematic_intro`
   (и режимные флаги) → окно закрывается, далее `glp_news.100` (газета)
6. Решение «Пересмотреть вступление» в категории анархических мер позволяет
   открыть окно снова — режим сброшен в читаемый текст

## Соответствие ТЗ

- [x] Мрачный нуар, архивные фото 1918–1934, состаренная бумага, угольно-черные тона
- [x] Золотая кайма высокого разрешения
- [x] Левый верхний угол — портрет Махно ч/б с золотой окантовкой
- [x] Правый нижний угол — карта + фото конницы
- [x] Центр — история обычным текстом в пределах окна (поле с прокруткой); анимированная лента титров удалена по ТЗ
- [x] Кнопка «Вольному воля!» с золотым тиснением, ENTER
- [x] Аудио voice.ogg из voice.mp3, автовоспроизведение
- [x] Файлы по указанным путям
- [x] AAA Photorealistic & PDX Guidelines Compliance (DDS без мип-мап, BOM в локализации, правильные размеры портретов)
- [x] Audit: 0 errors

## Дальнейшее улучшение

- (лента титров удалена по ТЗ; при желании вернуть — см. git-историю итерации 6)
- При замене исходной озвучки перекодировать её в Vorbis и обновить `sound/voice.ogg` (например: `ffmpeg -i voice.mp3 -ar 44100 -ac 1 -c:a libvorbis -q:a 5 sound/voice.ogg`).
- Добавить виньетку и film grain overlay как отдельный спрайт с `alwaystransparent = yes`
