# Сторонние материалы

В текущей версии мода используются 3D-модели **пехоты-матроса**, **конницы
в чёрных папахах** и шашки из модификации
**Revolution or Reaction: Rise of Russia**.

Импортированы в `gfx/models/units/` и объявлены в
`gfx/entities/GLP_units.{asset,gfx}`:

- `RSR_marine*` — пехотинец-матрос (палубная/морская пехота), tag-specific
  `GLP_infantry_entity`;
- `NTC_cavalry*` — повстанческий конный всадник в чёрной папахе и черкеске;
- `russian_sword_sabre*` — шашка и ножны;
- `CHI_sword_sabre_*.dds` — локальные алиасы текстур ножен
  (holder-mesh ссылается на эти имена; DLC Waking the Tiger не требуется);
- пять анимаций сабельной конницы
  `russian_infantry_cavalry_rider_*_sabre.anim`.

Источник: <https://github.com/Gtym33/Kursach-Himiya>
(зафиксированная ревизия — `c69a9156b76c1cafa3098974b0432adcecd64909`, 2026-08-24).

Пехотные и кавалерийские сущности собраны явно (без кросс-файлового
`clone` на `infantry_rifle_entity` / `cavalry_entity`), по паттерну RSR.

Атрибуция:

- Команда и участники **Revolution or Reaction: Rise of Russia**.
- **Wolferos Productions Ltd. / Hearts of Iron IV: The Great War** —
  для материалов, восходящих к HOI4 TGW согласно уведомлению исходного
  репозитория.
- Уведомление исходного репозитория:
  [`Лицензия License.txt`](https://github.com/Gtym33/Kursach-Himiya/blob/master/%D0%9B%D0%B8%D1%86%D0%B5%D0%BD%D0%B7%D0%B8%D1%8F%20License.txt).
- Wolferos Shared Digital Media License:
  <https://www.wolferos.com/license/wsdml>.

Наличие материалов не означает поддержки или одобрения проекта авторами
Rise of Russia либо Wolferos.

---

## GFX-шаблоны и подложки (Ultimate-HOI4-GFX)

Для иконок министров/советников и национальных духов использованы шаблоны из
репозитория **Globvs/Ultimate-HOI4-GFX**
(<https://github.com/Globvs/Ultimate-HOI4-GFX>):

- `Portrait Templates/Minister Base.png` и
  `Portrait Templates/Minister Background.png` — ванильная рамка министра
  (65×67, тот же уголъ и размѣръ, что въ базовой игрѣ). Хранятся как
  `tools/_gfx_src/Minister_Base.png` / `Minister_Background.png`; сборка —
  `tools/build_portraits.sh`.
- `National Spirit Backgrounds/*.png` (Army, Shield, Soviet, Fire, Sun, Naval,
  Bars, Stop Sign, Intrigue, Military Police, Upgrade, Tiles, Pentagon, Ring,
  Circle) — тематические подложки духов 60×68. Хранятся как
  `tools/_gfx_src/bg_*.png`; сборка — `tools/build_spirit_icons.sh`.

Согласно `CREDITS.txt` репозитория, материалы предоставлены «all with consent,
and all free to use». Атрибуция — авторам Ultimate-HOI4-GFX и перечисленным в
их CREDITS.txt контрибуторам (HOI4 GFX Modding Database, ThePinkPanzer,
Pacifica, Deathlinger, Edouard_Saladier и др.).

Наличие материалов не означает поддержки или одобрения проекта авторами
Ultimate-HOI4-GFX.
