from datetime import datetime

from modelsDb import session
from scrapy.parse import main
from nltk import download
import asyncio


if __name__ == '__main__':
	download("punkt")
	start_time = datetime.now()
	print("Starting")
	asyncio.run(main())
	session.close()
	end_time = datetime.now()
	print("Duration: {}".format(end_time - start_time))
