# Scrapy settings for spider project
#
# Professional-grade configuration for SidelineSignal V3 autonomous crawler
# Configured for live fire testing and production monitoring

BOT_NAME = "spider"

SPIDER_MODULES = ["spider.spiders"]
NEWSPIDER_MODULE = "spider.spiders"

ADDONS = {}

# Professional Logging Configuration
LOG_LEVEL = 'INFO'
LOG_FILE = '../scout.log'
LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'
LOG_DATEFORMAT = '%Y-%m-%d %H:%M:%S'

# Live Fire Test Configuration - 5 minute timeout
CLOSESPIDER_TIMEOUT = 300  # 300 seconds = 5 minutes

# Crawl responsibly by identifying yourself
USER_AGENT = "SidelineSignal-V3-Scout/1.0 (+https://github.com/elliotttmiller/SidelineSignal)"

# Obey robots.txt rules (disabled for streaming sites)
ROBOTSTXT_OBEY = False

# Concurrency and throttling settings optimized for streaming site discovery
CONCURRENT_REQUESTS = 5
CONCURRENT_REQUESTS_PER_DOMAIN = 2
DOWNLOAD_DELAY = 1
RANDOMIZE_DOWNLOAD_DELAY = 0.5

# Request retry configuration
RETRY_ENABLED = True
RETRY_TIMES = 2
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]

# Depth limit for focused crawling
DEPTH_LIMIT = 3

# Page count limit for testing
CLOSESPIDER_PAGECOUNT = 100

# Enable autothrottle for respectful crawling
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1
AUTOTHROTTLE_MAX_DELAY = 3
AUTOTHROTTLE_TARGET_CONCURRENCY = 2.0
AUTOTHROTTLE_DEBUG = False

# Disable telnet console
TELNETCONSOLE_ENABLED = False

# Default request headers
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
    "Accept-Encoding": "gzip, deflate",
    "Cache-Control": "no-cache",
}

# Downloader middlewares
DOWNLOADER_MIDDLEWARES = {
    "scrapy.downloadermiddlewares.retry.RetryMiddleware": 90,
    "scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware": 110,
}

# Enable stats collection
STATS_CLASS = 'scrapy.statscollectors.MemoryStatsCollector'

# Disable cookies for better crawling
COOKIES_ENABLED = False

# Feed export settings
FEED_EXPORT_ENCODING = "utf-8"

# Memory usage optimization
MEMUSAGE_ENABLED = True
MEMUSAGE_LIMIT_MB = 2048
MEMUSAGE_WARNING_MB = 1024

# Enable response caching for development
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"
