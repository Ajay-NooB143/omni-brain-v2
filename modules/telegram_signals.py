import logging

logger = logging.getLogger(__name__)


def send_signal(telegram_user_id, signal, delay=0):
    """Placeholder: send signal to Telegram user"""
    logger.info(f"Signal to {telegram_user_id}: {signal.get('pair')} {signal.get('verdict')} (delay={delay}s)")
    return True
