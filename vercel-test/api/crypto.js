const ALLOWED_SYMBOLS = new Set([
  "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "DOGEUSDT",
  "ADAUSDT", "LINKUSDT", "AVAXUSDT", "SUIUSDT", "TRXUSDT", "NEARUSDT",
  "BCHUSDT", "LTCUSDT", "DOTUSDT", "AAVEUSDT",
]);

const SPOT_BASES = [
  "https://data-api.binance.vision",
  "https://api.binance.com",
  "https://api1.binance.com",
  "https://api2.binance.com",
  "https://api3.binance.com",
  "https://api4.binance.com",
];
const FUTURES_BASE = "https://fapi.binance.com";

async function fetchJson(url) {
  const response = await fetch(url, {
    headers: {
      accept: "application/json",
      "user-agent": "MarketTruth-EU-Relay/1.0",
    },
    cache: "no-store",
    signal: AbortSignal.timeout(10000),
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(`HTTP ${response.status}: ${body.slice(0, 180)}`);
  }
  return response.json();
}

async function fetchFirst(urls) {
  const errors = [];
  for (const url of urls) {
    try {
      return await fetchJson(url);
    } catch (error) {
      errors.push(String(error));
    }
  }
  throw new Error(errors.slice(-2).join(" | "));
}

module.exports = async function handler(req, res) {
  if (req.method !== "GET") {
    res.setHeader("Allow", "GET");
    return res.status(405).json({ error: "GET only" });
  }

  const symbol = String(req.query.symbol || "BTCUSDT").trim().toUpperCase();
  if (!ALLOWED_SYMBOLS.has(symbol)) {
    return res.status(400).json({
      error: "Unsupported symbol",
      allowed_symbols: Array.from(ALLOWED_SYMBOLS),
    });
  }

  const spotUrls = (path) => SPOT_BASES.map((base) => `${base}${path}`);
  const tasks = {
    "spot ticker": spotUrls(`/api/v3/ticker/24hr?symbol=${encodeURIComponent(symbol)}`),
    "spot klines": spotUrls(`/api/v3/klines?symbol=${encodeURIComponent(symbol)}&interval=15m&limit=48`),
    "spot depth": spotUrls(`/api/v3/depth?symbol=${encodeURIComponent(symbol)}&limit=100`),
    "funding": [`${FUTURES_BASE}/fapi/v1/fundingRate?symbol=${encodeURIComponent(symbol)}&limit=1`],
    "open interest history": [`${FUTURES_BASE}/futures/data/openInterestHist?symbol=${encodeURIComponent(symbol)}&period=15m&limit=48`],
    "global long short": [`${FUTURES_BASE}/futures/data/globalLongShortAccountRatio?symbol=${encodeURIComponent(symbol)}&period=15m&limit=24`],
    "top trader positions": [`${FUTURES_BASE}/futures/data/topLongShortPositionRatio?symbol=${encodeURIComponent(symbol)}&period=15m&limit=24`],
    "taker flow": [`${FUTURES_BASE}/futures/data/takerlongshortRatio?symbol=${encodeURIComponent(symbol)}&period=15m&limit=24`],
    "basis": [`${FUTURES_BASE}/futures/data/basis?pair=${encodeURIComponent(symbol)}&contractType=PERPETUAL&period=15m&limit=24`],
  };

  const entries = await Promise.all(
    Object.entries(tasks).map(async ([name, urls]) => {
      try {
        const value = await fetchFirst(urls);
        return [name, value, null];
      } catch (error) {
        return [name, null, `${name}: ${String(error)}`];
      }
    })
  );

  const data = {};
  const warnings = [];
  for (const [name, value, warning] of entries) {
    data[name] = value;
    if (warning) warnings.push(warning);
  }

  res.setHeader("Cache-Control", "public, s-maxage=5, stale-while-revalidate=20");
  return res.status(200).json({
    service: "MarketTruth Binance EU relay",
    requested_region: "fra1",
    symbol,
    server_time_utc: new Date().toISOString(),
    data,
    warnings,
  });
};
