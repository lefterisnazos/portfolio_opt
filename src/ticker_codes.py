# Materials (XLB)
XLB = ["APD", "NEM", "NUE", "FCX"]

# Communication Services (XLC)
XLC = ["NFLX", "VZ", "ATVI", "DIS"]

# Energy (XLE)
XLE = ["OXY", "PSX", "COP", "DVN"]

# Financials (XLF)
XLF = ["BAC", "AXP", "CB", "C"]

# Industrials (XLI)
XLI = ["LMT", "CAT", "UNP", "FDX"]

# Technology (XLK)
XLK = ["ORCL", "CRM", "ADBE", "TXN"]

# Consumer Staples (XLP)
XLP = ["GIS", "PG", "KO", "KR"]

# Utilities (XLU)
XLU = ["EXC", "DUK", "EIX", "NEE"]

# Health Care (XLV)
XLV = ["GILD", "MDT", "ABBV", "BMY"]

# Consumer Discretionary (XLY)
XLY = ["SBUX", "HD", "TGT", "F"]

# Real Estate (XLRE)
XLRE = ["O", "AMT", "EQIX", "SPG"]

# Ticker lists for each ETF
materials_tickers = ["APD", "NEM", "NUE", "FCX"]
communication_services_tickers = ["NFLX", "VZ", "ATVI", "DIS"]
energy_tickers = ["OXY", "PSX", "COP", "DVN"]
financials_tickers = ["BAC", "AXP", "CB", "C"]
industrials_tickers = ["LMT", "CAT", "UNP", "FDX"]
technology_tickers = ["ORCL", "CRM", "ADBE", "TXN"]
consumer_staples_tickers = ["GIS", "PG", "KO", "KR"]
utilities_tickers = ["EXC", "DUK", "EIX", "NEE"]
health_care_tickers = ["GILD", "MDT", "ABBV", "BMY"]
consumer_discretionary_tickers = ["SBUX", "HD", "TGT", "F"]
real_estate_tickers = ["O", "AMT", "EQIX", "SPG"]

# Mapping ETF symbols to ticker lists
etf_ticker_universe = {'xlb': materials_tickers, 'xlc': communication_services_tickers, 'xle': energy_tickers, 'xlf': financials_tickers, 'xli': industrials_tickers,
    'xlk': technology_tickers, 'xlp': consumer_staples_tickers, 'xlu': utilities_tickers, 'xlv': health_care_tickers, 'xly': consumer_discretionary_tickers,
    'xlre': real_estate_tickers}

tickers = [
    "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA", "NVDA", "JNJ", "JPM",
    "V", "PG", "UNH", "HD", "MA", "DIS", "PYPL", "NFLX", "ADBE", "KO",
    "PFE", "NKE", "PEP", "MRK", "CSCO", "ABT", "CRM", "AVGO", "CMCSA", "T",
    "XOM", "CVX", "WMT", "INTC", "AMD", "BA", "COST", "QCOM", "TXN", "ORCL",
    "MMM", "HON", "AMGN", "SPGI", "CAT", "GS", "MDT", "BLK", "USB", "LMT"]
