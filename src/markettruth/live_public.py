from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


# Public crypto demo traffic is routed through a small Vercel Function in Frankfurt.
# This avoids cloud-host geo/IP restrictions while keeping the app read only.
CRYPTO_RELAY_BASE = "https://markettruth-api.vercel.app"

# Direct Binance hosts remain as a fallback for local use or relay outages.
SPOT_BASES = (
    "https://api.binance.com",
    "https://api-gcp.binance.com",
    "https://api1.binance.com",
    "https://api2.binance.com",
    "https://api3.binance.com",
    "https://api4.binance.com",
    "https://data-api.binance.vision",
)
FUTURES_BASE = "https://fapi.binance.com"
WEB3_BASE = "https://www.binance.com/bapi/defi"

BINANCE_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "identity",
    "User-Agent": "MarketTruth-AI/1.0",
}
WEB3_HEADERS = {
    "Accept": "application/json",
    "Accept-Encoding": "identity",
    "User-Agent": "binance-web3/1.1 (Skill)",
}

POPULAR_CRYPTO_SYMBOLS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT",
    "ADAUSDT", "LINKUSDT", "AVAXUSDT", "SUIUSDT", "TRXUSDT", "NEARUSDT",
    "BCHUSDT", "LTCUSDT", "DOTUSDT", "AAVEUSDT",
]


class LiveDataError(RuntimeError):
    pass


def _request_json(
    base: str,
    path: str,
    params: dict[str, Any] | None = None,
    *,
    web3: bool = False,
) -> Any:
    query = f"?{urlencode(params)}" if params else ""
    headers = WEB3_HEADERS if web3 else BINANCE_HEADERS
    request = Request(base + path + query, headers=headers)
    try:
        with urlopen(request, timeout=12) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise LiveDataError(f"HTTP {exc.code} from {path}") from exc
    except URLError as exc:
        raise LiveDataError(f"Network error from {path}: {exc.reason}") from exc
    except TimeoutError as exc:
        raise LiveDataError(f"Timeout from {path}") from exc

    if web3 and isinstance(payload, dict):
        if payload.get("code") not in (None, "000000") or payload.get("success") is False:
            raise LiveDataError(
                f"Binance Web3 error from {path}: {payload.get('message') or payload.get('code')}"
            )
    return payload


def _request_json_any(
    bases: str | Sequence[str],
    path: str,
    params: dict[str, Any] | None = None,
    *,
    web3: bool = False,
) -> Any:
    candidates = (bases,) if isinstance(bases, str) else tuple(bases)
    errors: list[str] = []
    for base in candidates:
        try:
            return _request_json(base, path, params, web3=web3)
        except Exception as exc:
            errors.append(f"{base}: {exc}")
    raise LiveDataError("all official Binance hosts failed; " + " | ".join(errors[-3:]))


def _float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _pct_change(new: float | None, old: float | None) -> float | None:
    if new is None or old in (None, 0):
        return None
    return (new / old - 1.0) * 100.0


def _iso_ms(value: Any) -> str | None:
    number = _float(value)
    if number is None:
        return None
    return datetime.fromtimestamp(number / 1000.0, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _latest_timestamp_ms(*payloads: Any) -> float | None:
    values: list[float] = []
    for payload in payloads:
        if isinstance(payload, dict):
            for key in ("time", "closeTime", "timestamp", "fundingTime"):
                value = _float(payload.get(key))
                if value is not None:
                    values.append(value)
        elif isinstance(payload, list) and payload:
            item = payload[-1]
            if isinstance(item, dict):
                for key in ("timestamp", "time", "fundingTime"):
                    value = _float(item.get(key))
                    if value is not None:
                        values.append(value)
            elif isinstance(item, list) and len(item) > 6:
                value = _float(item[6])
                if value is not None:
                    values.append(value)
    return max(values) if values else None


TaskSpec = tuple[str | Sequence[str], str, dict[str, Any] | None, bool]


def _parallel(tasks: dict[str, TaskSpec]) -> tuple[dict[str, Any], list[str]]:
    results: dict[str, Any] = {}
    warnings: list[str] = []

    def run(item: tuple[str, TaskSpec]) -> tuple[str, Any, str | None]:
        name, (bases, path, params, web3) = item
        try:
            return name, _request_json_any(bases, path, params, web3=web3), None
        except Exception as exc:
            return name, None, f"{name}: {exc}"

    with ThreadPoolExecutor(max_workers=min(10, len(tasks))) as pool:
        for name, value, error in pool.map(run, tasks.items()):
            results[name] = value
            if error:
                warnings.append(error)
    return results, warnings


def _crypto_tasks(symbol: str) -> dict[str, TaskSpec]:
    return {
        "spot ticker": (SPOT_BASES, "/api/v3/ticker/24hr", {"symbol": symbol}, False),
        "spot klines": (SPOT_BASES, "/api/v3/klines", {"symbol": symbol, "interval": "15m", "limit": 48}, False),
        "spot depth": (SPOT_BASES, "/api/v3/depth", {"symbol": symbol, "limit": 100}, False),
        "funding": (FUTURES_BASE, "/fapi/v1/fundingRate", {"symbol": symbol, "limit": 1}, False),
        "open interest history": (FUTURES_BASE, "/futures/data/openInterestHist", {"symbol": symbol, "period": "15m", "limit": 48}, False),
        "global long short": (FUTURES_BASE, "/futures/data/globalLongShortAccountRatio", {"symbol": symbol, "period": "15m", "limit": 24}, False),
        "top trader positions": (FUTURES_BASE, "/futures/data/topLongShortPositionRatio", {"symbol": symbol, "period": "15m", "limit": 24}, False),
        "taker flow": (FUTURES_BASE, "/futures/data/takerlongshortRatio", {"symbol": symbol, "period": "15m", "limit": 24}, False),
        "basis": (FUTURES_BASE, "/futures/data/basis", {"pair": symbol, "contractType": "PERPETUAL", "period": "15m", "limit": 24}, False),
    }


def _fetch_crypto_relay(symbol: str) -> tuple[dict[str, Any], list[str]]:
    payload = _request_json(CRYPTO_RELAY_BASE, "/api/crypto", {"symbol": symbol})
    if not isinstance(payload, dict):
        raise LiveDataError("EU relay returned an invalid payload")
    data = payload.get("data")
    warnings = payload.get("warnings")
    if not isinstance(data, dict):
        raise LiveDataError("EU relay returned no market data")
    if not isinstance(warnings, list):
        warnings = []
    return data, [str(item) for item in warnings]


def _normalize_crypto_data(
    symbol: str,
    data: dict[str, Any],
    warnings: list[str],
) -> tuple[dict[str, Any], list[str]]:
    ticker = data.get("spot ticker") if isinstance(data.get("spot ticker"), dict) else {}
    klines = data.get("spot klines") if isinstance(data.get("spot klines"), list) else []
    depth = data.get("spot depth") if isinstance(data.get("spot depth"), dict) else {}

    funding_payload = data.get("funding")
    if isinstance(funding_payload, list):
        funding = funding_payload[-1] if funding_payload and isinstance(funding_payload[-1], dict) else {}
    elif isinstance(funding_payload, dict):
        funding = funding_payload
    else:
        funding = {}

    oi_hist = data.get("open interest history") if isinstance(data.get("open interest history"), list) else []
    global_ls = data.get("global long short") if isinstance(data.get("global long short"), list) else []
    top_ls = data.get("top trader positions") if isinstance(data.get("top trader positions"), list) else []
    taker = data.get("taker flow") if isinstance(data.get("taker flow"), list) else []
    basis = data.get("basis") if isinstance(data.get("basis"), list) else []

    closes = [_float(row[4]) for row in klines if isinstance(row, list) and len(row) > 4]
    closes = [value for value in closes if value is not None]
    price_1h = _pct_change(closes[-1], closes[-5]) if len(closes) >= 5 else None
    price_4h = _pct_change(closes[-1], closes[-17]) if len(closes) >= 17 else None

    bids = depth.get("bids") or []
    asks = depth.get("asks") or []
    bid_notional = sum(
        (_float(row[0]) or 0) * (_float(row[1]) or 0)
        for row in bids[:20]
        if isinstance(row, list) and len(row) >= 2
    )
    ask_notional = sum(
        (_float(row[0]) or 0) * (_float(row[1]) or 0)
        for row in asks[:20]
        if isinstance(row, list) and len(row) >= 2
    )
    imbalance = bid_notional / ask_notional if ask_notional > 0 else None

    oi_values = [_float(item.get("sumOpenInterest")) for item in oi_hist if isinstance(item, dict)]
    oi_values = [value for value in oi_values if value is not None]
    oi_1h = _pct_change(oi_values[-1], oi_values[-5]) if len(oi_values) >= 5 else None
    oi_4h = _pct_change(oi_values[-1], oi_values[-17]) if len(oi_values) >= 17 else None

    latest_global = global_ls[-1] if global_ls and isinstance(global_ls[-1], dict) else {}
    latest_top = top_ls[-1] if top_ls and isinstance(top_ls[-1], dict) else {}
    latest_taker = taker[-1] if taker and isinstance(taker[-1], dict) else {}
    latest_basis = basis[-1] if basis and isinstance(basis[-1], dict) else {}

    taker_ratio = _float(latest_taker.get("buySellRatio"))
    if taker_ratio is None:
        buy = _float(latest_taker.get("buyVol"))
        sell = _float(latest_taker.get("sellVol"))
        taker_ratio = buy / sell if buy is not None and sell not in (None, 0) else None

    basis_rate = _float(latest_basis.get("basisRate"))
    basis_pct = basis_rate * 100.0 if basis_rate is not None else None
    funding_rate = _float(funding.get("fundingRate"))
    if funding_rate is None:
        funding_rate = _float(funding.get("lastFundingRate"))

    timestamp_ms = _latest_timestamp_ms(ticker, klines, funding, oi_hist, global_ls, top_ls, taker, basis)
    snapshot = {
        "symbol": symbol,
        "price_change_24h": _float(ticker.get("priceChangePercent")),
        "price_change_1h": price_1h,
        "price_change_4h": price_4h,
        "quote_volume_24h": _float(ticker.get("quoteVolume")),
        "orderbook_imbalance": imbalance,
        "funding_rate": funding_rate,
        "oi_change_1h": oi_1h,
        "oi_change_4h": oi_4h,
        "long_short_ratio": _float(latest_global.get("longShortRatio")),
        "top_trader_position_ratio": _float(latest_top.get("longShortRatio")),
        "taker_buy_sell_ratio": taker_ratio,
        "basis_pct": basis_pct,
        "data_timestamp": _iso_ms(timestamp_ms),
    }

    coverage = sum(value is not None for key, value in snapshot.items() if key != "symbol")
    if coverage < 5:
        warnings.append(
            "Live coverage is too limited for a high-quality investigation; "
            "use the validated example if this host cannot reach enough Binance market endpoints."
        )
    return snapshot, warnings


def fetch_crypto_snapshot(symbol: str) -> tuple[dict[str, Any], list[str]]:
    symbol = symbol.strip().upper()
    if symbol not in POPULAR_CRYPTO_SYMBOLS:
        raise LiveDataError("Market Move Autopsy currently expects a supported USDT spot/perpetual symbol")

    try:
        data, warnings = _fetch_crypto_relay(symbol)
    except Exception as relay_exc:
        data, warnings = _parallel(_crypto_tasks(symbol))
        warnings.insert(0, f"EU relay unavailable; direct Binance fallback used: {relay_exc}")

    return _normalize_crypto_data(symbol, data, warnings)


def fetch_tokenized_stock_list() -> list[dict[str, Any]]:
    payload = _request_json(
        WEB3_BASE,
        "/v1/public/wallet-direct/buw/wallet/market/token/rwa/stock/detail/list/ai",
        {"type": 1},
        web3=True,
    )
    rows = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise LiveDataError("Tokenized stock list returned no data")
    return [
        row
        for row in rows
        if isinstance(row, dict) and row.get("ticker") and row.get("contractAddress")
    ]


def _select_stock_deployment(rows: list[dict[str, Any]], ticker: str) -> dict[str, Any]:
    ticker = ticker.strip().upper()
    matches = [row for row in rows if str(row.get("ticker", "")).upper() == ticker]
    if not matches:
        raise LiveDataError(f"{ticker} is not present in the Binance tokenized securities list")
    return next((row for row in matches if str(row.get("chainId")) == "56"), matches[0])


def _status_label(overall: dict[str, Any]) -> str | None:
    reason = str(overall.get("reasonCode") or "").upper()
    if overall.get("openState") is True:
        return "open"
    if "PAUSED" in reason:
        return "pause"
    if "CLOSED" in reason:
        return "closed"
    return "closed" if overall.get("openState") is False else None


def fetch_cross_market_snapshot(
    ticker: str,
    rows: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    ticker = ticker.strip().upper()
    rows = rows or fetch_tokenized_stock_list()
    deployment = _select_stock_deployment(rows, ticker)
    chain_id = str(deployment.get("chainId"))
    contract = str(deployment.get("contractAddress"))
    query = {"chainId": chain_id, "contractAddress": contract}

    tasks: dict[str, TaskSpec] = {
        "dynamic": (WEB3_BASE, "/v2/public/wallet-direct/buw/wallet/market/token/rwa/dynamic/ai", query, True),
        "asset status": (WEB3_BASE, "/v1/public/wallet-direct/buw/wallet/market/token/rwa/asset/market/status/ai", query, True),
        "overall status": (WEB3_BASE, "/v1/public/wallet-direct/buw/wallet/market/token/rwa/market/status/ai", None, True),
    }
    data, warnings = _parallel(tasks)

    dynamic_payload = data.get("dynamic") if isinstance(data.get("dynamic"), dict) else {}
    dynamic = dynamic_payload.get("data") if isinstance(dynamic_payload.get("data"), dict) else {}
    token = dynamic.get("tokenInfo") if isinstance(dynamic.get("tokenInfo"), dict) else {}
    stock = dynamic.get("stockInfo") if isinstance(dynamic.get("stockInfo"), dict) else {}
    dynamic_status = dynamic.get("statusInfo") if isinstance(dynamic.get("statusInfo"), dict) else {}

    asset_payload = data.get("asset status") if isinstance(data.get("asset status"), dict) else {}
    asset_status = asset_payload.get("data") if isinstance(asset_payload.get("data"), dict) else {}
    status = asset_status or dynamic_status

    overall_payload = data.get("overall status") if isinstance(data.get("overall status"), dict) else {}
    overall = overall_payload.get("data") if isinstance(overall_payload.get("data"), dict) else {}

    multiplier = _float(token.get("sharesMultiplier"))
    if multiplier is None:
        multiplier = _float(deployment.get("multiplier"))

    snapshot = {
        "ticker": ticker,
        "token_symbol": dynamic.get("symbol") or deployment.get("symbol"),
        "chain_id": chain_id,
        "contract_address": contract,
        "token_price": _float(token.get("price")),
        "stock_price": _float(stock.get("price")),
        "shares_multiplier": multiplier,
        "token_price_change_24h": _float(token.get("priceChangePct24h")),
        "total_holders": _int(token.get("totalHolders")),
        "token_market_cap": _float(token.get("marketCap")),
        "market_status": status.get("marketStatus"),
        "overall_market_status": _status_label(overall),
        "open_state": status.get("openState"),
        "reason_code": status.get("reasonCode"),
        "reason_msg": status.get("reasonMsg"),
        "next_open_time": _iso_ms(status.get("nextOpenTime")),
        "next_close_time": _iso_ms(status.get("nextCloseTime")),
        "price_to_earnings": _float(stock.get("priceToEarnings")),
        "dividend_yield": _float(stock.get("dividendYield")),
        "price_high_52w": _float(stock.get("priceHigh52w")),
        "price_low_52w": _float(stock.get("priceLow52w")),
        "data_timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return snapshot, warnings