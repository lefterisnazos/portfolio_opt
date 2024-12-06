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

# "BRK.B" stock was problematic, and was messing up hrp.
tickers = [
    "NVDA", "AAPL", "MSFT", "AMZN", "GOOGL", "GOOG", "META", "TSLA", "AVGO",
    "WMT", "JPM", "LLY", "V", "UNH", "XOM", "MA", "COST", "HD", "PG",
    "NFLX", "JNJ", "CRM", "BAC", "ABBV", "CVX", "TMUS", "KO", "MRK", "WFC",
    "BX", "CSCO", "ADBE", "ACN", "AMD", "PEP", "NOW", "MS", "LIN", "AXP",
    "DIS", "IBM", "TXN", "PFE", "TMO", "C", "INTU", "PM", "BMY", "GS",
    "QCOM", "BKNG", "DHR", "CMCSA", "T", "RTX", "BLK", "SPGI", "AMGN", "UNP",
    "HON", "MDT", "CAT", "COP", "SLB", "GE", "SBUX", "CHTR", "MDLZ", "CL",
    "GM", "F", "MMM", "TGT", "LMT", "NOC", "RTX", "BA", "DAL", "LUV",
    "AAL", "UAL", "MAR", "HLT", "MCD", "YUM", "CMG", "DPZ", "DRI", "BBY",
    "LOW", "TJX", "ROST", "DG", "DLTR", "AZO", "ORLY", "AAP", "KMX", "TSLA", 'ORCL', 'INTC', 'AEP']

# tickers = ['SPGI', 'BKNG', 'LUV', 'PCAR', 'SHW', 'CPT', 'CVX', 'SWK', 'TXT', 'MSFT', 'TRV', 'ZBRA', 'QRVO',
#            'ANSS', 'NI', 'ATO', 'PAYC', 'ALLE', 'PWR', 'PHM', 'SYY', 'IR', 'SNPS', 'HON', 'HPQ', 'BF-B', 'BG',
#            'DAL', 'PEP', 'KHC', 'AMAT', 'ICE', 'VLO', 'COST', 'EVRG', 'ENPH', 'NSC', 'BKR', 'SRE', 'ADBE', 'GLW',
#            'CMG', 'PH', 'TPR', 'J', 'JPM', 'ROK', 'EXPE', 'WMB', 'ADI', 'TSCO', 'HD', 'STX', 'ALB', 'IPG', 'CBOE',
#            'YUM', 'VZ', 'RTX', 'ADSK', 'MDT', 'KEYS', 'PM', 'DTE', 'CSGP', 'EG', 'HRL', 'BEN', 'MGM', 'MA', 'AJG',
#            'CTLT', 'DELL', 'USB', 'WEC', 'NWS', 'DAY', 'C', 'SLB',
#            'MAR', 'DXCM', 'CHTR', 'AMD', 'PGR', 'AMT', 'CVS', 'ROST', 'BALL',
#            'JNJ', 'MSI', 'AZO', 'PANW', 'EFX', 'PKG', 'COP', 'ZBH', 'CL', 'OKE','L','TDY']

polygon_api_key ='LTLVSbi7rBjyjJtCpmLuTDPPhFsNSCyy'