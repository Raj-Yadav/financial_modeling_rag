def build_documents(data, symbol):
    docs = []

    # --- 1. PROFILE DATA ---
    p = data.get("profile", [{}])[0]
    
    company_name = p.get('companyName', symbol)
    industry = p.get('industry', 'Unknown Industry')
    sector = p.get('sector', 'Unknown Sector')
    market_cap = p.get('marketCap', 'unknown')
    description = p.get('description', '')

    # Build a richer text chunk for the LLM
    profile_text = f"{company_name} operates in the {industry} industry within the {sector} sector with a market cap of {market_cap}. "
    
    # Optional: Add the first sentence of the company description to give the LLM deep context
    if description:
        first_sentence = description.split('. ')[0] + "."
        profile_text += f"Overview: {first_sentence}"

    docs.append({
        "text": profile_text.strip(),
        "meta": {"type": "profile", "symbol": symbol}
    })

    # --- 2. METRICS DATA ---
    # Use data.get() just in case the "metrics" key is entirely missing from the payload
    for m in data.get("metrics", []):
        date = m.get('date', 'Unknown Date')
        docs.append({
            "text": f"On {date}, PE ratio {m.get('peRatio', 'N/A')} and ROE {m.get('roe', 'N/A')}.",
            "meta": {"type": "metrics", "symbol": symbol}
        })

    # --- 3. PRICE DATA ---
    # Safely grab the price data. Default to an empty list if missing.
    raw_price_data = data.get("price", [])
    
    # Handle both API formats: Dictionary with "historical" key OR direct List
    if isinstance(raw_price_data, dict):
        prices = raw_price_data.get("historical", [])
    elif isinstance(raw_price_data, list):
        prices = raw_price_data
    else:
        prices = []
    
    if len(prices) > 0:
        prices_subset = prices[:30]
        latest, past = prices_subset[0], prices_subset[-1]
        
        # Prevent division by zero if a stock had a $0.00 close price
        past_close = past.get('close', 0)
        latest_close = latest.get('close', 0)
        
        if past_close != 0:
            change = (latest_close - past_close) / past_close * 100
            docs.append({
                "text": f"{symbol} moved {change:.2f}% in last {len(prices_subset)} days.",
                "meta": {"type": "price", "symbol": symbol}
            })

    return docs