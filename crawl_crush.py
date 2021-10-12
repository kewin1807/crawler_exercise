from lxml import html
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
from tkinter.ttk import Frame, Label, Entry, Button
from tkinter import Tk, Text, TOP, BOTH, X, N, LEFT, RIGHT
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time


def process_background(style):
    color = style.split(":")[1].strip()
    if color == "rgb(80, 124, 209)":
        return "background-color: #507cd1"
    elif color.lower() == "violet":
        return "background-color: #ac50d1"
    elif color.lower() == "green":
        return "background-color: #008000"
    elif color.lower() == "white":
        return "background-color: #ffffff"
    return style


def extractTableToExcel(table, fileExcel, sheetname):
    rows = table.find_elements(By.TAG_NAME, "tr")
    styles = []
    titles = []
    html = "<table>" + table.get_attribute("innerHTML") + "</table>"

    def row_style(row):
        return styles[row.name]
    objectResult = {}
    for (index, row) in enumerate(rows):
        if row.get_attribute("class") == "GridFooter" or row.get_attribute("class") == "GridPaging":
            break
        cols = row.find_elements(By.TAG_NAME, "td")
        style = row.get_attribute("style").split(";")[1].strip()
        arr_style = [process_background(style) for i in range(len(cols))]
        styles.append(arr_style)

    df = pd.read_html(html)[0]

    df = df.drop([len(df)-1, len(df)-2])
    df = df.style.apply(row_style, axis=1)
    df.to_excel(fileExcel, sheet_name=sheetname)


class SimpleDialog(Frame):

    def __init__(self, browser):
        super().__init__()
        # self allow the variable to be used anywhere in the class
        self.output1 = ""
        self.output2 = ""
        self.output3 = ""
        self.initUI()
        self.browser = browser

    def initUI(self):

        self.master.title("Nhập thông tin doanh nghiệp")
        self.pack(fill=BOTH, expand=True)

        frame1 = Frame(self)
        frame1.pack(fill=X)

        lbl1 = Label(frame1, text="Mã số doanh nghiệp", width=15)
        lbl1.pack(side=LEFT, padx=5, pady=10)

        self.entry1 = Entry(frame1, textvariable=self.output1)
        self.entry1.pack(fill=X, padx=5, expand=True)

        frame2 = Frame(self)
        frame2.pack(fill=X)

        lbl2 = Label(frame2, text="Số cmt", width=15)
        lbl2.pack(side=LEFT, padx=5, pady=10)

        self.entry2 = Entry(frame2)
        self.entry2.pack(fill=X, padx=5, expand=True)

        frame3 = Frame(self)
        frame3.pack(fill=X)

        lbl3 = Label(frame3, text="Nhập số captcha", width=15)
        lbl3.pack(side=LEFT, padx=5, pady=10)

        self.entry3 = Entry(frame3)
        self.entry3.pack(fill=X, padx=5, expand=True)

        frame4 = Frame(self)
        frame4.pack(fill=X)

        # Command tells the form what to do when the button is clicked
        btn = Button(frame4, text="Submit", command=self.onSubmit)
        btn.pack(padx=5, pady=10)

    def onSubmit(self):
        self.output1 = self.entry1.get()
        self.output2 = self.entry2.get()
        self.output3 = self.entry3.get()
        bussinessId = browser.find_element_by_id(
            "ctl00_m_g_ed53fbc5_ced8_4002_b05c_81e3422b5262_ctl00_txtMa_DV")
        cmtID = browser.find_element_by_id(
            "ctl00_m_g_ed53fbc5_ced8_4002_b05c_81e3422b5262_ctl00_txtSoCMT")
        captchaID = browser.find_element_by_id(
            "ctl00_m_g_ed53fbc5_ced8_4002_b05c_81e3422b5262_ctl00_txtCaptcha")
        # clear value of element HTML attribute
        cmtID.clear()
        bussinessId.clear()
        captchaID.clear()

        cmtID.send_keys(self.entry2.get())
        bussinessId.send_keys(self.entry1.get())
        captchaID.send_keys(self.output3)
        paging_index = 0
        correct_pagging = 1
        check_break = True
        file_excel = pd.ExcelWriter("test.xlsx", engine="xlsxwriter")
        browser.find_element_by_id(
            'ctl00_m_g_ed53fbc5_ced8_4002_b05c_81e3422b5262_ctl00_btnSubmit').click()

        try:
            start_time = time.time()
            tableElement = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located(
                    (By.ID, "ctl00_m_g_ed53fbc5_ced8_4002_b05c_81e3422b5262_ctl00_grdDS"))
            )

            extractTableToExcel(tableElement, file_excel, "sheetname_1")
            paging_index += 1
            correct_pagging += 1
            max_value_page = correct_pagging
            while(check_break):
                print("process: ", correct_pagging)
                paging_part_element = tableElement.find_element_by_css_selector(
                    'tr.GridPaging').find_elements(By.TAG_NAME, "td")[0]
                paging_elements = paging_part_element.find_elements(
                    By.XPATH, "*")

                if(paging_elements[paging_index].text == "..." and paging_index == 0):
                    indexs = [i for i in range(len(
                        paging_elements)) if paging_elements[i].text != "..." and int(paging_elements[i].text) >= correct_pagging]
                    print(indexs)
                    if len(indexs) == 0:
                        continue
                    min_index = min(indexs)
                    paging_index = min_index
                    continue

                value = paging_elements[paging_index].text
                print("paging_index: ", paging_index)
                print("link: ", value)
                paging_elements[paging_index].click()
                tableElement = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                        (By.ID, "ctl00_m_g_ed53fbc5_ced8_4002_b05c_81e3422b5262_ctl00_grdDS")))
                extractTableToExcel(tableElement, file_excel,
                                    "sheetname_{}".format(correct_pagging))
                correct_pagging += 1
                if(paging_index == len(paging_elements)-1):
                    if value == "...":
                        paging_index = 0
                    else:
                        check_break = False
                    continue
                paging_index += 1

                # print(paging_index)
                # pagings = tableElement.find_element_by_css_selector(
                #     'tr.GridPaging').find_elements(By.TAG_NAME, "td")[0].find_element(By.partialLinkText(str(correct_pagging)))
                # print("length of pagings: ", len(pagings))

                # # print(pagings[paging_index].text)
                # if pagings[paging_index].tag_name == "a":
                #     pagings[paging_index].click()

                # )
                # extractTableToExcel(tableElement, file_excel,
                #                     "sheetname_{}".format(correct_pagging))

                # # max_page = max([p.text for p in pagings if p.])
                # if(paging_index == len(pagings)-1):
                #     print(pagings[len(pagings)-1])
                #     value_link = pagings[len(pagings)-1].get_attribute('text')
                #     print("value_link", value_link)
                #     if value_link == "...":
                #         paging_index = 0
                #     else:
                #         check_break = False
                # paging_index += 1
                # correct_pagging += 1
            end_time = time.time()
            file_excel.save()
            file_excel.close()
            print("processing time: ", end_time-start_time)

            # df.to_excel("output.xlsx",
            #             sheet_name='Sheet_name_1')

        finally:
            print("done")
            # browser.quit()
        self.quit()


if __name__ == '__main__':
    url = 'https://www.customs.gov.vn/SitePages/TraCuuNoThue.aspx'
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_experimental_option("useAutomationExtension", False)
    # chrome_options.add_experimental_option(
    #     "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("detach", True)

    browser = webdriver.Chrome(
        "chromedriver/chromedriver", options=chrome_options)
    browser.maximize_window()
    browser.get(url)
    root = Tk()
    root.geometry("400x300+300+300")
    app = SimpleDialog(browser)

    root.mainloop()
    # Here we can act on the form components or
    # better yet, copy the output to a new variable
    # Get rid of the error message if the user clicks the
    # close icon instead of the submit button
    # Any component of the dialog will no longer be available
    # past this point
    try:
        root.destroy()
    except:
        pass
    # import tkinter as tk

    # ROOT = tk.Tk()

    # ROOT.withdraw()
    # # the input dialog
    # USER_INP = simpledialog.askstring(title="Test",
    #                                   prompt="What's your Name?:")
    # USER_INP = simpledialog.askstring(title="Test",
    #                                   prompt="What's your Name?:")
    # USER_INP = simpledialog.askstring(title="Test",
    #                                   prompt="What's your Name?:")

    # #  check it out
    # print("Hello", USER_INP)
