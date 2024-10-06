#app/api/scheduler.py
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from vnexpress_scraper import scrape_vnexpress
from tuoitre_scraper import scrape_tuoitre
from vietnamnet_rss_scraper import scrape_vietnamnet_rss
from thanhnien_rss_scraper import scrape_thanhnien_rss
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Scheduler job definitions 
def job_vnexpress():
    logger.info("Running VNExpress scraper...")
    try:
        scrape_vnexpress()
        logger.info("VNExpress scraper completed.")
    except Exception as e:
        logger.exception("VNExpress scraper failed.")

def job_tuoitre():
    logger.info("Running Tuổi Trẻ scraper...")
    try:
        scrape_tuoitre()
        logger.info("Tuổi Trẻ scraper completed.")
    except Exception as e:
        logger.exception("Tuổi Trẻ scraper failed.")
        
def job_vietnamnet():
    logger.info("Running Vietnamnet scraper...")
    try:
        scrape_vietnamnet_rss()
        logger.info("Vietnamnet scraper completed.")
    except Exception as e:
        logger.exception("Vietnamnet scraper failed.")

def job_thanhnien():
    logger.info("Running Thanh Niên RSS...")
    try:
        scrape_thanhnien_rss()
        logger.info("Thanh Niên RSS completed.")
    except Exception as e:
        logger.exception("Thanh Niên RSS failed.")
        
if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # Schedule jobs
    scheduler.add_job(job_vnexpress, 'interval', minutes=3)
    scheduler.add_job(job_tuoitre, 'interval', minutes=3)
    scheduler.add_job(job_vietnamnet, 'interval', minutes=3)
    scheduler.add_job(job_thanhnien, 'interval', minutes=3)

    logger.info("Scheduler started. Press Ctrl+C to exit.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")
