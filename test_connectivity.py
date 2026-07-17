"""
Quick connectivity test - run from GitHub Actions to check whether
NSE and/or Yahoo Finance option chain data is reachable from a cloud runner.
No credentials needed. Just prints results to the Action log.
"""

import sys
import json
import requests


def test_yfinance():
    print("\n" + "=" * 50)
    print("TEST 1: Yahoo Finance (yfinance) - NIFTY 50 (^NSEI)")
    print("=" * 50)
    try:
        import yfinance as yf
        ticker = yf.Ticker("^NSEI")
        expiries = ticker.options
        print(f"SUCCESS - Expiries found: {expiries[:5] if expiries else 'NONE'}")

        if expiries:
            chain = ticker.option_chain(expiries[0])
            print(f"Calls sample:\n{chain.calls.head(3)}")
            print(f"Puts sample:\n{chain.puts.head(3)}")
            print(f"\nTotal call strikes: {len(chain.calls)}")
            print(f"Total put strikes: {len(chain.puts)}")
        return True
    except Exception as e:
        print(f"FAILED - {type(e).__name__}: {e}")
        return False


def test_nse_direct():
    print("\n" + "=" * 50)
    print("TEST 2: NSE direct API (session + cookies)")
    print("=" * 50)
    try:
        session = requests.Session()
        headers = {
            "user-agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "accept-language": "en-US,en;q=0.9",
            "accept-encoding": "gzip, deflate, br",
        }

        # Step 1: hit homepage first to get cookies
        r1 = session.get("https://www.nseindia.com", headers=headers, timeout=15)
        print(f"Homepage status: {r1.status_code}")

        # Step 2: hit the option chain API
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        r2 = session.get(url, headers=headers, timeout=15)
        print(f"API status: {r2.status_code}")

        if r2.status_code == 200:
            data = r2.json()
            records = data.get("records", {}).get("data", [])
            print(f"SUCCESS - {len(records)} strike records returned")
            print(f"Underlying value: {data.get('records', {}).get('underlyingValue')}")
            return True
        else:
            print(f"FAILED - Non-200 status. Body preview: {r2.text[:300]}")
            return False

    except Exception as e:
        print(f"FAILED - {type(e).__name__}: {e}")
        return False


def test_nsepython():
    print("\n" + "=" * 50)
    print("TEST 3: nsepython library")
    print("=" * 50)
    try:
        from nsepython import nse_optionchain_scrapper
        data = nse_optionchain_scrapper("NIFTY")
        records = data.get("records", {}).get("data", [])
        print(f"SUCCESS - {len(records)} strike records returned")
        print(f"Underlying value: {data.get('records', {}).get('underlyingValue')}")
        return True
    except Exception as e:
        print(f"FAILED - {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    results = {
        "yfinance": test_yfinance(),
        "nse_direct": test_nse_direct(),
        "nsepython": test_nsepython(),
    }

    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    for name, ok in results.items():
        print(f"{name}: {'WORKS' if ok else 'BLOCKED/FAILED'}")

    # Exit code 0 if at least one method worked, 1 if all failed
    sys.exit(0 if any(results.values()) else 1)
