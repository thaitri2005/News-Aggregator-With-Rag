import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from techcrunch_scraper import scrape_techcrunch
from ycombinator_scraper import scrape_ycombinator
from theverge_scraper import scrape_theverge
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Delay start of scheduler tasks
time.sleep(5)

# Scheduler job definitions
def job_techcrunch():
    logger.info("Running TechCrunch scraper...")
    scrape_techcrunch()
    
def job_ycombinator():
    logger.info("Running YCombinator scraper...")
    scrape_ycombinator()
    
def job_theverge():
    logger.info("Running The Verge scraper...")
    scrape_theverge()

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    scheduler.add_job(job_techcrunch, 'interval', minutes=2)
    scheduler.add_job(job_ycombinator, 'interval', minutes=2)
    scheduler.add_job(job_theverge, 'interval', minutes=2)

    logger.info("Scheduler started. Press Ctrl+C to exit.")
    scheduler.start()
