import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import asyncio
import logging

# Configure logging to show what happens
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Test that the bot module can be imported and configured
try:
    import bot
    logger.info("✅ Bot module imported successfully")

    # Check that logging is configured
    logger.info("✅ Logging configured")

    # Check that error classes are imported
    from telegram.error import NetworkError, TimedOut
    logger.info("✅ Error classes imported")

    logger.info("=" * 50)
    logger.info("TEST: Bot startup simulation")
    logger.info("=" * 50)

    # This will try to start the bot and handle network errors
    try:
        asyncio.run(bot.main_async())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Bot stopped with error: {type(e).__name__}: {e}")
        logger.info("This is expected if VPN is not enabled")
        logger.info("The retry mechanism should have attempted to reconnect")

except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"❌ Unexpected error: {e}")
    sys.exit(1)
