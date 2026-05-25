import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.portfolio_manager import (
    add_trade,
    get_holdings,
    get_portfolio_value,
    init_db,
    remove_trade,
)


def run_phase4_flow() -> None:
    db_path = Path("data/test_portfolio.db")
    if db_path.exists():
        db_path.unlink()

    init_db(db_path)

    t1 = add_trade("RELIANCE", 10, 1400.0, db_path=db_path)
    t2 = add_trade("TCS", 5, 3800.0, db_path=db_path)
    t3 = add_trade("INFY", 8, 1500.0, db_path=db_path)
    print(f"  added trades: {t1}, {t2}, {t3}")

    holdings = get_holdings(db_path)
    assert len(holdings) == 3, f"Expected 3 holdings, got {len(holdings)}"
    print(f"  holdings count after add: {len(holdings)}")

    summary = get_portfolio_value(db_path)
    assert "positions" in summary and len(summary["positions"]) == 3
    print(f"  total_cost: {summary['total_cost']}")
    print(f"  total_market_value: {summary['total_market_value']}")
    print(f"  total_pnl: {summary['total_pnl']}")

    removed = remove_trade(t2, db_path)
    assert removed, "Expected trade removal to succeed"
    holdings_after = get_holdings(db_path)
    assert len(holdings_after) == 2, f"Expected 2 holdings, got {len(holdings_after)}"
    print(f"  holdings count after remove: {len(holdings_after)}")

    summary_after = get_portfolio_value(db_path)
    assert "positions" in summary_after and len(summary_after["positions"]) == 2
    print(f"  updated total_cost: {summary_after['total_cost']}")
    print(f"  updated total_market_value: {summary_after['total_market_value']}")
    print(f"  updated total_pnl: {summary_after['total_pnl']}")


if __name__ == "__main__":
    print("Running portfolio_manager Phase 4 flow...\n")
    run_phase4_flow()
    print("\nPhase 4 tests passed!")
