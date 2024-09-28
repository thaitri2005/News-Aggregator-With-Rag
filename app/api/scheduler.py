# app/api/scheduler.py
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from techcrunch_scraper import scrape_techcrunch
from ycombinator_scraper import scrape_ycombinator
from theverge_scraper import scrape_theverge
from vnexpress_scraper import scrape_vnexpress
import time

# Set up logging
logger = logging.getLogger(__name__)


# Scheduler job definitions
def job_techcrunch():
    logger.info("Running TechCrunch scraper...")
    try:
        scrape_techcrunch()
        logger.info("TechCrunch scraper completed.")
    except Exception as e:
        logger.exception("TechCrunch scraper failed.")

def job_ycombinator():
    logger.info("Running YCombinator scraper...")
    try:
        scrape_ycombinator()
        logger.info("YCombinator scraper completed.")
    except Exception as e:
        logger.exception("YCombinator scraper failed.")

def job_theverge():
    logger.info("Running The Verge scraper...")
    try:
        scrape_theverge()
        logger.info("The Verge scraper completed.")
    except Exception as e:
        logger.exception("The Verge scraper failed.")
        
def job_vnexpress():
    logger.info("Running VNExpress scraper...")
    try:
        scrape_vnexpress()
        logger.info("VNExpress scraper completed.")
    except Exception as e:
        logger.exception("VNExpress scraper failed.")

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # scheduler.add_job(job_techcrunch, 'interval', minutes=2)
    # scheduler.add_job(job_ycombinator, 'interval', minutes=2)
    # scheduler.add_job(job_theverge, 'interval', minutes=2)
    scheduler.add_job(job_vnexpress, 'interval', minutes=3)

    logger.info("Scheduler started. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
