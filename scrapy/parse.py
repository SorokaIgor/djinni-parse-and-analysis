import asyncio
from typing import Any, Coroutine
import httpx
import requests
from bs4 import BeautifulSoup
from cleantext import clean
from httpx import AsyncClient
from nltk import word_tokenize
from nltk.corpus import stopwords
import difflib
import re
from sqlalchemy.orm import exc
from modelsDb import Vacancy, Framework, session
from scrapy.config import *


def parse_pages_with_exp_filter(soup: BeautifulSoup) -> Coroutine:
    list_jobs = soup.select("div .profile")
    for link in list_jobs:
        list_of_all_vacancies.append(link["href"])
    try:
        if soup.select_one("li:last-child a.page-link")["href"] != "#":
            new_page = soup.select_one("li:last-child a.page-link")["href"]
            return parse_pages_with_exp_filter(make_page_soup(new_page))
    except TypeError:
        print("No more Pages found")


async def make_page_link(new_page: str, client: AsyncClient) -> requests:
    new_page_url = urljoin(FILTER_FOR_VACANCIES, new_page)
    new_page_response = await client.get(new_page_url)
    return new_page_response


def make_page_soup(new_page: str) -> BeautifulSoup:
    new_page_url = urljoin(FILTER_FOR_VACANCIES, new_page)
    new_page_response = requests.get(new_page_url)
    soup = BeautifulSoup(new_page_response.text, "html.parser")
    return soup


async def parse_everyone_vacancy(full_links_list: list):
    print("Prepare to starting parse_everyone_vacancy() function")
    async with httpx.AsyncClient(timeout=None) as client:
        page_response = await asyncio.gather(
            *[make_page_link(link, client) for link in full_links_list]
        )
        for response in page_response:
            page_soup = BeautifulSoup(response.text, "html.parser")
            frameworks = cleaning_text(page_soup)
            clear_vacancy_name = clean_vacancy_names(page_soup)
            experience_lvl = find_experience_lvl(page_soup)
            lvl = check_lvl(experience_lvl)
            views = find_views(page_soup)
            reviews = find_reviews(page_soup)
            print(response.url)
            vac = Vacancy(vacancy_name=clear_vacancy_name,
                          experience=experience_lvl,
                          lvl=lvl,
                          views=views,
                          applications=reviews,
                          part_of_url=str(response.url)
                          )
            session.add(vac)
            try:
                for fr in frameworks:
                    print(f"THIS IS <<{fr}>> WORD")
                    if len(fr) == 0:
                        print("No frameworks")
                    else:
                        a = session.query(Framework).filter_by(framework_name=fr)
                        if session.query(a.exists()).scalar():
                            a = session.query(Framework).filter_by(framework_name=fr).first()
                            vac.frameworks.append(a)
                        else:
                            vac.frameworks.append(Framework(framework_name=fr))
            except exc.FlushError:
                    session.rollback()
                    continue
            session.add(vac)
            session.commit()


def check_lvl(exp_lvl: int) -> str:
    if exp_lvl == 0 or exp_lvl == 1:
        return "junior"
    elif exp_lvl == 2:
        return "middle"
    elif exp_lvl == 3:
        return "middle/senior"
    elif exp_lvl == 5:
        return "senior"


def find_experience_lvl(page_soup: BeautifulSoup) -> int:
    find_exp = page_soup.find("ul", class_="job-additional-info--body").text.split()[-4]
    clean_exp_field = re.sub(r"([!@#$:,-])", "r", find_exp)
    if clean_exp_field.isalpha():
        clean_exp_field = 0
    print(clean_exp_field)
    return int(clean_exp_field)


def find_views(page_soup: BeautifulSoup) -> int:
    find_view = page_soup.find("p", class_="text-muted").text.split()[-4]
    return int(find_view)


def find_reviews(page_soup: BeautifulSoup) -> int:
    search_reviews = page_soup.find("p", class_="text-muted").text.split()[-2]
    return int(search_reviews)


def clean_vacancy_names(page_soup: BeautifulSoup) -> str:
    vacancy_name = page_soup.select_one("h1").get_text(" ").replace("/", " ")
    vacancy_name = list(
        set(re.sub(r"([^\x00-\x7f])|([!@#$-])|([0-9]+)", r"", vacancy_name).split())
    )
    clean_vac_name = [
        difflib.get_close_matches(i.lower(), python_vacancies, cutoff=0.7)
        for i in vacancy_name
    ]
    open_lists = []
    for i in clean_vac_name:
        if len(i) != 0:
            i = set(i)
            open_lists.append(*i)
    open_lists.sort()
    if len(open_lists) == 0:
        open_lists.append("developer")
    join_lists = " ".join(open_lists)
    return join_lists


def cleaning_text(text_soup: Any) -> [str]:
    text = text_soup.find_all("div", class_="profile-page-section")
    finished_joined_text = ""
    for tag in text:
        tag_text = tag.get_text(separator="/")
        clean_text = clean(
            text=tag_text, punct=False, lowercase=True, numbers=False
        ).replace("/", " ")
        clean_text = re.sub(
            r"(@\[A-Za-z0-9]+)|([^0-9A-Za-z \t])|^rt|http.+?", "", clean_text
        )
        finished_joined_text += clean_text
    tokens = word_tokenize(finished_joined_text)
    stop_words = set(stopwords.words("english"))
    keywords = [
        word.lower() for word in tokens if word.isalpha() and word not in stop_words
    ]
    return list(set(keywords).intersection(set(python_frameworks)))


def parse_all_vacancies_links(exp_filter: list):
    for exp in exp_filter:
        new_page = requests.get(FILTER_FOR_VACANCIES + BASE_PYTHON_URL + exp)
        soup = BeautifulSoup(new_page.text, "html.parser")
        parse_pages_with_exp_filter(soup)


async def main():
    print("Program starting...")
    print("Start parsing all links from vacancies")
    parse_all_vacancies_links(EXP_FILTERS)
    print(f"{len(list_of_all_vacancies)} founded")
    print("Start parsing everyone vacancy")
    await parse_everyone_vacancy(list_of_all_vacancies)
    print(f"{len(list_of_all_vacancies)}")
