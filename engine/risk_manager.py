class RiskManager:
    """Handles risk validation for orders."""
    
    def __init__(self, max_position_size_pct: float = 0.1, stop_loss_pct: float = 0.05, max_drawdown_pct: float = 0.05):
        self.max_position_size_pct = max_position_size_pct  # Fraction of total balance
        self.stop_loss_pct = stop_loss_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.initial_balance = None

    def validate_order(self, signal: str, balance: float, current_price: float) -> tuple[bool, float, str]:
        """
        Validate if the signal meets risk management criteria.
        Returns (is_safe, amount, message).
        """
        if self.initial_balance is None:
            self.initial_balance = balance

        if signal == 'hold':
            return False, 0.0, "Signal is HOLD"
            
        if balance <= 0:
            return False, 0.0, "Insufficient balance"
            
        if self.check_circuit_breaker(balance):
            return False, 0.0, f"Circuit Breaker Triggered: Total drawdown > {self.max_drawdown_pct*100}%"
            
        amount = self.calculate_position_size(balance, current_price)
        return True, amount, "Risk checks passed"

    def check_circuit_breaker(self, current_balance: float) -> bool:
        """Returns True if the circuit breaker should be triggered."""
        if self.initial_balance and current_balance < self.initial_balance * (1 - self.max_drawdown_pct):
            return True
        return False

    def calculate_position_size(self, balance: float, current_price: float) -> float:
        """Calculate the amount to buy/sell based on risk rules."""
        return (balance * self.max_position_size_pct) / current_price
