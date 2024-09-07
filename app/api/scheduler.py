import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from techcrunch_scraper import scrape_techcrunch
# from guardian_scraper import scrape_guardian
# from reuters_scraper import scrape_reuters
from ycombinator_scraper import scrape_ycombinator
from theverge_scraper import scrape_theverge
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Delay start of scheduler tasks
time.sleep(10)

# Scheduler job definitions go here
def job_techcrunch():
    logger.info("Running TechCrunch scraper...")
    scrape_techcrunch()

# def job_guardian():
#     logger.info("Running Guardian scraper...")
#     scrape_guardian()

# def job_reuters():
#     logger.info("Running Reuters scraper...")
#     scrape_reuters()
    
def job_ycombinator():
    logger.info("Running YCombinator scraper...")
    scrape_ycombinator()
    
def job_theverge():
    logger.info("Running The Verge scraper...")
    scrape_theverge()

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    scheduler.add_job(job_techcrunch, 'interval', minutes=2)
    # scheduler.add_job(job_guardian, 'interval', minutes=1)
    # scheduler.add_job(job_reuters, 'interval', minutes=1)
    scheduler.add_job(job_ycombinator, 'interval', minutes=2)
    scheduler.add_job(job_theverge, 'interval', minutes=2)

    logger.info("Scheduler started. Press Ctrl+C to exit.")
    scheduler.start()
