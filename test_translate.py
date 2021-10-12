from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import JavascriptException

# local variables
from selenium.webdriver.chrome.options import Options as ChromeOptions
chrome_op = ChromeOptions()
chrome_op.add_argument('--incognito')
browser = webdriver.Chrome(
    executable_path='chromedriver/chromedriver', options=chrome_op)


def makeCall(url, script, default):
    response = default
    try:
        browser.get(url)
        while(response == default):
            response = browser.execute_script(script)
            print(response)

    except JavascriptException:
        print(JavascriptException.args)

    except NoSuchElementException:
        print(NoSuchElementException.args)

    if(response != default):
        return response
    else:
        return 'Not Available'


def googleTranslate(src, trg, phrase):
    url = 'https://translate.google.com/#view=home&op=translate&sl=' + \
        src + '&tl=' + trg+'&text='+phrase
    script = 'return document.getElementsByClassName("tlid-translation")[0].textContent'
    return makeCall(url, script, None)


if __name__ == "__main__":
    src = "vi"
    trg = "en"
    phrase = "Ở trận đấu diễn ra muộn hơn, Valencia tiếp tục cho thấy màn trình diễn nghèo nàn của mình khi nhận thất bại tan nát 0-4 trên sân nhà Mestalla trước Eibar. Trận thua này khiến “Bầy dơi” tiếp tục dậm chân ở vị trí thứ 16 trên BXH."
    print("\nResult: ", googleTranslate(src, trg, phrase))
