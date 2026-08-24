# Сторонние материалы

В текущей версии мода **сторонние материалы не используются**.

Ранее в `gfx/entities/GLP_units.{asset,gfx}` и `gfx/models/units/*` были
импортированы 3D-модели и анимации пехоты/конницы из модификации
**Revolution or Reaction: Rise of Russia** (донская казачья конница
`DON_cavalry*`, русская пехота и зимняя пехота `RSR_infantry*`, шашка с
ножнами `russian_sword_sabre*`, пять анимаций сабельной конницы
`russian_infantry_cavalry_rider_*_sabre.anim`). Источник:
<https://github.com/Gtym33/Kursach-Homiya> (зафиксированная ревизия —
`c69a9156b76c1cafa3098974b0432adcecd64909`, 2026-08-24).

После выявленного краша рендера (предположительно из-за кросс-файловых
`clone` на cavalry-сущности в исходной компоновке) все импортированные
файлы удалены, `gfx/entities/GLP_units.*` и каталог `gfx/models/units/`
более не существуют. `GLP` использует ванильные
`infantry_rifle_entity` / `cavalry_entity` / `cavalry_2_entity` по
`graphical_culture = eastern_european_gfx`. Аудит (`tools/glp_audit.py`)
запрещает повторно подкладывать импортированные mesh/anim/asset и
любые ссылки на имена `GLP_*_entity`, `RSR_infantry`, `DON_cavalry`,
`russian_sword_sabre`, `russian_infantry_cavalry_rider_*`.

При дальнейшем распространении эта атрибуция сохраняется в качестве
исторической ссылки на исходные правообладатели:

- Команда и участники **Revolution or Reaction: Rise of Russia**.
- **Wolferos Productions Ltd. / Hearts of Iron IV: The Great War** —
  для материалов, восходящих к HOI4 TGW согласно уведомлению исходного
  репозитория.
- Уведомление исходного репозитория:
  [`Лицензия License.txt`](https://github.com/Gtym33/Kursach-Homiya/blob/master/%D0%9B%D0%B8%D1%86%D0%B5%D0%BD%D0%B7%D0%B8%D1%8F%20License.txt).
- Wolferos Shared Digital Media License:
  <https://www.wolferos.com/license/wsdml>.

Отсутствие материалов в текущей версии GLP не означает поддержки или
одобрения проекта авторами Rise of Russia либо Wolferos; атрибуция
сохраняется как подтверждение прошлого использования и соблюдения
условий исходных правообладателей.
