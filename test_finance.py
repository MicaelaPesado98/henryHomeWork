import math
import pathlib
import importlib.util
import pytest

# import finance functions (works whether tests run from project root or editor)
try:
    from finance import (
        calculate_compound_interest,
        calculate_annuity_payment,
        calculate_internal_rate_of_return,
    )
except Exception:
    spec = importlib.util.spec_from_file_location(
        "finance",
        str(pathlib.Path(__file__).resolve().parent / "finance.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    calculate_compound_interest = mod.calculate_compound_interest
    calculate_annuity_payment = mod.calculate_annuity_payment
    calculate_internal_rate_of_return = mod.calculate_internal_rate_of_return


def _npv(cash_flows, r):
    return sum(cf / (1 + r) ** i for i, cf in enumerate(cash_flows))


def test_annuity_payment_zero_rate_returns_principal_over_periods():
    assert calculate_annuity_payment(1200.0, 0.0, 12) == pytest.approx(100.0)


def test_annuity_payment_zero_periods_raises_zero_division():
    with pytest.raises(ZeroDivisionError):
        calculate_annuity_payment(1000.0, 0.05, 0)


def test_compound_interest_zero_rate_identity():
    assert calculate_compound_interest(500.0, 0.0, 5) == pytest.approx(500.0)


def test_compound_interest_fractional_and_negative_periods_consistent():
    fv = calculate_compound_interest(1000.0, 0.05, 0.5)
    pv = calculate_compound_interest(1000.0, 0.05, -1)
    assert fv == pytest.approx(1000.0 * (1.05 ** 0.5))
    assert pv == pytest.approx(1000.0 * (1.05 ** -1))


def test_compound_interest_zero_periods():
    assert calculate_compound_interest(1234.5, 0.05, 0) == pytest.approx(1234.5)






def test_irr_returns_reasonable_root_for_multi_period_case():
    cfs = [-100.0, 60.0, 60.0]
    r = calculate_internal_rate_of_return(cfs)
    assert isinstance(r, float)
    assert abs(_npv(cfs, r)) < 1e-5


def test_irr_handles_small_alternating_series():
    cfs = [-1.0] + [0.3 if i % 2 == 0 else -0.1 for i in range(1, 20)]
    r = calculate_internal_rate_of_return(cfs)
    assert isinstance(r, float)
    assert abs(_npv(cfs, r)) < 1e-4



def test_irr_simple_two_period_root():
    # -100 + 110/(1+r) = 0 -> r = 0.1
    r = calculate_internal_rate_of_return([-100.0, 110.0])
    assert r == pytest.approx(0.1, rel=1e-8)


def test_irr_newton_updates_guess_when_derivative_nonzero():
    # With these cashflows the derivative at r=0.1 is non-zero, so one
    # Newton iteration should update the guess away from 0.1.
    cfs = [-100.0, 200.0]
    r = calculate_internal_rate_of_return(cfs, iterations=1)
    assert isinstance(r, float)
    assert not pytest.approx(0.1) == r
    assert math.isfinite(r)


def test_irr_derivative_exact_zero_returns_guess():
    # derivative depends only on cashflows with i>=1; for a two-term
    # series derivative at any r is -1*cf1/(1+r)**2. If cf1 == 0, derivative == 0.
    r = calculate_internal_rate_of_return([-100.0, 0.0])
    assert pytest.approx(0.1, rel=1e-12) == r


def test_annuity_payment_negative_principal():
    val = calculate_annuity_payment(-1000.0, 0.03, 5)
    assert isinstance(val, float)
    assert val < 0


def test_annuity_payment_small_rate_finite():
    val = calculate_annuity_payment(500.0, 1e-12, 10)
    assert math.isfinite(val)


def test_fallback_iterations_zero_no_sign_change_returns_guess():
    # Skip Newton and ensure no sign change in fallback -> function returns the initial guess
    r = calculate_internal_rate_of_return([-1.0, 0.0001], iterations=0)
    assert pytest.approx(0.1, rel=1e-12) == r


def test_compound_interest_zero_principal_returns_zero():
    assert calculate_compound_interest(0.0, 0.05, 10) == pytest.approx(0.0)


def test_annuity_payment_one_period_equals_principal_times_one_plus_rate():
    val = calculate_annuity_payment(1000.0, 0.05, 1)
    assert val == pytest.approx(1000.0 * (1 + 0.05))


def test_irr_returns_finite_float_for_mixed_cashflows():
    cfs = [-1000.0, 100.0, 200.0, 900.0]
    r = calculate_internal_rate_of_return(cfs)
    assert isinstance(r, float)
    assert math.isfinite(r)


def test_irr_handles_large_cashflows_finite():
    cfs = [-1e9, 6e8, 6e8]
    r = calculate_internal_rate_of_return(cfs)
    assert isinstance(r, float)
    assert math.isfinite(r)






