"""OmniBrainV2 Orchestrator - lte_v35_v2.py
Integrates all modules: confidence scoring, MTF, risk, sentiment, correlation
"""
import logging
from datetime import datetime

from core.confidence_scorer import calculate_confidence, get_signal
from core.mtf_confirmation import mtf_confirmation_full
from core.risk_manager import (
    calculate_position_size,
    calculate_dynamic_grid,
    calculate_stop_loss,
    calculate_take_profit,
)
from modules.sentiment_engine import forex_sentiment_analyzer
from modules.correlation_engine import detect_correlation_breakdown

# Setup logging
logging.basicConfig(
    filename='omni_brain_v2.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


class OmniBrainV2:
    """Main trading orchestrator."""

    def __init__(self, account_balance=10000, risk_percent=1.0, max_daily_loss=5.0):
        """
        Initialize OMNI BRAIN V2.

        Args:
            account_balance (float): Starting account balance in USD
            risk_percent (float): Risk per trade (%)
            max_daily_loss (float): Max daily loss before circuit breaker (%)
        """
        self.account_balance = account_balance
        self.risk_percent = risk_percent
        self.max_daily_loss = max_daily_loss

        self.live_pairs = ['XAUUSD', 'EURUSD', 'GBPUSD', 'SP500', 'BTC']
        self.open_trades = []
        self.closed_trades = []
        self.daily_pl = 0

        logger.info(
            f"OmniBrainV2 initialized: Account=${account_balance}, Risk={risk_percent}%"
        )

    def scan_and_execute(self, market_data):
        """
        Main scan loop: check all pairs, execute signals.

        Args:
            market_data (dict): {pair: {d1: [...], h1: [...], m15: [...]}}

        Returns:
            dict: Execution summary
        """
        execution_log = {
            'timestamp': datetime.now().isoformat(),
            'pairs_scanned': 0,
            'signals_found': 0,
            'trades_opened': 0,
            'trades_blocked': 0,
            'details': [],
        }

        for pair in self.live_pairs:
            if pair not in market_data:
                continue

            execution_log['pairs_scanned'] += 1

            try:
                d1_data = market_data[pair].get('d1', {})
                h1_data = market_data[pair].get('h1', {})
                m15_data = market_data[pair].get('m15', {})

                # MTF confirmation
                mtf_result = mtf_confirmation_full(d1_data, h1_data, m15_data, pair)

                if mtf_result['mtf_status'] != 'CONFIRMED':
                    execution_log['trades_blocked'] += 1
                    continue

                execution_log['signals_found'] += 1

                # Calculate confidence
                confidence = calculate_confidence(
                    ob=20,
                    fvg=15,
                    sweep=25,
                    vwap=12,
                    session=10,
                    corr=12,
                    yield_=8,
                    sentiment=7,
                    pattern=18,
                    divergence=16,
                )

                signal = get_signal(confidence['confidence'])

                if signal != 'EXECUTE':
                    execution_log['trades_blocked'] += 1
                    continue

                # Check sentiment
                sentiment = forex_sentiment_analyzer(
                    pair=pair,
                    news_articles=[],
                    social_signals={},
                    macro_events=[],
                )

                # Risk management
                entry_price = m15_data.get('close', [0])[-1]
                stop_loss = entry_price * 0.99  # Placeholder

                position = calculate_position_size(
                    account_balance=self.account_balance,
                    risk_percent=self.risk_percent,
                    entry_price=entry_price,
                    stop_loss=stop_loss,
                )

                grid = calculate_dynamic_grid(
                    confidence=confidence['confidence'],
                    market_weather='SUNNY',
                    account_risk=self.account_balance * self.risk_percent / 100,
                    portfolio_dd=0.0,
                )

                if grid['action'] != 'EXECUTE':
                    execution_log['trades_blocked'] += 1
                    continue

                # Execute trade
                trade = {
                    'trade_id': len(self.open_trades) + 1,
                    'pair': pair,
                    'timestamp': datetime.now().isoformat(),
                    'entry_price': entry_price,
                    'size': position['lots'],
                    'direction': (
                        'LONG' if mtf_result['d1_bias']['direction'] == 'BULLISH' else 'SHORT'
                    ),
                    'confidence': confidence['confidence'],
                    'sentiment': sentiment['composite_sentiment'],
                    'mtf_confluence': mtf_result['overall_confluence'],
                    'stop_loss': None,
                    'take_profit': None,
                }

                self.open_trades.append(trade)
                execution_log['trades_opened'] += 1

                execution_log['details'].append({
                    'pair': pair,
                    'signal': signal,
                    'confidence': confidence['confidence'],
                    'entry': trade['entry_price'],
                    'size': trade['size'],
                    'status': 'EXECUTED',
                })

                logger.info(
                    f"TRADE OPENED: {pair} @ {trade['entry_price']:.4f}, "
                    f"Size {trade['size']} lots, Confidence {confidence['confidence']:.0f}"
                )

            except Exception as e:
                logger.error(f"Error scanning {pair}: {str(e)}")
                execution_log['details'].append({
                    'pair': pair,
                    'error': str(e),
                    'status': 'ERROR',
                })

        return execution_log

    def update_open_trades(self, market_data):
        """
        Update open trades: check SL/TP, manage partial exits.

        Args:
            market_data (dict): Current market data

        Returns:
            dict: Trade management summary
        """
        update_log = {
            'timestamp': datetime.now().isoformat(),
            'trades_updated': 0,
            'trades_closed': 0,
            'partial_exits': 0,
        }

        for trade in self.open_trades[:]:
            pair = trade['pair']

            if pair not in market_data:
                continue

            current_price = market_data[pair].get('m15', {}).get('close', [0])[-1]

            # Check stop loss
            if trade['stop_loss'] and (
                (trade['direction'] == 'LONG' and current_price < trade['stop_loss'])
                or (trade['direction'] == 'SHORT' and current_price > trade['stop_loss'])
            ):
                self._close_trade(trade, current_price, 'STOP_LOSS')
                update_log['trades_closed'] += 1
                continue

            # Check take profit
            if trade['take_profit'] and (
                (trade['direction'] == 'LONG' and current_price > trade['take_profit'])
                or (trade['direction'] == 'SHORT' and current_price < trade['take_profit'])
            ):
                self._close_trade(trade, current_price, 'TAKE_PROFIT')
                update_log['trades_closed'] += 1
                continue

            update_log['trades_updated'] += 1

        return update_log

    def _close_trade(self, trade, close_price, close_reason):
        """
        Close a trade.

        Args:
            trade (dict): Trade to close
            close_price (float): Close price
            close_reason (str): Reason for closure
        """
        profit = (close_price - trade['entry_price']) * trade['size']
        if trade['direction'] == 'SHORT':
            profit = -profit

        trade['close_price'] = close_price
        trade['close_reason'] = close_reason
        trade['profit_loss'] = profit
        trade['close_timestamp'] = datetime.now().isoformat()

        self.open_trades.remove(trade)
        self.closed_trades.append(trade)
        self.daily_pl += profit

        logger.info(
            f"TRADE CLOSED: {trade['pair']} @ {close_price:.4f}, "
            f"P&L ${profit:.2f} ({close_reason})"
        )

    def get_statistics(self):
        """Get trading statistics."""
        if not self.closed_trades:
            return {
                'trades': 0,
                'wins': 0,
                'losses': 0,
                'win_rate': 0,
                'avg_profit': 0,
                'avg_loss': 0,
            }

        wins = [t for t in self.closed_trades if t['profit_loss'] > 0]
        losses = [t for t in self.closed_trades if t['profit_loss'] < 0]

        win_rate = len(wins) / len(self.closed_trades) * 100
        avg_profit = (
            sum(t['profit_loss'] for t in wins) / len(wins) if wins else 0
        )
        avg_loss = (
            sum(t['profit_loss'] for t in losses) / len(losses) if losses else 0
        )

        return {
            'total_trades': len(self.closed_trades),
            'wins': len(wins),
            'losses': len(losses),
            'win_rate': f'{win_rate:.1f}%',
            'avg_profit': f'${avg_profit:.2f}',
            'avg_loss': f'${avg_loss:.2f}',
            'daily_pl': f'${self.daily_pl:.2f}',
            'open_trades': len(self.open_trades),
        }


# Example usage
if __name__ == "__main__":
    bot = OmniBrainV2(account_balance=10000, risk_percent=1.0)

    # Mock market data
    mock_data = {
        'EURUSD': {
            'd1': {
                'close': [1.0900, 1.0920, 1.0950],
                'vwap': [1.0910, 1.0930, 1.0945],
                'rsi': [55, 60, 65],
                'structure': {'trend': 'up'},
            },
            'h1': {
                'close': [1.0945, 1.0948, 1.0950],
                'structure': {'trend': 'up'},
                'order_block': {'high': 1.0960, 'low': 1.0930},
            },
            'm15': {
                'close': [1.0948, 1.0949, 1.0950],
                'vwap': [1.0945, 1.0946, 1.0947],
                'rsi': [55, 58, 60],
            },
        }
    }

    # Scan market
    result = bot.scan_and_execute(mock_data)
    print(f"Execution: {result['trades_opened']} trades opened, {result['trades_blocked']} blocked")

    # Get stats
    stats = bot.get_statistics()
    print(f"Stats: {stats}")
