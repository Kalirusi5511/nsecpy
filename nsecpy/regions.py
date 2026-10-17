from dataclasses import dataclass, field
from typing import AsyncGenerator, Generator, List, Literal, Optional, Union

from .listing import Game, query_listing
from .pricing import PriceQuery, query_price, query_prices
from .status import Status, query_status


@dataclass
class Region:
    culture_code: str
    familiar_name: str  # Tippfehler behoben (war: familar_name)
    supports_listing: bool = True
    supports_pricing: bool = True
    netinfo_TZ: Optional[str] = None

    async def query_status(self) -> Status:
        return await query_status(self)

    async def query_listing(self, type: Literal["sales", "new", "ranking"]) -> AsyncGenerator[Game, None]:
        async for game in query_listing(self, type):
            yield game

    async def query_price(self, game: Union[int, "Game"]) -> PriceQuery:
        return await query_price(self, game)

    async def query_prices(self, games: List[Union[int, "Game"]]) -> AsyncGenerator[PriceQuery, None]:
        async for game in query_prices(self, games):
            yield game


# Regions from https://www.nintendo.com/regionselector/
# Korrigiert und mit realistischen API-Limitierungen versehen
regions_list = [
    # -------- Americas --------
    Region('en_US', 'USA', netinfo_TZ="America/Los_Angeles"),
    Region('en_CA', 'Canada (English)', netinfo_TZ="America/Toronto"),
    Region('fr_CA', 'Canada (French)', netinfo_TZ="America/Toronto"),
    Region('es_MX', 'México', netinfo_TZ="America/Mexico_City"),
    Region('pt_BR', 'Brasil', netinfo_TZ="America/Sao_Paulo"),
    Region('es_CO', 'Colombia', netinfo_TZ="America/Bogota", supports_listing=False),
    Region('es_AR', 'Argentina', netinfo_TZ="America/Argentina/Buenos_Aires", supports_listing=False),
    Region('es_CL', 'Chile', netinfo_TZ="America/Santiago", supports_listing=False),
    Region('es_PE', 'Perú', netinfo_TZ="America/Lima", supports_listing=False),
    # -------- Asia Pacific --------
    Region('ja_JP', 'Japan', netinfo_TZ="Asia/Tokyo"),
    Region('ko_KR', 'Korea', netinfo_TZ="Asia/Seoul"),
    Region(
        'zh_CN', 'China Mainland (Tencent)', netinfo_TZ="Asia/Shanghai", supports_listing=False, supports_pricing=False
    ),
    Region('zh_TW', 'Taiwan', netinfo_TZ="Asia/Taipei", supports_listing=False, supports_pricing=False),
    Region('zh_HK', 'Hong Kong', netinfo_TZ="Asia/Hong_Kong"),
    Region('en_AU', 'Australia', netinfo_TZ="Australia/Sydney"),
    Region('en_NZ', 'New Zealand', netinfo_TZ="Pacific/Auckland"),
    # -------- Europe, Middle East & Africa --------
    Region('de_AT', 'Austria', netinfo_TZ="Europe/Vienna"),
    Region('nl_BE', 'België (Dutch)', netinfo_TZ="Europe/Brussels"),
    Region('fr_BE', 'Belgique (French)', netinfo_TZ="Europe/Brussels"),
    Region('en_CZ', 'Czech Republic', netinfo_TZ="Europe/Prague"),
    Region('en_DK', 'Denmark', netinfo_TZ="Europe/Copenhagen"),
    Region('de_DE', 'Deutschland', netinfo_TZ="Europe/Berlin"),
    Region('es_ES', 'España', netinfo_TZ="Europe/Madrid"),
    Region('en_FI', 'Finland', netinfo_TZ="Europe/Helsinki"),
    Region('fr_FR', 'France', netinfo_TZ="Europe/Paris"),
    Region('en_GR', 'Greece', netinfo_TZ="Europe/Athens"),
    Region('en_HU', 'Hungary', netinfo_TZ="Europe/Budapest"),
    Region('he_IL', 'Israel', netinfo_TZ="Asia/Jerusalem", supports_listing=False),
    Region('it_IT', 'Italia', netinfo_TZ="Europe/Rome"),
    Region('nl_NL', 'Nederland', netinfo_TZ="Europe/Amsterdam"),
    Region('pt_PT', 'Portugal', netinfo_TZ="Europe/Lisbon"),
    Region('ru_RU', 'Russia', netinfo_TZ="Europe/Moscow", supports_listing=False),
    Region('en_ZA', 'South Africa', netinfo_TZ="Africa/Johannesburg"),
    Region('en_SE', 'Sweden', netinfo_TZ="Europe/Stockholm"),
    Region('de_CH', 'Schweiz (German)', netinfo_TZ="Europe/Zurich"),
    Region('fr_CH', 'Suisse (French)', netinfo_TZ="Europe/Zurich"),
    Region('it_CH', 'Svizzera (Italian)', netinfo_TZ="Europe/Zurich"),
    Region('en_GB', 'UK & Ireland', netinfo_TZ="Europe/London"),
]

# Comprehend list into dict, indexed by culture code
regions = {r.culture_code: r for r in regions_list}
