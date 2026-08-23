# Отчёт по иконкам — Гуляйполе

Подбор выполнен через каталог **HOI4 Icon Search**: <https://wyandotte.github.io/hoi4-icon-search/> (витрина данных репозитория `kr4/icons`: 1960 иконок фокусов + 1294 духа/советника).

**Метод проверки.** Каждое имя спрайта сверено с ванильными файлами базовой игры `interface/goals.gfx` / `interface/ideas.gfx` (дампы **1.7.1 Hydra** и **1.14.10**): используются **только спрайты базовой игры — никаких DLC-зависимостей** (DLC-иконки каталога — tfv/wtt/dod/bftb и пр. — и 1325 иконок Kaiserreich не используются). Примечание: каталог немного старее текущей игры — 59 выбранных спрайтов добавлены в базу позже и в каталоге отсутствуют; для них указан точный путь в файлах игры.

**Сводка**

| Категория | Всего | Уникальных иконок | Макс. повторов использования |
|---|---|---|---|
| Фокусы | 190 | **118** | 5 (`mass_production` — производственные ветки) |
| Национальные духи | 118 | 15 своих GLP + 29 ванильных | 17 (`production_bonus`) |

## Иконки дерева фокусов (190)

| Фокус | Иконка | Источник/ссылка |
|---|---|---|
| Продвинутая металлургия | `GFX_focus_generic_steel` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_steel.png) |
| Агентурные сети | `GFX_focus_generic_secret_service_agency` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_secret_service_agency.dds` |
| Сельскохозяйственные исследования | `GFX_focus_generic_socialist_science` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_socialist_science.png) |
| Братская помощь CNT-FAI | `GFX_focus_generic_invite_republican_spanish_exiles` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_invite_republican_spanish_exiles.dds` |
| Воздушная разведка | `GFX_goal_generic_radar` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_radar.png) |
| Доктрина превосходства в воздухе | `GFX_goal_generic_air_fighter2` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_air_fighter2.png) |
| Договор с Великобританией | `GFX_goal_generic_major_alliance` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_major_alliance.png) |
| Пакт с Германией | `GFX_goal_generic_alliance` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_alliance.png) |
| Союз с Советским Союзом | `GFX_focus_generic_join_comintern` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_join_comintern.png) |
| Противовоздушная оборона | `GFX_focus_generic_air_defense` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_air_defense.png) |
| Антигосударственный поход | `GFX_goal_generic_major_war` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_major_war.png) |
| Противотанковая конница | `GFX_focus_generic_anti_tank_guns` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_anti_tank_guns.dds` |
| Противотанковая оборона | `GFX_focus_generic_anti_tank_guns` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_anti_tank_guns.dds` |
| Бронетанковые исследования | `GFX_goal_generic_build_tank` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_build_tank.png) |
| Производство бронепоездов РПА | `GFX_focus_generic_railway_gun` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_railway_gun.dds` |
| Автаркический рай | `GFX_focus_generic_modernize_industry` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_modernize_industry.dds` |
| Автономный индустриальный бастион | `GFX_focus_generic_industry_2` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_industry_2.png) |
| Балканская анархистская федерация | `GFX_focus_generic_balkan_diplomacy` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_balkan_diplomacy.dds` |
| Оплот свободных наций | `GFX_goal_generic_fortify_city` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_fortify_city.png) |
| В тылу врага | `GFX_goal_generic_occupy_states_ongoing_war` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_occypy_states_ongoing_war.png) |
| Авангард Черного Знамени | `GFX_focus_generic_red_flags` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_red_flags.dds` |
| Черный Полумесяц Вольных Степей | `GFX_focus_generic_welfare` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_welfare.dds` |
| Помощь Чёрного Креста | `GFX_focus_generic_welfare` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_welfare.dds` |
| Черный крест степей | `GFX_goal_generic_improve_relations` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_improve_relations.png) |
| Черный Интернационал | `GFX_goal_generic_major_alliance` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_major_alliance.png) |
| Черная военная диктатура | `GFX_focus_generic_military_dictatorship` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_military_dictatorship.dds` |
| Господство на Чёрном море | `GFX_focus_generic_black_sea_focus` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_black_sea_focus.dds` |
| Судоверфи Черного моря | `GFX_focus_generic_refit_civilian_ships` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_refit_civilian_ships.dds` |
| Бомбардировочные крылья | `GFX_goal_generic_air_bomber` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_air_bomber.png) |
| Пограничные укрепления | `GFX_focus_generic_coastal_fort` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_coastal_fort.png) |
| Безопасность границ | `GFX_focus_generic_national_security` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_national_security.dds` |
| Хлеб для городов и фронта | `GFX_focus_generic_welfare` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_welfare.dds` |
| Житница Европы | `GFX_focus_generic_farmland` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_farmland.dds` |
| Сеть бункеров | `GFX_goal_generic_fortify_city` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_fortify_city.png) |
| Изучение трофейного вооружения | `GFX_focus_generic_license_production` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_license_production.png) |
| Химическая промышленность | `GFX_focus_generic_rubber` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_rubber.png) |
| Кинопропаганда | `GFX_focus_generic_printing_press` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_printing_press.dds` |
| Расширение гражданской промышленности | `GFX_goal_generic_construct_civ_factory` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_construct_civ_factory.png) |
| Береговые батареи | `GFX_focus_generic_coastal_fort` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_coastal_fort.png) |
| Шифрованная связь | `GFX_focus_generic_radio_communication` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_radio_communication.dds` |
| Коллективное земледелие | `GFX_focus_generic_agricultural_subsidies` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_agricultural_subsidies.dds` |
| Мастерство общевойскового боя | `GFX_focus_generic_combined_arms` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_combined_arms.png) |
| Коммандос | `GFX_focus_generic_self_propelled_gun` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_self_propelled_gun.dds` |
| Общинные зернохранилища и элеваторы | `GFX_focus_generic_agricultural_subsidies` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_agricultural_subsidies.dds` |
| Вычислительные машины | `GFX_focus_generic_cryptologic_bomb` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_cryptologic_bomb.png) |
| Казачьи кавалерийские дивизии | `GFX_goal_generic_cavalry` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_cavalry.png) |
| Казачья слава | `GFX_goal_generic_special_forces` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_special_forces.png) |
| Казачье наследие | `GFX_goal_generic_cavalry` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_cavalry.png) |
| Казачье наследие | `GFX_goal_generic_defence` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_defence.png) |
| Казачий офицерский корпус | `GFX_focus_generic_military_academy` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_military_academy.png) |
| Мастерство клинка и пулемета | `GFX_goal_generic_cavalry` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_cavalry.png) |
| Сохранение казачьих традиций | `GFX_goal_generic_national_unity` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_national_unity.png) |
| Сеть контршпионажа | `GFX_focus_generic_secret_service_agency` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_secret_service_agency.dds` |
| Развитие Крыма | `GFX_focus_generic_public_works` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_public_works.dds` |
| Крымские нефтяные месторождения | `GFX_focus_generic_offshore_oil_rig` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_offshore_oil_rig.dds` |
| Отдел криптоанализа | `GFX_focus_generic_cryptologic_bomb` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_cryptologic_bomb.png) |
| Культурное просвещение | `GFX_focus_generic_welfare` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_welfare.dds` |
| Сеть децентрализованных мастерских | `GFX_focus_generic_mass_production` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_mass_production.dds` |
| Декларация Мировой Анархии | `GFX_focus_generic_strike_at_democracy3` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_strike_at_democracy3.png) |
| Декрет о Черном терроре | `GFX_focus_generic_conspiracy` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_conspiracy.dds` |
| Доктрина глубокой операции | `GFX_focus_generic_army_doctrines_2` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_army_doctrines_2.dds` |
| Оборона в глубину | `GFX_focus_generic_defensive_reorganization` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_defensive_reorganization.dds` |
| Кампании дезинформации | `GFX_goal_generic_propaganda` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_propaganda.png) |
| ДнепроГЭС: электрификация степи | `GFX_focus_generic_hydroelectric_energy` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_hydroelectric_energy.dds` |
| Шахтерские и металлургические коллективы Донбасса | `GFX_focus_generic_coal_mining` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_coal_mining.dds` |
| Двойные агенты | `GFX_focus_generic_whispers` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_whispers.dds` |
| Экономическая независимость | `GFX_goal_generic_trade` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_trade.png) |
| Экономическое чудо | `GFX_focus_generic_economic_recovery` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_economic_recovery.dds` |
| Элитные гвардейские части | `GFX_goal_generic_special_forces` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_special_forces.png) |
| Укрепление фабричных коммун | `GFX_focus_generic_workers_and_farmers_rise` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_workers_and_farmers_rise.dds` |
| Евразийский Красно-Черный Авангард | `GFX_focus_generic_red_flags` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_red_flags.dds` |
| Экспансия железного кулака | `GFX_goal_generic_political_pressure` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_political_pressure.png) |
| Фабричные комитеты | `GFX_focus_generic_workers` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_workers.dds` |
| Федерация вольных Советов | `GFX_focus_generic_self_management` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_self_management.png) |
| Женские боевые части | `GFX_focus_generic_women_in_military` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_women_in_military.dds` |
| Полевые госпитали | `GFX_focus_generic_field_hostpital` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_field_hostpital.dds` |
| Истребительные эскадрильи | `GFX_goal_generic_air_fighter` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_air_fighter.png) |
| Процветающая вольная деревня | `GFX_focus_generic_public_works` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_public_works.dds` |
| Переработка продовольствия | `GFX_focus_generic_farmland` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_farmland.dds` |
| IV Съезд крестьян, рабочих и повстанцев | `GFX_focus_generic_workers_and_farmers_rise` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_workers_and_farmers_rise.dds` |
| Свободные школы и ликвидация неграмотности | `GFX_focus_generic_university_3` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_university_3.dds` |
| Свободные университеты | `GFX_focus_generic_university_1` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_university_1.dds` |
| Вольному воля | `GFX_goal_generic_neutrality_focus` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_neutrality_focus.png) |
| Фронтовая разведка | `GFX_goal_generic_position_armies` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_position_armies.png) |
| Синтез топлива | `GFX_focus_generic_stockpile_fuel` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_stockpile_fuel.dds` |
| Полная занятость | `GFX_focus_generic_full_employment` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_full_employment.dds` |
| Гендерное равенство | `GFX_focus_generic_universal_suffrage` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_universal_suffrage.dds` |
| Глобальная анархистская сеть | `GFX_goal_generic_military_sphere` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_military_sphere.png) |
| Слава моря | `GFX_goal_generic_navy_battleship` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_navy_battleship.png) |
| Штурмовая авиация | `GFX_goal_generic_CAS` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_CAS.png) |
| Рывок тяжёлой промышленности | `GFX_focus_generic_military_industry` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_military_industry.dds` |
| Коневодство | `GFX_focus_generic_horse_studs` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_horse_studs.dds` |
| Санитарные поезда | `GFX_focus_generic_supply_line` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_supply_line.dds` |
| Непробиваемая разведка | `GFX_focus_generic_cryptologic_bomb` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_cryptologic_bomb.png) |
| Улучшенное вооружение | `GFX_goal_generic_small_arms` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_small_arms.png) |
| Промышленная сверхдержава | `GFX_focus_generic_industry_3` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_industry_3.png) |
| Модернизация инфраструктуры | `GFX_focus_generic_improve_roads` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_improve_roads.dds` |
| Реорганизация Повстанческой Армии | `GFX_goal_generic_army_doctrines` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_army_doctrines.png) |
| Управление внутренней безопасности | `GFX_goal_generic_political_pressure` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_political_pressure.png) |
| Интернациональные бригады | `GFX_goal_generic_allies_build_infantry` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_allies_build_infantry.png) |
| Дипломатический выбор Гуляйполя | `GFX_goal_generic_improve_relations` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_improve_relations.png) |
| Несокрушимое восстание | `GFX_goal_generic_defence` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_defence.png) |
| Реактивные двигатели | `GFX_focus_generic_jet_planes` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_jet_planes.dds` |
| Совместная военная академия | `GFX_focus_generic_military_academy` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_military_academy.png) |
| Реорганизация Контрразведки РПА | `GFX_goal_generic_intelligence_exchange` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_intelligence_exchange.png) |
| Поставки вооружений от Krupp | `GFX_focus_generic_license_production` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_license_production.png) |
| Декрет: Земля тем, кто её обрабатывает | `GFX_focus_generic_land_reclamation` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_land_reclamation.dds` |
| Легендарные тачанки | `GFX_goal_generic_cavalry` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_cavalry.png) |
| Суды чести и народные сходы | `GFX_focus_generic_court` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_court.dds` |
| Свободная железнодорожная сеть юга | `GFX_focus_generic_railroad` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_railroad.dds` |
| Кампания по ликвидации неграмотности | `GFX_focus_generic_printing_press` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_printing_press.dds` |
| Местная добыча ресурсов | `GFX_focus_generic_mining_industry` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_mining_industry.dds` |
| Мастерство логистики | `GFX_focus_generic_supply_line` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_supply_line.dds` |
| Миф о Махно | `GFX_focus_generic_printing_press` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_printing_press.dds` |
| Тактика массированного штурма | `GFX_focus_generic_total_war` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_total_war.dds` |
| Владыки небес | `GFX_goal_generic_air_doctrine` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_air_doctrine.png) |
| Механизированное сельское хозяйство | `GFX_focus_generic_mechanized` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_mechanized.dds` |
| Медицинская подготовка | `GFX_focus_generic_military_academy` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_military_academy.png) |
| Флот рейдеров | `GFX_focus_generic_merchant_fleet` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_merchant_fleet.dds` |
| Всплеск военного производства | `GFX_focus_generic_mass_production` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_mass_production.dds` |
| Моторный транспорт | `GFX_focus_generic_truck` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_truck.dds` |
| Морская авиация | `GFX_goal_generic_air_naval_bomber` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_air_naval_bomber.png) |
| Морская пехота РПА | `GFX_focus_generic_naval_invasion` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_naval_invasion.dds` |
| Новая советская культура | `GFX_focus_generic_self_management` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_self_management.png) |
| Старые враги | `GFX_focus_generic_little_entente` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_little_entente.png) |
| Партизанские ячейки | `GFX_focus_generic_forest_brothers` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_forest_brothers.dds` |
| Доктрина партизанской войны | `GFX_focus_generic_forest_brothers` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_forest_brothers.dds` |
| Поставки продовольствия от вольных крестьян | `GFX_focus_generic_farmland` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_farmland.dds` |
| Гармония крестьянского и умственного труда | `GFX_goal_generic_national_unity` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_national_unity.png) |
| Патрули народной стражи | `GFX_goal_generic_defence` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_defence.png) |
| Помощь персидским революционерам | `GFX_focus_generic_military_mission` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_military_mission.png) |
| Философия свободы | `GFX_goal_generic_neutrality_focus` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_neutrality_focus.png) |
| Рост населения | `GFX_focus_generic_population_growth` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_population_growth.dds` |
| Бонусы за производительность | `GFX_focus_generic_mass_production` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_mass_production.dds` |
| Ликвидация белогвардейских заговоров | `GFX_focus_generic_strike_at_democracy2` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_strike_at_democracy2.png) |
| Радиотехнологии | `GFX_focus_generic_radio_communication` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_radio_communication.dds` |
| Расширение железных дорог | `GFX_focus_generic_railroad` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_railroad.dds` |
| Стремительная ж/д переброска | `GFX_focus_generic_supply_line` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_supply_line.dds` |
| Координация сопротивления | `GFX_goal_generic_position_armies` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_position_armies.png) |
| Революционные эсминцы | `GFX_focus_generic_destroyer` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_destroyer.png) |
| Революционный театр | `GFX_goal_generic_propaganda` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_propaganda.png) |
| Бронетанковое и железнодорожное управление | `GFX_goal_generic_army_tanks` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_army_tanks.png) |
| Координация военных мастерских | `GFX_focus_generic_military_industry` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_military_industry.dds` |
| Ракетная наука | `GFX_focus_rocketry` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_rocketry.png) |
| Сеть земской медицины | `GFX_focus_generic_field_hostpital` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_field_hostpital.dds` |
| Диверсионная подготовка | `GFX_goal_generic_special_forces` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_special_forces.png) |
| Сеть конспиративных квартир | `GFX_focus_generic_conspiracy` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_conspiracy.dds` |
| Санитарные батальоны | `GFX_focus_generic_field_hostpital` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_field_hostpital.dds` |
| Научные лаборатории вольных коммун | `GFX_focus_generic_socialist_science` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_socialist_science.png) |
| Самодостаточная экономика | `GFX_focus_generic_resource_extraction` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_resource_extraction.dds` |
| Военно-морская база Севастополь | `GFX_goal_generic_occupy_states_coastal` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_occypy_states_coastal.png) |
| Модернизация верфей с Royal Navy | `GFX_focus_generic_naval_discipline` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_naval_discipline.dds` |
| Теневая война | `GFX_goal_generic_major_war` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_major_war.png) |
| Судоверфи | `GFX_goal_generic_construct_naval_dockyard` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_construct_naval_dockyard.png) |
| Радиоразведка | `GFX_goal_generic_radar` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_radar.png) |
| Советский военный ленд-лиз | `GFX_goal_generic_military_deal` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_military_deal.png) |
| Специальные операции | `GFX_goal_generic_special_forces` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_special_forces.png) |
| Милитаризация спорта | `GFX_focus_generic_military_academy` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_military_academy.png) |
| Производство стали | `GFX_focus_generic_steel` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_steel.png) |
| Тактика стального тарана | `GFX_focus_generic_tank_assault` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_tank_assault.dds` |
| Воздушный корпус степи | `GFX_goal_generic_build_airforce` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_build_airforce.png) |
| Степная молния | `GFX_goal_generic_army_motorized` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_army_motorized.png) |
| Школа степной войны | `GFX_goal_generic_army_doctrines` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_army_doctrines.png) |
| Житница свободной степи | `GFX_focus_generic_farmland` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_farmland.dds` |
| Стратегические бомбардировки | `GFX_goal_generic_air_bomber` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_air_bomber.png) |
| Стратегические резервы | `GFX_focus_generic_mass_production` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_mass_production.dds` |
| Подводная флотилия | `GFX_goal_generic_navy_submarine` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_navy_submarine.png) |
| Система складов снабжения | `GFX_focus_generic_reinforcing_the_supply_network` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_reinforcing_the_supply_network.dds` |
| Поддержка турецких левых | `GFX_focus_generic_anti_fascist_diplomacy` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_anti_fascist_diplomacy.png) |
| Синдикалистский рай | `GFX_focus_generic_industry_2` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_industry_2.png) |
| Индустриальный план вольных синдикатов | `GFX_focus_generic_workers` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_workers.dds` |
| Техническое образование | `GFX_focus_generic_university_1` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_university_1.dds` |
| Технологическое превосходство | `GFX_goal_generic_scientific_exchange` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_scientific_exchange.png) |
| Текстильные синдикаты | `GFX_focus_generic_mass_production` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_mass_production.dds` |
| Тотальная милитаризация коммун | `GFX_focus_generic_full_social_mobilization` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_full_social_mobilization.dds` |
| Машинно-тракторные станции коммун | `GFX_focus_generic_mechanized` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_mechanized.dds` |
| Триумф Свободного Человечества | `GFX_focus_generic_the_giant_wakes` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_the_giant_wakes.png) |
| Подпольные арсеналы | `GFX_goal_generic_small_arms` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_small_arms.png) |
| Подпольная железная дорога | `GFX_focus_generic_railroad` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_railroad.dds` |
| Подпольное государство | `GFX_goal_generic_national_unity` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_national_unity.png) |
| Непоколебимый революционный порядок | `GFX_focus_generic_national_security` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_national_security.dds` |
| Военные поставки Vickers | `GFX_goal_generic_military_deal` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_military_deal.png) |
| Борьба с агентурой ЧК и ОГПУ | `GFX_focus_generic_infiltration` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_infiltration.dds` |
| Тайники с оружием | `GFX_goal_generic_small_arms` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/goal_generic_small_arms.png) |
| Военные инструкторы Вермахта | `GFX_focus_generic_military_mission` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_military_mission.png) |
| Освобождение женщин | `GFX_focus_generic_universal_suffrage` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_universal_suffrage.dds` |
| Женское лидерство | `GFX_focus_generic_universal_suffrage` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_universal_suffrage.dds` |
| Рабочие факультеты | `GFX_focus_generic_university_2` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_university_2.dds` |
| Демократия на рабочем месте | `GFX_focus_generic_self_management` | [каталог](https://raw.githubusercontent.com/kr4/icons/master/images/goals/focus_generic_self_management.png) |
| Сеть контрразведки Лева Задова | `GFX_focus_generic_secret_service_agency` | базовая игра (новее каталога): `gfx/interface/goals/focus_generic_secret_service_agency.dds` |

## Иконки национальных духов (118)

| Дух | Картинка | Источник |
|---|---|---|
| Оплот Свободных Наций | `GFX_idea_generic_flexible_foreign_policy` | ванильная базовая игра: `gfx/interface/ideas/generic_flexible_foreign_policy.dds` |
| Наследие Черной Гвардии | `GFX_idea_GLP_black_guard_legacy` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_black_guard_legacy.dds` |
| Кредиты Британского Сити | `GFX_idea_generic_foreign_capital` | ванильная базовая игра: `gfx/interface/ideas/generic_foreign_capital.dds` |
| Евразийский Красно-Черный Авангард | `GFX_idea_generic_communist_army` | ванильная базовая игра: `gfx/interface/ideas/generic_communist_army.dds` |
| Вольные Синдикаты и Советы | `GFX_idea_GLP_free_syndicates_and_soviets` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_free_syndicates_and_soviets.dds` |
| Кооперация с Державами Оси | `GFX_idea_generic_deal_with_the_devil` | ванильная базовая игра: `gfx/interface/ideas/generic_deal_with_the_devil.dds` |
| Враждебное окружение | `GFX_idea_GLP_hostile_encirclement` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_hostile_encirclement.dds` |
| Агентурные сети | `GFX_idea_generic_spy_intel` | ванильная базовая игра: `gfx/interface/ideas/generic_spy_intel.dds` |
| Владыки небес | `GFX_idea_generic_air_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_air_bonus.dds` |
| Воздушная разведка | `GFX_idea_generic_air_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_air_bonus.dds` |
| Щит от провокаторов | `GFX_idea_generic_spy_intel` | ванильная базовая игра: `gfx/interface/ideas/generic_spy_intel.dds` |
| Истребители Бронетехники | `GFX_idea_generic_artillery_regiments` | ванильная базовая игра: `gfx/interface/ideas/generic_artillery_regiments.dds` |
| Производство Бронепоездов | `GFX_idea_GLP_logistics` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_logistics.dds` |
| Автаркический рай | `GFX_idea_GLP_industry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_industry.dds` |
| Автаркия | `GFX_idea_GLP_industry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_industry.dds` |
| Автономная индустрия | `GFX_idea_GLP_industry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_industry.dds` |
| В тылу врага | `GFX_idea_generic_spy_coup` | ванильная базовая игра: `gfx/interface/ideas/generic_spy_coup.dds` |
| Черная Лавина | `GFX_idea_GLP_cavalry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_cavalry.dds` |
| Черный Полумесяц Степей | `GFX_idea_GLP_society` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_society.dds` |
| Сеть Чёрного Креста | `GFX_idea_GLP_health` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_health.dds` |
| Черный Интернационал | `GFX_idea_generic_volunteer_expedition_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_volunteer_expedition_bonus.dds` |
| Господство на Чёрном море | `GFX_idea_GLP_navy` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_navy.dds` |
| Черный Террор | `GFX_idea_generic_purge` | ванильная базовая игра: `gfx/interface/ideas/generic_purge.dds` |
| Безопасность границ | `GFX_idea_generic_wall_line` | ванильная базовая игра: `gfx/interface/ideas/generic_wall_line.dds` |
| Хлеб для фронта | `GFX_idea_GLP_agriculture` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_agriculture.dds` |
| Житница Европы | `GFX_idea_generic_agrarian_society` | ванильная базовая игра: `gfx/interface/ideas/generic_agrarian_society.dds` |
| Кинопропаганда | `GFX_idea_generic_political_support` | ванильная базовая игра: `gfx/interface/ideas/generic_political_support.dds` |
| Шифрованная связь | `GFX_idea_generic_electronics_concern_1` | ванильная базовая игра: `gfx/interface/ideas/generic_electronics_concern_1.dds` |
| Коллективное земледелие | `GFX_idea_generic_agrarian_reform` | ванильная базовая игра: `gfx/interface/ideas/generic_agrarian_reform.dds` |
| Общевойсковой бой | `GFX_idea_generic_armor` | ванильная базовая игра: `gfx/interface/ideas/generic_armor.dds` |
| Рейды коммандос | `GFX_idea_GLP_tachanka` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_tachanka.dds` |
| Укрепление Коммун | `GFX_idea_generic_local_self_management` | ванильная базовая игра: `gfx/interface/ideas/generic_local_self_management.dds` |
| Континентальный поход | `GFX_idea_generic_war_preparation` | ванильная базовая игра: `gfx/interface/ideas/generic_war_preparation.dds` |
| Казачьи дивизии | `GFX_idea_GLP_cavalry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_cavalry.dds` |
| Казачья слава | `GFX_idea_GLP_cavalry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_cavalry.dds` |
| Казачье наследие | `GFX_idea_GLP_cavalry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_cavalry.dds` |
| Казачье наследие | `GFX_idea_GLP_cavalry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_cavalry.dds` |
| Казачьи офицеры | `GFX_idea_generic_army_war_college` | ванильная базовая игра: `gfx/interface/ideas/generic_army_war_college.dds` |
| Казачьи традиции | `GFX_idea_GLP_society` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_society.dds` |
| Контршпионаж | `GFX_idea_GLP_kontrrazvedka_surveillance` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_kontrrazvedka_surveillance.dds` |
| Криптоанализ | `GFX_idea_generic_electronics_concern_1` | ванильная базовая игра: `gfx/interface/ideas/generic_electronics_concern_1.dds` |
| Культурное просвещение | `GFX_idea_GLP_society` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_society.dds` |
| Децентрализованные мастерские | `GFX_idea_GLP_industry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_industry.dds` |
| Оборона в глубину | `GFX_idea_generic_fortify_the_borders` | ванильная базовая игра: `gfx/interface/ideas/generic_fortify_the_borders.dds` |
| Дезинформация | `GFX_idea_generic_spy_political` | ванильная базовая игра: `gfx/interface/ideas/generic_spy_political.dds` |
| Энергия ДнепроГЭС | `GFX_idea_generic_production_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_production_bonus.dds` |
| Двойные агенты | `GFX_idea_generic_spy_coup` | ванильная базовая игра: `gfx/interface/ideas/generic_spy_coup.dds` |
| Экономическая независимость | `GFX_idea_generic_production_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_production_bonus.dds` |
| Экономическое чудо | `GFX_idea_generic_production_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_production_bonus.dds` |
| Элитная гвардия | `GFX_idea_GLP_black_guard_legacy` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_black_guard_legacy.dds` |
| Фабричные комитеты | `GFX_idea_GLP_industry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_industry.dds` |
| Федерация Вольных Советов | `GFX_idea_generic_local_self_management` | ванильная базовая игра: `gfx/interface/ideas/generic_local_self_management.dds` |
| Женские боевые части | `GFX_idea_GLP_military` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_military.dds` |
| Полевые госпитали | `GFX_idea_GLP_health` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_health.dds` |
| Переработка продовольствия | `GFX_idea_GLP_agriculture` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_agriculture.dds` |
| Вольному воля | `GFX_idea_GLP_free_syndicates_and_soviets` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_free_syndicates_and_soviets.dds` |
| Фронтовая разведка | `GFX_idea_GLP_intelligence` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_intelligence.dds` |
| Полная занятость | `GFX_idea_GLP_industry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_industry.dds` |
| Гендерное равенство | `GFX_idea_GLP_society` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_society.dds` |
| Глобальная сеть | `GFX_idea_generic_intel_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_intel_bonus.dds` |
| Слава моря | `GFX_idea_GLP_navy` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_navy.dds` |
| Коневодство | `GFX_idea_GLP_cavalry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_cavalry.dds` |
| Санитарные поезда | `GFX_idea_GLP_logistics` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_logistics.dds` |
| Непробиваемая разведка | `GFX_idea_GLP_intelligence` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_intelligence.dds` |
| Промышленная сверхдержава | `GFX_idea_GLP_industry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_industry.dds` |
| Народная Повстанческая Армия | `GFX_idea_GLP_insurgent_army` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_insurgent_army.dds` |
| Внутренняя безопасность | `GFX_idea_generic_secret_police` | ванильная базовая игра: `gfx/interface/ideas/generic_secret_police.dds` |
| Интернациональные бригады | `GFX_idea_generic_volunteer_expedition_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_volunteer_expedition_bonus.dds` |
| Непобедимое Повстанчество | `GFX_idea_GLP_insurgent_army` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_insurgent_army.dds` |
| Бдительность Контрразведки | `GFX_idea_GLP_kontrrazvedka_surveillance` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_kontrrazvedka_surveillance.dds` |
| Земля народу | `GFX_idea_generic_agrarian_reform` | ванильная базовая игра: `gfx/interface/ideas/generic_agrarian_reform.dds` |
| Легендарные Махновские Тачанки | `GFX_idea_GLP_tachanka` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_tachanka.dds` |
| Народные сходы правосудия | `GFX_idea_generic_constitutional_guarantees` | ванильная базовая игра: `gfx/interface/ideas/generic_constitutional_guarantees.dds` |
| Мастерство логистики | `GFX_idea_GLP_logistics` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_logistics.dds` |
| Миф о Махно | `GFX_idea_GLP_black_guard_legacy` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_black_guard_legacy.dds` |
| Массированный штурм | `GFX_idea_generic_infantry_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_infantry_bonus.dds` |
| Механизированное хозяйство | `GFX_idea_GLP_agriculture` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_agriculture.dds` |
| Рейдеры торговых путей | `GFX_idea_generic_sea_focused_navy` | ванильная базовая игра: `gfx/interface/ideas/generic_sea_focused_navy.dds` |
| Черная Военная Хунта | `GFX_idea_generic_oppression` | ванильная базовая игра: `gfx/interface/ideas/generic_oppression.dds` |
| Народная стража | `GFX_idea_GLP_military` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_military.dds` |
| Моторный транспорт | `GFX_idea_generic_motorized_equipment_manufacturer_1` | ванильная базовая игра: `gfx/interface/ideas/generic_motorized_equipment_manufacturer_1.dds` |
| Новая культура | `GFX_idea_GLP_society` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_society.dds` |
| Партизанские ячейки | `GFX_idea_GLP_military` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_military.dds` |
| Партизанская Доктрина | `GFX_idea_GLP_tachanka` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_tachanka.dds` |
| Рост населения | `GFX_idea_generic_manpower_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_manpower_bonus.dds` |
| Бонусы за производительность | `GFX_idea_generic_production_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_production_bonus.dds` |
| Железнодорожная Мобильность | `GFX_idea_generic_build_infrastructure` | ванильная базовая игра: `gfx/interface/ideas/generic_build_infrastructure.dds` |
| Координация сопротивления | `GFX_idea_GLP_intelligence` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_intelligence.dds` |
| Координация РевВоенСовета | `GFX_idea_GLP_logistics` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_logistics.dds` |
| Партизанское управление РевВоенСовета | `GFX_idea_GLP_tachanka` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_tachanka.dds` |
| Всеобщая боеготовность | `GFX_idea_generic_war_preparation` | ванильная базовая игра: `gfx/interface/ideas/generic_war_preparation.dds` |
| Земская медицина | `GFX_idea_GLP_health` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_health.dds` |
| Санитарные батальоны | `GFX_idea_GLP_health` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_health.dds` |
| Теневая война | `GFX_idea_generic_spy_intel` | ванильная базовая игра: `gfx/interface/ideas/generic_spy_intel.dds` |
| Специальные операции | `GFX_idea_GLP_military` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_military.dds` |
| Милитаризация спорта | `GFX_idea_generic_manpower_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_manpower_bonus.dds` |
| Стальной Таран Бронепоездов | `GFX_idea_generic_armor` | ванильная базовая игра: `gfx/interface/ideas/generic_armor.dds` |
| Степная Молния | `GFX_idea_GLP_cavalry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_cavalry.dds` |
| Степная война | `GFX_idea_GLP_tachanka` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_tachanka.dds` |
| Житница свободной степи | `GFX_idea_generic_agrarian_society` | ванильная базовая игра: `gfx/interface/ideas/generic_agrarian_society.dds` |
| Стратегические резервы | `GFX_idea_generic_reserve_divisions` | ванильная базовая игра: `gfx/interface/ideas/generic_reserve_divisions.dds` |
| Склады снабжения | `GFX_idea_GLP_logistics` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_logistics.dds` |
| Синдикалистский рай | `GFX_idea_GLP_industry` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_industry.dds` |
| Технологическое превосходство | `GFX_idea_generic_research_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_research_bonus.dds` |
| Текстильные синдикаты | `GFX_idea_generic_production_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_production_bonus.dds` |
| Тотальная Милитаризация | `GFX_idea_generic_manpower_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_manpower_bonus.dds` |
| Триумф Свободы | `GFX_idea_generic_victors_of_ww1` | ванильная базовая игра: `gfx/interface/ideas/generic_victors_of_ww1.dds` |
| Сеть Тайных Арсеналов | `GFX_idea_GLP_military` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_military.dds` |
| Подпольная железная дорога | `GFX_idea_GLP_intelligence` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_intelligence.dds` |
| Подпольное государство | `GFX_idea_generic_secret_police` | ванильная базовая игра: `gfx/interface/ideas/generic_secret_police.dds` |
| Полки европейских доббровольцев | `GFX_idea_generic_volunteer_expedition_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_volunteer_expedition_bonus.dds` |
| Освобождение женщин | `GFX_idea_GLP_society` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_society.dds` |
| Рабочие факультеты | `GFX_idea_generic_research_bonus` | ванильная базовая игра: `gfx/interface/ideas/generic_research_bonus.dds` |
| Демократия на производстве | `GFX_idea_generic_local_self_management` | ванильная базовая игра: `gfx/interface/ideas/generic_local_self_management.dds` |
| Пламя Мировой Анархии | `GFX_idea_GLP_society` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_society.dds` |
| Агентурная сеть Задова | `GFX_idea_GLP_intelligence` | собственная иконка мода: `gfx/interface/ideas/idea_GLP_intelligence.dds` |
| Прусская Дисциплина и Выучка | `GFX_idea_generic_army_war_college` | ванильная базовая игра: `gfx/interface/ideas/generic_army_war_college.dds` |
| Советская Промышленная Помощь | `GFX_idea_generic_foreign_capital` | ванильная базовая игра: `gfx/interface/ideas/generic_foreign_capital.dds` |
