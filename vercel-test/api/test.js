module.exports = async function handler(req, res) {
  const tests = {
    spot: "https://data-api.binance.vision/api/v3/ticker/24hr?symbol=BTCUSDT",
    futuresPremiumIndex: "https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT",
    futuresLongShort: "https://fapi.binance.com/futures/data/globalLongShortAccountRatio?symbol=BTCUSDT&period=15m&limit=1",
  };

  async function run(url) {
    const started = Date.now();
    try {
      const response = await fetch(url, {
        headers: {
          accept: "application/json",
          "user-agent": "MarketTruth-Vercel-Test/1.0",
        },
        cache: "no-store",
      });
      const text = await response.text();
      return {
        http: response.status,
        time_ms: Date.now() - started,
        body_preview: text.slice(0, 700),
      };
    } catch (error) {
      return {
        http: 0,
        time_ms: Date.now() - started,
        error: String(error),
        body_preview: "",
      };
    }
  }

  const results = {};
  for (const [name, url] of Object.entries(tests)) {
    results[name] = await run(url);
  }

  res.setHeader("Cache-Control", "no-store");
  res.status(200).json({
    service: "MarketTruth Binance connectivity test",
    requested_region: "fra1",
    server_time_utc: new Date().toISOString(),
    results,
  });
};
