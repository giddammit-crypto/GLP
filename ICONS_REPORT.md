# Отчёт по иконкам — Гуляйполе

Подбор выполнен через каталог **HOI4 Icon Search**: <https://wyandotte.github.io/hoi4-icon-search/> (витрина данных репозитория `kr4/icons`: 1960 иконок фокусов + 1294 духа/советника).

**Метод проверки.** Иконки фокусов сверены с ванильным `interface/goals.gfx` (дампы **1.7.1 Hydra** и **1.14.10**) и не требуют DLC. Все национальные духи используют только 15 тематических категорий собственного GLP-пака из `interface/GLP_ideas.gfx`; точное соответствие контролируется файлом `tools/idea_pictures.tsv` и автоматическим аудитом. Иконки Kaiserreich и DLC-контент не используются.

**Сводка**

| Категория | Всего | Уникальных иконок | Макс. повторов использования |
|---|---|---|---|
| Фокусы | 190 | **118** | 5 (`mass_production` — производственные ветки) |
| Национальные духи | 118 | **15 собственных GLP** | 17 (`GLP_military`) |

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

Все духи используют **только собственный GLP-пак**. Категория выбрана по смыслу эффекта: армия, промышленность, разведка, логистика, медицина, сельское хозяйство, флот, кавалерия, общество и т. д.

Все 15 категорий пака — **сгенерированные ИИ-эмблемы на прозрачном фоне**
(60×68 несжатый BGRA DDS, реальная прозрачность `min alpha = 0`): мотив
вырезается по маске прозрачности и ставится на прозрачную канву без
подложки, с узкой бронзовой кромкой (`#c8b48f`) для читаемости на тёмном
слоте идей. Холодная сепиево-бронзовая палитра, тонкая тёмная обводка.
Мастера: `tools/_icons_src/_src_<category>.png`; сборка — `tools/build_icons.sh`.

### Использование категорий

| Категория пака | Назначений | Файл |
|---|---:|---|
| `GFX_idea_GLP_military` | 17 | `gfx/interface/ideas/idea_GLP_military.dds` |
| `GFX_idea_GLP_industry` | 16 | `gfx/interface/ideas/idea_GLP_industry.dds` |
| `GFX_idea_GLP_intelligence` | 15 | `gfx/interface/ideas/idea_GLP_intelligence.dds` |
| `GFX_idea_GLP_cavalry` | 10 | `gfx/interface/ideas/idea_GLP_cavalry.dds` |
| `GFX_idea_GLP_society` | 9 | `gfx/interface/ideas/idea_GLP_society.dds` |
| `GFX_idea_GLP_logistics` | 8 | `gfx/interface/ideas/idea_GLP_logistics.dds` |
| `GFX_idea_GLP_agriculture` | 7 | `gfx/interface/ideas/idea_GLP_agriculture.dds` |
| `GFX_idea_GLP_free_syndicates_and_soviets` | 7 | `gfx/interface/ideas/idea_GLP_free_syndicates_and_soviets.dds` |
| `GFX_idea_GLP_hostile_encirclement` | 5 | `gfx/interface/ideas/idea_GLP_hostile_encirclement.dds` |
| `GFX_idea_GLP_kontrrazvedka_surveillance` | 5 | `gfx/interface/ideas/idea_GLP_kontrrazvedka_surveillance.dds` |
| `GFX_idea_GLP_tachanka` | 5 | `gfx/interface/ideas/idea_GLP_tachanka.dds` |
| `GFX_idea_GLP_black_guard_legacy` | 4 | `gfx/interface/ideas/idea_GLP_black_guard_legacy.dds` |
| `GFX_idea_GLP_health` | 4 | `gfx/interface/ideas/idea_GLP_health.dds` |
| `GFX_idea_GLP_insurgent_army` | 3 | `gfx/interface/ideas/idea_GLP_insurgent_army.dds` |
| `GFX_idea_GLP_navy` | 3 | `gfx/interface/ideas/idea_GLP_navy.dds` |

### Полное соответствие

| Дух | ID | Иконка пака |
|---|---|---|
| Автаркический рай | `GLP_idea_autarkic_paradise` | `GFX_idea_GLP_industry` |
| Автаркия | `GLP_idea_autarky` | `GFX_idea_GLP_industry` |
| Автономная индустрия | `GLP_idea_autonomous_industrial_bastion` | `GFX_idea_GLP_industry` |
| Агентурная сеть Задова | `GLP_idea_zadov_network` | `GFX_idea_GLP_intelligence` |
| Агентурные сети | `GLP_idea_agent_networks` | `GFX_idea_GLP_intelligence` |
| Бдительность Контрразведки | `GLP_idea_kontrrazvedka_surveillance` | `GFX_idea_GLP_kontrrazvedka_surveillance` |
| Безопасность границ | `GLP_idea_border_security` | `GFX_idea_GLP_hostile_encirclement` |
| Бонусы за производительность | `GLP_idea_productivity_bonuses` | `GFX_idea_GLP_industry` |
| В тылу врага | `GLP_idea_behind_lines` | `GFX_idea_GLP_intelligence` |
| Владыки небес | `GLP_idea_air_mastery` | `GFX_idea_GLP_military` |
| Внутренняя безопасность | `GLP_idea_internal_security` | `GFX_idea_GLP_kontrrazvedka_surveillance` |
| Воздушная разведка | `GLP_idea_air_recon` | `GFX_idea_GLP_intelligence` |
| Вольному воля | `GLP_idea_free_will` | `GFX_idea_GLP_free_syndicates_and_soviets` |
| Вольные Синдикаты и Советы | `GLP_free_syndicates_and_soviets` | `GFX_idea_GLP_free_syndicates_and_soviets` |
| Враждебное окружение | `GLP_hostile_encirclement` | `GFX_idea_GLP_hostile_encirclement` |
| Всеобщая боеготовность | `GLP_idea_revvoensovet_total_preparedness` | `GFX_idea_GLP_military` |
| Гендерное равенство | `GLP_idea_gender_equality` | `GFX_idea_GLP_society` |
| Глобальная сеть | `GLP_idea_global_network` | `GFX_idea_GLP_intelligence` |
| Господство на Чёрном море | `GLP_idea_black_sea_dominance` | `GFX_idea_GLP_navy` |
| Двойные агенты | `GLP_idea_double_agents` | `GFX_idea_GLP_intelligence` |
| Дезинформация | `GLP_idea_disinformation` | `GFX_idea_GLP_intelligence` |
| Демократия на производстве | `GLP_idea_workplace_democracy` | `GFX_idea_GLP_free_syndicates_and_soviets` |
| Децентрализованные мастерские | `GLP_idea_decentralized_workshops` | `GFX_idea_GLP_industry` |
| Евразийский Красно-Черный Авангард | `GLP_eurasian_red_black_vanguard` | `GFX_idea_GLP_black_guard_legacy` |
| Железнодорожная Мобильность | `GLP_idea_rapid_rail_deployment` | `GFX_idea_GLP_logistics` |
| Женские боевые части | `GLP_idea_female_combat` | `GFX_idea_GLP_military` |
| Житница Европы | `GLP_idea_breadbasket` | `GFX_idea_GLP_agriculture` |
| Житница свободной степи | `GLP_idea_steppes_breadbasket` | `GFX_idea_GLP_agriculture` |
| Земля народу | `GLP_idea_land_to_tillers` | `GFX_idea_GLP_agriculture` |
| Земская медицина | `GLP_idea_rural_healthcare` | `GFX_idea_GLP_health` |
| Интернациональные бригады | `GLP_idea_international_brigades` | `GFX_idea_GLP_military` |
| Истребители Бронетехники | `GLP_idea_anti_tank_cavalry` | `GFX_idea_GLP_cavalry` |
| Казачье наследие | `GLP_idea_cossack_heritage` | `GFX_idea_GLP_cavalry` |
| Казачье наследие | `GLP_idea_cossack_legacy` | `GFX_idea_GLP_cavalry` |
| Казачьи дивизии | `GLP_idea_cossack_divisions` | `GFX_idea_GLP_cavalry` |
| Казачьи офицеры | `GLP_idea_cossack_officers` | `GFX_idea_GLP_cavalry` |
| Казачьи традиции | `GLP_idea_cossack_traditions` | `GFX_idea_GLP_cavalry` |
| Казачья слава | `GLP_idea_cossack_glory` | `GFX_idea_GLP_cavalry` |
| Кинопропаганда | `GLP_idea_cinema_propaganda` | `GFX_idea_GLP_society` |
| Коллективное земледелие | `GLP_idea_collective_farming` | `GFX_idea_GLP_agriculture` |
| Коневодство | `GLP_idea_horse_breeding` | `GFX_idea_GLP_cavalry` |
| Континентальный поход | `GLP_idea_continental_crusade` | `GFX_idea_GLP_military` |
| Контршпионаж | `GLP_idea_counter_espionage` | `GFX_idea_GLP_kontrrazvedka_surveillance` |
| Кооперация с Державами Оси | `GLP_german_axis_synergy` | `GFX_idea_GLP_military` |
| Координация РевВоенСовета | `GLP_idea_revvoensovet_coordination` | `GFX_idea_GLP_logistics` |
| Координация сопротивления | `GLP_idea_resistance_coordination` | `GFX_idea_GLP_intelligence` |
| Кредиты Британского Сити | `GLP_british_sterling_credits` | `GFX_idea_GLP_industry` |
| Криптоанализ | `GLP_idea_cryptanalysis` | `GFX_idea_GLP_intelligence` |
| Культурное просвещение | `GLP_idea_cultural_enlightenment` | `GFX_idea_GLP_society` |
| Легендарные Махновские Тачанки | `GLP_idea_legendary_tachankas` | `GFX_idea_GLP_tachanka` |
| Массированный штурм | `GLP_idea_mass_assault` | `GFX_idea_GLP_military` |
| Мастерство логистики | `GLP_idea_logistics_mastery` | `GFX_idea_GLP_logistics` |
| Механизированное хозяйство | `GLP_idea_mechanized_agriculture` | `GFX_idea_GLP_agriculture` |
| Милитаризация спорта | `GLP_idea_sports_militarization` | `GFX_idea_GLP_military` |
| Миф о Махно | `GLP_idea_makhno_myth` | `GFX_idea_GLP_black_guard_legacy` |
| Моторный транспорт | `GLP_idea_motor_transport` | `GFX_idea_GLP_logistics` |
| Народная Повстанческая Армия | `GLP_idea_insurgent_army` | `GFX_idea_GLP_insurgent_army` |
| Народная стража | `GLP_idea_militia_patrols` | `GFX_idea_GLP_military` |
| Народные сходы правосудия | `GLP_idea_libertarian_courts` | `GFX_idea_GLP_free_syndicates_and_soviets` |
| Наследие Черной Гвардии | `GLP_black_guard_legacy` | `GFX_idea_GLP_black_guard_legacy` |
| Непобедимое Повстанчество | `GLP_idea_invincible_insurgency` | `GFX_idea_GLP_insurgent_army` |
| Непробиваемая разведка | `GLP_idea_impregnable_intel` | `GFX_idea_GLP_intelligence` |
| Новая культура | `GLP_idea_new_culture` | `GFX_idea_GLP_society` |
| Оборона в глубину | `GLP_idea_defense_in_depth` | `GFX_idea_GLP_hostile_encirclement` |
| Общевойсковой бой | `GLP_idea_combined_arms` | `GFX_idea_GLP_military` |
| Оплот Свободных Наций | `GLP_anglo_free_bastion` | `GFX_idea_GLP_hostile_encirclement` |
| Освобождение женщин | `GLP_idea_womens_emancipation` | `GFX_idea_GLP_society` |
| Партизанская Доктрина | `GLP_idea_partisan_doctrine` | `GFX_idea_GLP_tachanka` |
| Партизанские ячейки | `GLP_idea_partisan_cells` | `GFX_idea_GLP_insurgent_army` |
| Партизанское управление РевВоенСовета | `GLP_idea_revvoensovet_partisan_command` | `GFX_idea_GLP_tachanka` |
| Переработка продовольствия | `GLP_idea_food_processing` | `GFX_idea_GLP_agriculture` |
| Пламя Мировой Анархии | `GLP_idea_world_anarchy` | `GFX_idea_GLP_society` |
| Подпольная железная дорога | `GLP_idea_underground_railway` | `GFX_idea_GLP_intelligence` |
| Подпольное государство | `GLP_idea_underground_state` | `GFX_idea_GLP_intelligence` |
| Полевые госпитали | `GLP_idea_field_hospitals` | `GFX_idea_GLP_health` |
| Полки европейских доббровольцев | `GLP_idea_white_volunteers` | `GFX_idea_GLP_military` |
| Полная занятость | `GLP_idea_full_employment` | `GFX_idea_GLP_industry` |
| Производство Бронепоездов | `GLP_idea_armored_train_production` | `GFX_idea_GLP_logistics` |
| Промышленная сверхдержава | `GLP_idea_industrial_powerhouse` | `GFX_idea_GLP_industry` |
| Прусская Дисциплина и Выучка | `GLP_prussian_drill_discipline` | `GFX_idea_GLP_military` |
| Рабочие факультеты | `GLP_idea_worker_faculties` | `GFX_idea_GLP_society` |
| Рейдеры торговых путей | `GLP_idea_merchant_raiders` | `GFX_idea_GLP_navy` |
| Рейды коммандос | `GLP_idea_commando_raids` | `GFX_idea_GLP_tachanka` |
| Рост населения | `GLP_idea_population_growth` | `GFX_idea_GLP_society` |
| Санитарные батальоны | `GLP_idea_sanitary_battalions` | `GFX_idea_GLP_health` |
| Санитарные поезда | `GLP_idea_hospital_trains` | `GFX_idea_GLP_logistics` |
| Сеть Тайных Арсеналов | `GLP_idea_underground_armories` | `GFX_idea_GLP_military` |
| Сеть Чёрного Креста | `GLP_idea_black_cross_aid` | `GFX_idea_GLP_health` |
| Синдикалистский рай | `GLP_idea_syndicalist_paradise` | `GFX_idea_GLP_industry` |
| Склады снабжения | `GLP_idea_supply_depots` | `GFX_idea_GLP_logistics` |
| Слава моря | `GLP_idea_glory_of_the_sea` | `GFX_idea_GLP_navy` |
| Советская Промышленная Помощь | `GLP_soviet_industrial_aid` | `GFX_idea_GLP_industry` |
| Специальные операции | `GLP_idea_special_ops` | `GFX_idea_GLP_military` |
| Стальной Таран Бронепоездов | `GLP_idea_steel_ram` | `GFX_idea_GLP_military` |
| Степная война | `GLP_idea_steppe_warfare` | `GFX_idea_GLP_tachanka` |
| Степная Молния | `GLP_idea_steppe_lightning` | `GFX_idea_GLP_cavalry` |
| Стратегические резервы | `GLP_idea_strategic_reserves` | `GFX_idea_GLP_logistics` |
| Текстильные синдикаты | `GLP_idea_textile_syndicates` | `GFX_idea_GLP_industry` |
| Теневая война | `GLP_idea_shadow_war` | `GFX_idea_GLP_intelligence` |
| Технологическое превосходство | `GLP_idea_tech_supremacy` | `GFX_idea_GLP_industry` |
| Тотальная Милитаризация | `GLP_idea_total_militarization` | `GFX_idea_GLP_military` |
| Триумф Свободы | `GLP_idea_triumph_of_liberty` | `GFX_idea_GLP_free_syndicates_and_soviets` |
| Укрепление Коммун | `GLP_idea_communes_empowerment` | `GFX_idea_GLP_free_syndicates_and_soviets` |
| Фабричные комитеты | `GLP_idea_factory_committees` | `GFX_idea_GLP_industry` |
| Федерация Вольных Советов | `GLP_idea_federation_of_free_soviets` | `GFX_idea_GLP_free_syndicates_and_soviets` |
| Фронтовая разведка | `GLP_idea_frontline_recon` | `GFX_idea_GLP_intelligence` |
| Хлеб для фронта | `GLP_idea_bread_for_front` | `GFX_idea_GLP_agriculture` |
| Черная Военная Хунта | `GLP_idea_military_junta` | `GFX_idea_GLP_military` |
| Черная Лавина | `GLP_idea_black_avalanche` | `GFX_idea_GLP_cavalry` |
| Черный Интернационал | `GLP_idea_black_international` | `GFX_idea_GLP_society` |
| Черный Полумесяц Степей | `GLP_idea_black_crescent` | `GFX_idea_GLP_hostile_encirclement` |
| Черный Террор | `GLP_idea_black_terror` | `GFX_idea_GLP_kontrrazvedka_surveillance` |
| Шифрованная связь | `GLP_idea_coded_comms` | `GFX_idea_GLP_intelligence` |
| Щит от провокаторов | `GLP_idea_anti_cheka_vigilance` | `GFX_idea_GLP_kontrrazvedka_surveillance` |
| Экономическая независимость | `GLP_idea_economic_independence` | `GFX_idea_GLP_industry` |
| Экономическое чудо | `GLP_idea_economic_miracle` | `GFX_idea_GLP_industry` |
| Элитная гвардия | `GLP_idea_elite_guard` | `GFX_idea_GLP_black_guard_legacy` |
| Энергия ДнепроГЭС | `GLP_idea_dnieper_hydroelectric` | `GFX_idea_GLP_industry` |
