import asyncio
from decimal import Decimal

import httpx


async def get_vt_composition(debug: bool = False) -> dict[str, Decimal]:
    """Fetch the US/Ex-US composition of VT from the Vanguard API.

    VT seeks to track the performance of the FTSE Global All Cap Index, which covers
    both well-established and still-developing markets.

    https://investor.vanguard.com/investment-products/etfs/profile/vt

    {"VTI": Decimal("63.7"), "VXUS": Decimal("36.3")}
    """
    async with httpx.AsyncClient(base_url="https://investor.vanguard.com") as client:
        response = await client.get("/vmf/api/VT/characteristic")
        response.raise_for_status()
        response_json = response.json()
        foreign_holding = Decimal(
            response_json["equityCharacteristic"]["fund"]["foreignHolding"]
        )
        domestic_holding = Decimal("100") - foreign_holding
        return {
            "VTI": domestic_holding,
            "VXUS": foreign_holding,
        }


async def get_bndw_composition(debug: bool = False) -> dict[str, Decimal]:
    """Fetch the US/Ex-US compostition of BNDW from the Vanguard API.

    BNDW seeks to track the performance of the Bloomberg Global Aggregate Float
    Adjusted Composite Index.

    https://investor.vanguard.com/investment-products/etfs/profile/bndw

    {"BND": Decimal("50.1"), "BNDX": Decimal("49.9")}
    """
    async with httpx.AsyncClient(base_url="https://investor.vanguard.com") as client:
        response = await client.get("/vmf/api/BNDW/allocation")
        response.raise_for_status()
        response_json = response.json()
        return {
            item["ticker"].strip(): Decimal(item["percent"])
            for item in response_json["underlyingFund"]["fundAllocated"]
            if Decimal(item["percent"]) > 0
        }


async def two_fund(bond: float) -> dict[str, Decimal]:
    total_bonds_percent = Decimal(str(bond))
    total_stocks_percent = Decimal("100") - total_bonds_percent
    return {
        "VT": total_stocks_percent,
        "BNDW": total_bonds_percent,
    }


async def three_fund(bond: float) -> dict[str, Decimal]:
    """Fetch the foreign and domestic holdings composition based on the bonds percentage.

    Args:
        bond (float, optional): The percentage of bonds. Defaults to 10.0.

    """
    # Get the foreign percentage of VT, then calculate the domestic percentage.
    total_bonds_percent = Decimal(str(bond))
    total_stocks_percent = Decimal("100") - total_bonds_percent

    # Get the US/Ex-US percentage from VT
    vt_composition = await get_vt_composition()
    foreign_stock_holding_percentage = vt_composition["VXUS"]

    # Calculate the percentage of total investment
    foreign_equities_percent = (
        total_stocks_percent * foreign_stock_holding_percentage / Decimal("100")
    )

    # Deducting foreign from stocks to get domestic
    domestic_equities_percent = total_stocks_percent - foreign_equities_percent

    return {
        "VTI": domestic_equities_percent,
        "VXUS": foreign_equities_percent,
        "BNDW": total_bonds_percent,
    }


async def four_fund(bond: float) -> dict[str, Decimal]:
    total_bonds_percent = Decimal(str(bond))
    total_stocks_percent = Decimal("100") - total_bonds_percent

    vt_composition, bndw_composition = await asyncio.gather(
        get_vt_composition(), get_bndw_composition()
    )

    vti_percent = vt_composition["VTI"] / Decimal("100") * total_stocks_percent
    vxus_percent = vt_composition["VXUS"] / Decimal("100") * total_stocks_percent

    bnd_percent = bndw_composition["BND"] / Decimal("100") * total_bonds_percent
    bndx_percent = bndw_composition["BNDX"] / Decimal("100") * total_bonds_percent

    return {
        "VTI": vti_percent,
        "VXUS": vxus_percent,
        "BND": bnd_percent,
        "BNDX": bndx_percent,
    }
