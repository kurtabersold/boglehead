import functools
from collections.abc import Callable
from decimal import Decimal

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
    """Get the percentage of domestic and foreign holdings in VT

    See: https://investor.vanguard.com/investment-products/etfs/profile/vt
    """
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
    """Get the percentage of domestic and foreign holdings in BNDW

    See: https://investor.vanguard.com/investment-products/etfs/profile/bndw
    """
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


def balance_option(func: Callable) -> Callable:
    @click.option(
        # https://click.palletsprojects.com/en/stable/parameter-types/#built-in-types-listing
        "--amount",
        "-a",
        type=click.FloatRange(min=0, min_open=False, max_open=False, clamp=False),
        default=0.00,
        help="Total account balance",
    )
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


@cli.command()
@bonds_option
@balance_option
async def two_fund(bonds: float, amount: float) -> None:
    """Two-fund portfolio

    See: https://www.bogleheads.org/wiki/Two-fund_portfolio
    """
    two_fund_percentage = await vanguard.two_fund(bond=bonds)
    total_balance = Decimal(str(amount))
    vt_percent = two_fund_percentage["VT"]
    vt_amount = total_balance * (vt_percent / 100)
    bndw_percent = two_fund_percentage["BNDW"]
    bndw_amount = total_balance * (bndw_percent / 100)
    click.echo(
        f"Equities (VT): {vt_percent.normalize():f}% (${vt_amount.normalize():f})"
    )
    click.echo(
        f"Bonds (BNDW): {bndw_percent.normalize():f}% (${bndw_amount.normalize():f})"
    )


@cli.command()
@bonds_option
@balance_option
async def three_fund(bonds: float, amount: float) -> None:
    """Three-fund portfolio

    See: https://www.bogleheads.org/wiki/Three-fund_portfolio
    """
    try:
        three_fund_percentage = await vanguard.three_fund(bond=bonds)
    except Exception as e:
        click.echo(f"Got an exception: {e}")
        raise ServerErrorException(f"Got an exception: {e}") from e
    else:
        total_balance = Decimal(str(amount))
        vti_percent = three_fund_percentage["VTI"]
        vti_amount = total_balance * (vti_percent / 100)
        vxus_percent = three_fund_percentage["VXUS"]
        vxus_amount = total_balance * (vxus_percent / 100)
        bndw_percent = three_fund_percentage["BNDW"]
        bndw_amount = total_balance * (bndw_percent / 100)
        click.echo(
            f"Domestic Equities (VTI): {vti_percent.normalize():f}% (${vti_amount.normalize():f})"
        )
        click.echo(
            f"Foreign Equities (VXUS): {vxus_percent.normalize():f}% (${vxus_amount.normalize():f})"
        )
        click.echo(
            f"Bonds (BNDW): {bndw_percent.normalize():f}% (${bndw_amount.normalize():f})"
        )


@cli.command()
@bonds_option
@balance_option
async def four_fund(bonds: float, amount: float) -> None:
    """Four-fund portfolio

    See: https://www.bogleheads.org/wiki/Vanguard_four_fund_portfolio
    """
    try:
        four_fund_percentage = await vanguard.four_fund(bond=bonds)
    except Exception as e:
        click.echo(f"Got an exception: {e}")
        raise ServerErrorException(f"Got an exception: {e}") from e
    else:
        total_balance = Decimal(str(amount))
        vti_percent = four_fund_percentage["VTI"]
        vti_amount = total_balance * (vti_percent / 100)
        vxus_percent = four_fund_percentage["VXUS"]
        vxus_amount = total_balance * (vxus_percent / 100)
        bnd_percent = four_fund_percentage["BND"]
        bnd_amount = total_balance * (bnd_percent / 100)
        bndx_percent = four_fund_percentage["BNDX"]
        bndx_amount = total_balance * (bndx_percent / 100)
        click.echo(
            f"Domestic Equities (VTI): {vti_percent.normalize():f}% (${vti_amount.normalize():f})"
        )
        click.echo(
            f"Foreign Equities (VXUS): {vxus_percent.normalize():f}% (${vxus_amount.normalize():f})"
        )
        click.echo(
            f"Domestic Bonds (BND): {bnd_percent.normalize():f}% (${bnd_amount.normalize():f})"
        )
        click.echo(
            f"Foreign Bonds (BNDX): {bndx_percent.normalize():f}% (${bndx_amount.normalize():f})"
        )
