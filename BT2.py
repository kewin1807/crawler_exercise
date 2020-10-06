import bs4
import pandas as pd
import lxml.html as lh

import requests
import re
import chardet
USERNAME = "**************"
PASSWORD = "*************"

URL_LOGIN = "https://connect.appen.com/qrp/core/login"
URL = "https://connect.appen.com/qrp/core/vendors/shasta_feedbacks?list=&ajax=true"

headers = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"
}
payload = {
    "username": USERNAME,
    "password": PASSWORD,
    "ruri": "",
    "timeZoneIdentifier": "Asia/Saigon",
    "code": "",
    "login": "Login",
}


def get_page_content(session):
    r = session.get(
        URL, headers=headers)
    soup = bs4.BeautifulSoup(r.content)
    data = {}
    data["project.id"] = 40
    data["criteria.direction2"] = "asc"
    data["criteria.rowsPerPage"] = 100
    data["criteria.column2"] = "ia.trainingTaskAnswer.trainingTask.query"
    data["criteria.page"] = 1
    data["criteria.column"] = "ia.trainingTaskItem.trainingTask.goldenSet"
    data["criteria.direction"] = "desc"
    data["reviewId"] = ""
    data["posted"] = True
    data["type"] = "map_search2"
    data["search"] = ""
    data["_sourcePage"] = soup.find(
        "input", attrs={"name": "_sourcePage"})["value"]
    data["__fp"] = soup.find("input", attrs={"name": "__fp"})["value"]

    r = session.post(URL, data=data, headers=headers)
    content = r.content.decode(r.encoding)
    doc = lh.fromstring(content)
    thead_elments = doc.xpath("//thead")
    tr_elements = doc.xpath('//tr')
    col = []
    i = 0
    # get title from table
    titles = []
    for t in thead_elments[0]:

        name = t.text_content()
        if name.find("Set") != -1:
            name = "Set"
        name = re.sub(
            '[^a-zA-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßàáâãäåæçèéêëìíîïðñòóôõö÷øùúûüýþÿıŒœŠšŸŽž0-9 ]', '', name)
        titles.append(name)

    # create object result
    objectResult = {}
    for title in titles:
        objectResult[title] = []

    for tr in tr_elements:
        for (t, title) in zip(tr, titles):
            value = t.text_content()

            objectResult[title].append(value)
    df = pd.DataFrame(objectResult)
    return df


def main():

    with requests.Session() as session:
        r = session.get(
            URL_LOGIN, headers=headers)
        soup = bs4.BeautifulSoup(r.content)

        payload["_sourcePage"] = soup.find(
            "input", attrs={"name": "_sourcePage"})["value"]
        payload["__fp"] = soup.find("input", attrs={"name": "__fp"})["value"]

        login_result = session.post(URL_LOGIN, data=payload, headers=headers)
        df = get_page_content(session)
        df.to_csv("test.csv")


if __name__ == "__main__":
    main()
