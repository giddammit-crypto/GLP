# Сторонние материалы

В текущей версии мода используются 3D-модели **донской казачьей конницы**,
**чёрной повстанческой пехоты**, **белых добровольческих частей
(корниловцы и дроздовцы)** и шашки из модификации
**Revolution or Reaction: Rise of Russia**.

Импортированы в `gfx/models/units/` и объявлены в
`gfx/entities/GLP_units.{asset,gfx}`:

- `DON_cavalry*` — донской казачий всадник;
- `RSR_marine*` — чёрный бушлат с пулемётными лентами крест-накрест
  (модель «моряка-повстанца»; большевистские красная звезда на бескозырке
  и красная нарукавная полоса перекрашены в чёрный — РПА большевистскую
  символику не носила; редактура собственная);
- `KORN_cavalry*` — белая ударная кавалерия с красным околышем фуражки;
  отдаётся ТОЛЬКО элитному подразделению `kornilovtsy`;
- `DROZD_stormtroopers*` — белые штурмовики полковника Дроздовского;
  отдаётся ТОЛЬКО элитному подразделению `drozdovtsy`;
- `russian_sword_sabre*` — шашка и ножны;
- `CHI_sword_sabre_*.dds` — локальные алиасы текстур ножен
  (holder-mesh ссылается на эти имена; DLC Waking the Tiger не требуется);
- пять анимаций сабельной конницы
  `russian_infantry_cavalry_rider_*_sabre.anim`.

Источник: <https://github.com/Gtym33/Kursach-Himiya>
(зафиксированная ревизия — `c69a9156b76c1cafa3098974b0432adcecd64909`, 2026-08-24).

Отдельных моделей махновистов (чёрной армии) в Rise of Russia нет;
тематически ближайшие — чёрный бушлат и казачий всадник — и взяты за
основу. Пехота `RSR_infantry*` (с красной звездой) **не** импортируется.
Все сущности собраны явно (без кросс-файлового `clone`), по паттерну RSR:
`GLP_infantry_entity`, `GLP_cavalry_entity`, `GLP_cavalry_2_entity`,
`GLP_kornilovtsy_entity`, `GLP_drozdovtsy_entity`.
Дивизионные токены `kornilovtsy`/`drozdovtsy` объявлены в
`common/units/GLP_white_units.txt`; появляются только в OOB фокуса
«Старые враги» (`history/units/GLP_old_enemies.txt`).

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
