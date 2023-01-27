from datetime import datetime
from scrapy.parse import main
import asyncio


if __name__ == '__main__':
	start_time = datetime.now()
	print("Starting")
	asyncio.run(main())
	end_time = datetime.now()
	print("Duration: {}".format(end_time - start_time))
