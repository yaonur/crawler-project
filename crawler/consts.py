import os
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36'
HEADERS={
	"User-Agent":USER_AGENT
}
DB_URL=os.environ.get('DB_URL',"localhost:27017")

