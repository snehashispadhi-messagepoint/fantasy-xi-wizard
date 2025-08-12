import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.db.database import create_tables
from app.services.data_sync_service import data_sync_service
from app.core.config import settings

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI app startup and shutdown
    """
    # Startup
    logger.info("Starting up Fantasy XI Wizard API...")
    
    try:
        # Create database tables
        logger.info("Creating database tables...")
        create_tables()
        
        # Initial data sync if in debug mode
        if settings.DEBUG:
            logger.info("Debug mode: Starting initial data sync...")
            try:
                success = await data_sync_service.sync_all_data(force=False)
                if success:
                    logger.info("Initial data sync completed successfully")
                else:
                    logger.warning("Initial data sync failed, but continuing startup")
            except Exception as e:
                logger.error(f"Error during initial data sync: {e}")
                logger.warning("Continuing startup without initial sync")
        
        # Schedule periodic data sync (in production, this would be handled by a task queue)
        if not settings.DEBUG:
            logger.info("Production mode: Skipping automatic data sync")
            logger.info("Set up a cron job or task queue for periodic data synchronization")
        
        logger.info("Fantasy XI Wizard API startup completed")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        # Don't fail startup completely, but log the error
    
    yield
    
    # Shutdown
    logger.info("Shutting down Fantasy XI Wizard API...")
    # Add any cleanup tasks here
    logger.info("Shutdown completed")

async def sync_data_task():
    """
    Background task for periodic data synchronization
    This would typically be run by a task queue like Celery in production
    """
    while True:
        try:
            logger.info("Starting scheduled data sync...")
            success = await data_sync_service.sync_all_data(force=False)
            if success:
                logger.info("Scheduled data sync completed successfully")
            else:
                logger.error("Scheduled data sync failed")
        except Exception as e:
            logger.error(f"Error during scheduled data sync: {e}")
        
        # Wait for the next sync interval
        await asyncio.sleep(settings.DATA_REFRESH_INTERVAL_HOURS * 3600)

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('fantasy_xi_wizard.log') if not settings.DEBUG else logging.NullHandler()
        ]
    )
    
    # Set specific log levels for external libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    logger.info(f"Logging configured with level: {settings.LOG_LEVEL}")

def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application
    """
    setup_logging()

    app = FastAPI(
        title="Fantasy XI Wizard API",
        description="API for Fantasy Premier League analytics and AI recommendations",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        lifespan=lifespan
    )

    # Setup middleware
    from app.core.middleware import setup_middleware
    setup_middleware(app)

    return app
