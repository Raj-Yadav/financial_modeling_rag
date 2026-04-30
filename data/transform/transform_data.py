def build_documents(data, symbol):
    docs = []

    p = data["profile"][0]
    docs.append({
        "text": f"{p['companyName']} operates in {p['industry']} with market cap {p['mktCap']}.",
        "meta": {"type": "profile", "symbol": symbol}
    })

    for m in data["metrics"]:
        docs.append({
            "text": f"On {m['date']}, PE ratio {m.get('peRatio')} and ROE {m.get('roe')}.",
            "meta": {"type": "metrics", "symbol": symbol}
        })

    prices = data["price"]["historical"][:30]
    latest, past = prices[0], prices[-1]
    change = (latest['close'] - past['close']) / past['close'] * 100

    docs.append({
        "text": f"{symbol} moved {change:.2f}% in last 30 days.",
        "meta": {"type": "price", "symbol": symbol}
    })

    return docs