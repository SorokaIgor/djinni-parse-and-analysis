from bs4 import BeautifulSoup
from httpx import get

URL = "https://djinni.co/jobs/359059-odoo-developer-middle-senior-/"

response = get(URL)

soup = BeautifulSoup(response.content, "html.parser")

find_exp = soup.select_one("ul.job-additional-info--body li:last-child div.job-additional-info--item-text").get_text().strip()

if find_exp.split()[0].isdigit():
	print(type(find_exp.split()[0]))
else:
	print("0")