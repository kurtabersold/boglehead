from decimal import Decimal

import httpx
import pytest
import respx

from boglehead import vanguard


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "foreign_holding, expected",
    [
        ("0", {"VTI": Decimal("100"), "VXUS": Decimal("0")}),
        ("25", {"VTI": Decimal("75"), "VXUS": Decimal("25")}),
        ("36.3", {"VTI": Decimal("63.7"), "VXUS": Decimal("36.3")}),
        ("50", {"VTI": Decimal("50"), "VXUS": Decimal("50")}),
        ("75", {"VTI": Decimal("25"), "VXUS": Decimal("75")}),
        ("100", {"VTI": Decimal("0"), "VXUS": Decimal("100")}),
    ],
)
async def test_get_vt_composition(foreign_holding, expected):
    with respx.mock(
        base_url="https://investor.vanguard.com", assert_all_called=True
    ) as respx_mock:
        vt_route = respx_mock.get("/vmf/api/VT/characteristic")
        vt_route.return_value = httpx.Response(
            200,
            json={
                "equityCharacteristic": {"fund": {"foreignHolding": foreign_holding}}
            },
        )

        vt_composition = await vanguard.get_vt_composition()

        assert vt_composition == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bnd, bndx, expected",
    [
        ("0", "100", {"BNDX": Decimal("100")}),
        ("25", "75", {"BND": Decimal("25"), "BNDX": Decimal("75")}),
        ("50", "50", {"BND": Decimal("50"), "BNDX": Decimal("50")}),
        ("75", "25", {"BND": Decimal("75"), "BNDX": Decimal("25")}),
        ("100", "0", {"BND": Decimal("100")}),
    ],
)
async def test_get_bndw_composition(bnd, bndx, expected):
    with respx.mock(
        base_url="https://investor.vanguard.com", assert_all_called=True
    ) as respx_mock:
        bndw_route = respx_mock.get("/vmf/api/BNDW/allocation")

        bndw_route.return_value = httpx.Response(
            200,
            json={
                "underlyingFund": {
                    "fundAllocated": [
                        {"percent": bnd, "ticker": "BND       "},
                        {"percent": bndx, "ticker": "BNDX      "},
                    ]
                }
            },
        )

        bndw_composition = await vanguard.get_bndw_composition()
        assert bndw_composition == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bonds, expected",
    [
        ("0", {"VT": Decimal("100"), "BNDW": Decimal("0")}),
        ("25", {"VT": Decimal("75"), "BNDW": Decimal("25")}),
        ("50", {"VT": Decimal("50"), "BNDW": Decimal("50")}),
        ("75", {"VT": Decimal("25"), "BNDW": Decimal("75")}),
        ("100", {"VT": Decimal("0"), "BNDW": Decimal("100")}),
    ],
)
async def test_two_fund(bonds, expected):
    two_fund_response = await vanguard.two_fund(bond=bonds)
    assert two_fund_response == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bonds, expected",
    [
        ("0", {"VTI": Decimal("50"), "VXUS": Decimal("50"), "BNDW": Decimal("0")}),
        (
            "25",
            {"VTI": Decimal("37.5"), "VXUS": Decimal("37.5"), "BNDW": Decimal("25")},
        ),
        ("50", {"VTI": Decimal("25"), "VXUS": Decimal("25"), "BNDW": Decimal("50")}),
        (
            "75",
            {"VTI": Decimal("12.5"), "VXUS": Decimal("12.5"), "BNDW": Decimal("75")},
        ),
        ("100", {"VTI": Decimal("0"), "VXUS": Decimal("0"), "BNDW": Decimal("100")}),
    ],
)
async def test_three_fund(bonds, expected, mocked_vanguard):
    three_fund_response = await vanguard.three_fund(bond=bonds)
    assert three_fund_response == expected


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bonds, expected",
    [
        (
            "0",
            {
                "VTI": Decimal("50"),
                "VXUS": Decimal("50"),
                "BND": Decimal("0"),
                "BNDX": Decimal("0"),
            },
        ),
        (
            "25",
            {
                "VTI": Decimal("37.5"),
                "VXUS": Decimal("37.5"),
                "BND": Decimal("12.5"),
                "BNDX": Decimal("12.5"),
            },
        ),
        (
            "50",
            {
                "VTI": Decimal("25"),
                "VXUS": Decimal("25"),
                "BND": Decimal("25"),
                "BNDX": Decimal("25"),
            },
        ),
        (
            "75",
            {
                "VTI": Decimal("12.5"),
                "VXUS": Decimal("12.5"),
                "BND": Decimal("37.5"),
                "BNDX": Decimal("37.5"),
            },
        ),
        (
            "100",
            {
                "VTI": Decimal("0"),
                "VXUS": Decimal("0"),
                "BND": Decimal("50"),
                "BNDX": Decimal("50"),
            },
        ),
    ],
)
async def test_four_fund(bonds, expected, mocked_vanguard):
    four_fund_response = await vanguard.four_fund(bond=bonds)
    assert four_fund_response == expected
