import pandas as pd

def rsi(data: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index."""
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple:
    """Moving Average Convergence Divergence."""
    exp1 = data.ewm(span=fast, adjust=False).mean()
    exp2 = data.ewm(span=slow, adjust=False).mean()
    macd_line = exp1 - exp2
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram

def ema(data: pd.Series, window: int) -> pd.Series:
    """Exponential Moving Average."""
    return data.ewm(span=window, adjust=False).mean()

def bollinger_bands(data: pd.Series, window: int = 20, num_std: int = 2) -> tuple:
    """Bollinger Bands."""
    sma = data.rolling(window=window).mean()
    std = data.rolling(window=window).std()
    upper_band = sma + (std * num_std)
    lower_band = sma - (std * num_std)
    return upper_band, sma, lower_band
