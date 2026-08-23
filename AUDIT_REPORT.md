# Аудит мода «Гуляй-Поле» до AAA-качества (HOI4 1.19.2)

Дата аудита: 2026-08-23. Ветка: `arena/01a02ede-glp`.
Автоматическая проверка: `python3 tools/glp_audit.py` — **0 ошибок, 0 предупреждений**.

---

## 1. Найденные и устранённые дефекты

| # | Дефект | Последствия в игре | Что сделано |
|---|--------|--------------------|-------------|
| 1 | `common/national_focus/GLP_focus_expansion.txt` дублировал **92 фокуса** из `GLP_focus.txt` и при этом не был обёрнут ни в `focus_tree`, ни в `shared_focus` | ошибки парсера при загрузке, конфликт ID фокусов, «сломанное» дерево и расхождение чексуммы | файл удалён (все 92 ID уже присутствуют в основном дереве) |
| 2 | Кастомные черты генералов (`tachanka_commander`, `guerilla_master`) лежали в `/common/country_leader/` | движок 1.19.2 читает черты командиров только из `/common/unit_leader/` — черты молча не применялись | созданы заново в `common/unit_leader/GLP_unit_leader_traits.txt` с корректной схемой (`type`, `trait_type`, `gui_row/column`, `modifier`, `trait_xp_factor`) под именами `GLP_tachanka_commander`, `GLP_guerilla_master`, `GLP_steppe_raider` |
| 3 | Мод переопределял ванильные черты `cavalry_expert` и `aggressive_assaulter` (и их локализацию) | подмена ванильного текста/бонусов для всех стран, потенциальные конфликты с другими модами | переопределения удалены, персонажи используют ванильные черты напрямую |
| 4 | Портреты `*_large.dds` вообще не были подключены в `interface/GLP_portraits.gfx` | в игре везде показывались маленькие архивные фото вместо «живописных» портретов | все слоты `large` переведены на `Portrait_GLP_*_large.dds`, слоты `small` — на `gfx/interface/ideas/idea_GLP_*.dds` |
| 5 | Геометрия/формат .dds не соответствовали ТЗ: большие портреты 156x210, малые — DXT1 | «мыло», неверная рамка, отсутствие альфа-канала | конвейер `tools/build_portraits.sh`: большие → **156x224 DXT5**, малые и иконки советников → **156x210 DXT5** |
| 6 | Отсутствовал большой портрет Всеволода Волина | пустой слот портрета министра пропаганды | сгенерирован мастер `gfx/leaders/GLP/_src_vsevolod_volin_large.jpg` на базе архивного фото и собран `Portrait_GLP_Vsevolod_Volin_large.dds` |
| 7 | Отсутствовала русская и английская локализация для `GLP_idea_revvoensovet_partisan_command` и `GLP_idea_revvoensovet_total_preparedness` | в тултипах духа отображался «сырой» ключ | ключи и описания добавлены (UTF-8 **with BOM**) |
| 8 | 13 национальных духов не имели описаний (`*_desc`) | пустые тултипы | описания написаны на русском и английском |
| 9 | В трёх идеях использовался несуществующий модификатор `foreign_subversive_activities` | модификатор игнорировался движком | исправлено на ванильное написание `foreign_subversive_activites` |
| 10 | Профили черт персонажей не соответствовали ТЗ (Махно без Inspirational Leader/Panic, Белаш без Chief of Staff: Operational Planner, Щусь без Cavalry Leader, Задов без Head of Intelligence) | геймплейный профиль расходился с исторической ролью | все профили приведены к разделу 1 ТЗ (см. ниже) |

## 2. Итоговые профили персонажей

| Персонаж | Роль | Черты |
|----------|------|-------|
| Нестор Махно | глава государства (`anarchism`) + фельдмаршал | `batko_makhno`, `GLP_inspirational_leader`, `GLP_panic`; армия: `guerilla_fighter`, `trickster`, `cavalry_officer`, `offensive_doctrine`, `GLP_tachanka_commander` |
| Виктор Белаш | начальник штаба РПАУ, `corps_commander` + советник `army_chief` | `organizer`, `trickster`, `cavalry_expert`, `GLP_guerilla_master`; советник: `GLP_operational_planner` (Chief of Staff: Operational Planner) |
| Семён Каретник | командующий корпусом + `high_command` | `cavalry_expert`, `aggressive_assaulter`, `commando`; советник: `army_cavalry_2` |
| Феодосий Щусь | командующий кавалерией + `high_command` | `cavalry_leader`, `fast_planner`, `trait_reckless`, `GLP_steppe_raider`; советник: `army_cavalry_speed_2` |
| Лев (Александр) Задов | начальник РЗР, `corps_commander` + политсоветник | `trickster`, `commando`, `GLP_guerilla_master`; советник: `silent_workhorse`, `counter_intelligence_expert`, `GLP_head_of_intelligence` |
| Всеволод Волин | министр пропаганды, политсоветник | `ideological_crusader`, `free_soviets_minister` (Minister of Education: Free Soviets) |
| Галина Кузьменко | комиссар просвещения, политсоветник | `ideological_crusader` |
| Атаман Григорьев | союзник поневоле, `corps_commander` + `high_command` | `cavalry_officer`, `infantry_officer`, `guerilla_fighter`, `harsh_leader`, `trait_reckless` |

Жёстко заданные `id = <число>` в блоках `country_leader`/`corps_commander` **не используются** — движок 1.19.2 раздаёт идентификаторы сам, а ручные ID остаются классической причиной конфликта советников и вылета при загрузке сценариев 1936/1939. Уникальность всех `idea_token` проверяется автоматически.

## 3. Национальный дух «Чёрная Гвардия»

`GLP_black_guard_legacy` (`common/ideas/GLP_ideas.txt`) уже соответствует ТЗ и выдаётся стартово в `history/countries/GLP - Gulyaypole.txt`:

* `army_core_defence_factor = 0.25`, `army_core_attack_factor = 0.15`, `dig_in_speed_factor = 0.15` — мощная защита на коренных территориях;
* `cavalry_attack_factor = 0.15`, `cavalry_defence_factor = 0.10`, `cavalry_speed_factor = 0.10` — кавалерийское наследие;
* `out_of_supply_factor = 0.25`, `supply_consumption_factor = 0.10` — штраф за действия вне коренных стейтов.

## 4. Инструменты, добавленные в репозиторий

* `tools/glp_audit.py` — автоматический аудит: баланс скобок во всех скриптах, BOM и заголовки локализации, дубли ключей, дубли ID персонажей/советников/идей/фокусов/событий/спрайтов, целостность спрайтов и текстур, геометрия и компрессия .dds, покрытие локализацией, неизвестные черты. Код возврата 1 при ошибках — можно вешать в CI/pre-commit.
* `tools/build_portraits.sh` — сборка портретов из мастеров в .dds по спецификации (156x224 / 156x210, DXT5, без мип-мапов). Требует ImageMagick.

## 5. Что стоит проверить в самой игре (внешние зависимости)

1. Суб-идеология `anarchism` берётся из ванильного `common/ideologies` — при запуске убедиться, что лидер отображается корректно (`ruling_party = neutrality`).
2. Спрайты шайна фокусов ссылаются на ванильный `gfx/interface/goals/shine_overlay.dds` — путь намеренно оставлен базовым (аудит его белым списком не считает ошибкой).
3. Рекомендация на будущее (п. 2 ТЗ, патч 1.19): добавить отдельный шаблон «Чёрная Гвардия» на базе спецвойск и полковых поддержек — сейчас РПАУ использует обычные кавалерийские/стрелковые шаблоны.
