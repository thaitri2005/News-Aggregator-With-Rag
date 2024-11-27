# app/api/scheduler.py
from api.scrapers.vnexpress_scraper import scrape_vnexpress
from api.scrapers.vietnamnet_rss_scraper import scrape_vietnamnet_rss
from api.scrapers.tuoitre_scraper import scrape_tuoitre
from api.scrapers.thanhnien_rss_scraper import scrape_thanhnien_rss

from apscheduler.schedulers.blocking import BlockingScheduler
import logging

logger = logging.getLogger(__name__)

def schedule_jobs():
    scheduler = BlockingScheduler()

    scheduler.add_job(scrape_vnexpress, 'interval', minutes=3, id="vnexpress_scraper")
    scheduler.add_job(scrape_vietnamnet_rss, 'interval', minutes=3, id="vietnamnet_scraper")
    scheduler.add_job(scrape_tuoitre, 'interval', minutes=3, id="tuoitre_scraper")
    scheduler.add_job(scrape_thanhnien_rss, 'interval', minutes=3, id="thanhnien_scraper")

    logger.info("Scheduled jobs started.")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped.")

if __name__ == "__main__":
    schedule_jobs()