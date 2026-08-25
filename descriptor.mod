version="1.3.2"
tags={
	"Alternative History"
	"National Focuses"
	"Gameplay"
	"Military"
}
name="Гуляйполе: Вольная Территория — Анархия есть мать порядка"
supported_version="1.19.*"
picture="thumbnail.png"

# ============================================================================
#  Полное перекрытие каталога загрузочныхъ экрановъ: движокъ не подмешиваетъ
#  ни ванильные load_1..load_16, ни экраны DLC (load_tfv, load_dod, load_tiger,
#  load_mtg, load_lar, load_nsb, load_bba, load_aat и т. д.). Въ ротации
#  остаются только наши шесть экрановъ (load_1..load_16 ссылаются на нихъ же).
#  Фонъ главнаго меню (frontendmainviewbg.dds) — это спрайтъ, и онъ НЕ
#  затрагивается replace_path (подтверждено вики по моддингу HOI4).
# ============================================================================
replace_path="gfx/loadingscreens"
replace_path="music"
