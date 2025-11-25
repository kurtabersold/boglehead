import pytest
from asyncclick.testing import CliRunner

from boglehead.cli import cli


@pytest.mark.asyncio
async def test_help():
    runner = CliRunner()
    result = await runner.invoke(cli, ["--help"])
    assert result.exit_code == 0


@pytest.mark.asyncio
async def test_vt(mocked_vanguard):
    runner = CliRunner()
    result = await runner.invoke(cli, ["vt"])
    assert result.exit_code == 0


@pytest.mark.asyncio
async def test_vt_exception(mocked_vanguard_exception):
    runner = CliRunner()
    result = await runner.invoke(cli, ["vt"])
    assert result.exit_code == 1


@pytest.mark.asyncio
async def test_bndw(mocked_vanguard):
    runner = CliRunner()
    result = await runner.invoke(cli, ["bndw"])
    assert result.exit_code == 0


@pytest.mark.asyncio
async def test_bndw_exception(mocked_vanguard_exception):
    runner = CliRunner()
    result = await runner.invoke(cli, ["bndw"])
    assert result.exit_code == 1


@pytest.mark.asyncio
async def test_two_fund():
    runner = CliRunner()
    result = await runner.invoke(cli, ["two-fund"])
    assert result.exit_code == 0


@pytest.mark.asyncio
async def test_three_fund(mocked_vanguard):
    runner = CliRunner()
    result = await runner.invoke(cli, ["three-fund"])
    assert result.exit_code == 0


@pytest.mark.asyncio
async def test_three_fund_exception(mocked_vanguard_exception):
    runner = CliRunner()
    result = await runner.invoke(cli, ["three-fund"])
    assert result.exit_code == 1


@pytest.mark.asyncio
async def test_four_fund(mocked_vanguard):
    runner = CliRunner()
    result = await runner.invoke(cli, ["four-fund"])
    assert result.exit_code == 0


@pytest.mark.asyncio
async def test_four_fund_exception(mocked_vanguard_exception):
    runner = CliRunner()
    result = await runner.invoke(cli, ["four-fund"])
    assert result.exit_code == 1
