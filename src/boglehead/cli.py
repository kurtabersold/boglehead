import functools
from collections.abc import Callable

import asyncclick as click

from boglehead import vanguard


class ServerErrorException(click.ClickException):
    exit_code = 1


class OrderCommands(click.Group):
    def list_commands(self, ctx: click.Context) -> list[str]:
        return list(self.commands)


@click.group(cls=OrderCommands)
# @click.option("--debug/--no-debug", default=False)
async def cli(
    # debug: bool
) -> None:
    """Boglehead Portfolio Allocation CLI"""
    # click.echo(f"Debug mode is {'on' if debug else 'off'}")
    pass


@cli.command()
async def vt() -> None:
    """Get the percentage of domestic and foreign holdings in VT"""
    try:
        vt_composition = await vanguard.get_vt_composition()
    except Exception as e:
        # click.echo(f"Got an exception: {e}")
        raise ServerErrorException(f"Got an exception: {e}") from e
    else:
        # click.echo(vt_composition)
        click.echo(
            f"Percentage of domestic holdings (VTI): {vt_composition['VTI'].normalize():f}%"
        )
        click.echo(
            f"Percentage of foreign holdings (VXUS): {vt_composition['VXUS'].normalize():f}%"
        )


@cli.command()
async def bndw() -> None:
    """Get the percentage of domestic and foreign holdings in BNDW"""
    try:
        bndw_composition = await vanguard.get_bndw_composition()
    except Exception as e:
        # click.echo(f"Got an exception: {e}")
        raise ServerErrorException(f"Got an exception: {e}") from e
    else:
        # click.echo(bndw_composition)
        click.echo(
            f"Percentage of domestic holdings (BND): {bndw_composition['BND'].normalize():f}%"
        )
        click.echo(
            f"Percentage of foreign holdings (BNDX): {bndw_composition['BNDX'].normalize():f}%"
        )


def bonds_option(func: Callable) -> Callable:
    @click.option(
        # https://click.palletsprojects.com/en/stable/parameter-types/#built-in-types-listing
        "--bonds",
        "-b",
        type=click.FloatRange(
            min=0, max=100, min_open=False, max_open=False, clamp=False
        ),
        default=10.0,
        help="Total percentage of bonds",
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@cli.command()
@bonds_option
async def two_fund(bonds: float) -> None:
    """Blah blah"""
    two_fund_percentage = await vanguard.two_fund(bond=bonds)
    click.echo(f"Equities (VT): {two_fund_percentage['VT'].normalize():f}%")
    click.echo(f"Bonds (BNDW): {two_fund_percentage['BNDW'].normalize():f}%")


@cli.command()
@bonds_option
async def three_fund(bonds: float) -> None:
    """Blah blah blah

    See: https://www.bogleheads.org/wiki/Three-fund_portfolio
    """
    try:
        three_fund_percentage = await vanguard.three_fund(bond=bonds)
    except Exception as e:
        click.echo(f"Got an exception: {e}")
        raise ServerErrorException(f"Got an exception: {e}") from e
    else:
        click.echo(
            f"Domestic Equities (VTI): {three_fund_percentage['VTI'].normalize():f}%"
        )
        click.echo(
            f"Foreign Equities (VXUS): {three_fund_percentage['VXUS'].normalize():f}%"
        )
        click.echo(f"Bonds (BNDW): {three_fund_percentage['BNDW'].normalize():f}%")


@cli.command()
@bonds_option
async def four_fund(bonds: float) -> None:
    """Blah blah blah blah

    See: https://www.bogleheads.org/wiki/Vanguard_four_fund_portfolio
    """
    try:
        four_fund_percentage = await vanguard.four_fund(bond=bonds)
    except Exception as e:
        click.echo(f"Got an exception: {e}")
        raise ServerErrorException(f"Got an exception: {e}") from e
    else:
        click.echo(
            f"Domestic Equities (VTI): {four_fund_percentage['VTI'].normalize():f}%"
        )
        click.echo(
            f"Foreign Equities (VXUS): {four_fund_percentage['VXUS'].normalize():f}%"
        )
        click.echo(
            f"Domestic Bonds (BND): {four_fund_percentage['BND'].normalize():f}%"
        )
        click.echo(
            f"Foreign Bonds (BNDX): {four_fund_percentage['BNDX'].normalize():f}%"
        )
