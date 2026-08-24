version="1.2.0"
tags={
	"Alternative History"
	"National Focuses"
	"Gameplay"
	"Military"
}
name="Гуляйполе: Вольная Территорія — Анархія есть мать порядка"
supported_version="1.19.*"

# ============================================================================
#  Полное перекрытіе каталога загрузочныхъ экрановъ: движокъ не подмѣшиваетъ
#  ни ванильные load_1..load_16, ни экраны DLC (load_tfv, load_dod, load_tiger,
#  load_mtg, load_lar, load_nsb, load_bba, load_aat и т. д.). Въ ротаціи
#  остаются только наши шесть экрановъ (load_1..load_16 ссылаются на нихъ же).
#  Фонъ главнаго меню (frontendmainviewbg.dds) — это спрайтъ, и онъ НЕ
#  затрагивается replace_path (подтверждено вики по моддингу HOI4).
# ============================================================================
replace_path="gfx/loadingscreens"
