import httpx
import pytest
import respx


@pytest.fixture
def mocked_vanguard():
    with respx.mock(
        base_url="https://investor.vanguard.com", assert_all_called=False
    ) as respx_mock:
        vt_route = respx_mock.get("/vmf/api/VT/characteristic")
        vt_route.return_value = httpx.Response(
            200, json={"equityCharacteristic": {"fund": {"foreignHolding": "50"}}}
        )
        bndw_route = respx_mock.get("/vmf/api/BNDW/allocation")
        bndw_route.return_value = httpx.Response(
            200,
            json={
                "underlyingFund": {
                    "fundAllocated": [
                        {"percent": "50", "ticker": "BND       "},
                        {"percent": "50", "ticker": "BNDX      "},
                    ]
                }
            },
        )
        yield respx_mock


@pytest.fixture
def mocked_vanguard_exception():
    with respx.mock(
        base_url="https://investor.vanguard.com", assert_all_called=False
    ) as respx_mock:
        vt_route = respx_mock.get("/vmf/api/VT/characteristic")
        vt_route.return_value = httpx.Response(500, json={})
        bndw_route = respx_mock.get("/vmf/api/BNDW/allocation")
        bndw_route.return_value = httpx.Response(500, json={})
        yield respx_mock
