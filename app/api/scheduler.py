from apscheduler.schedulers.blocking import BlockingScheduler
from techcrunch_scraper import scrape_techcrunch
from guardian_scraper import scrape_guardian
from reuters_scraper import scrape_reuters

def job_techcrunch():
    print("Running TechCrunch scraper...")
    scrape_techcrunch()

def job_guardian():
    print("Running Guardian scraper...")
    scrape_guardian()

def job_reuters():
    print("Running Reuters scraper...")
    scrape_reuters()

if __name__ == "__main__":
    scheduler = BlockingScheduler()

    # Schedule the TechCrunch scraper to run every 12 hours
    scheduler.add_job(job_techcrunch, 'interval', minutes=1)

    # Schedule the Guardian scraper to run every 12 hours
    scheduler.add_job(job_guardian, 'interval', hours=12)

    # Schedule the Reuters scraper to run every 12 hours
    scheduler.add_job(job_reuters, 'interval', hours=12)

    print("Scheduler started. Press Ctrl+C to exit.")
    scheduler.start()
