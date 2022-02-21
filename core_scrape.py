from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver

from bs4 import BeautifulSoup as bsup

import time
import csv


########################################
# List of Employee objects.            #
########################################

employees_data = []

########################################
# Classes                              #
########################################


class Employee:

    def __init__(self, name, courses_data):
        self.name = name
        self.courses_data = courses_data


class Course:

    def __init__(self, name, assigned, completed, expiry, status, grade, certificate):
        self.name = name
        self.assigned = assigned
        self.completed = completed
        self.expiry = expiry
        self.status = status
        self.grade = grade
        self.certificate = certificate


####################################################
# scrape_data uses selenium to login to a website. #
# It takes arguments from core_gui.                #
####################################################

def scrape_data(username, password):

    s = Service("C:/Users/44750/Desktop/geckodriver.exe")
    driver = webdriver.Firefox(service=s)
    driver.get('https://quotes.toscrape.com/login')
    user_name = driver.find_element(By.ID, 'username')
    user_name.send_keys(username)
    pass_word = driver.find_element(By.ID, 'password')
    pass_word.send_keys(password)
    submit_but = driver.find_element(By.XPATH, "//input[@value='Login']")
    submit_but.click()

    time.sleep(2)
    driver.close()

#####################################################################################
# Website for which this scraper was built, shows only 50 employees per page.       #
# find_pages will try to check for the next page and if the page displays that      #
# there are no more candidates to display, it'll stop collecting data.              #
# Number of employees is changing.                                                  #
#####################################################################################


def find_pages(driver):
    addrs = ''
    driver.get(f'{addrs}')
    collect_data(driver)

    x = 50
    while x != 0:

        time.sleep(2)
        driver.get(f'{addrs}{x}')
        end_of = driver.find_elements(By.XPATH, "//*[@id='body']/div[3]/p[4]")

        if len(end_of) > 0:
            for elem in end_of:
                if elem.text == 'There are currently no candidates to display.':
                    x = 0
        else:
            collect_data(driver)
            x += 50

#####################################################################################
# collect_data will get all the employees' names from the web-page and using them   #
# it'll collect information about courses that the employees' are assigned to.      #
# There are maximum 57 courses that each candidate can have assigned to them.       #
#####################################################################################


def collect_data(driver):
    list_of_employees = get_employees(driver.page_source)

    for emp in list_of_employees:
        time.sleep(2)

        employee_courses = get_courses(emp[1], driver.page_source)
        driver.get(f'https://{employee_courses}')
        get_data(emp[1], driver.page_source)

#####################################################################################
# get_employees will scrape employees' names from the web-page                      #
#####################################################################################


def get_employees(page_code):

    employees = []
    sup = bsup(page_code, 'html.parser')
    table = sup.find('table', attrs={'id': 'candidate_list'})
    rows = table.find_all('td')
    for data in rows:
        if data.find('span', attrs={'class': 'count'}):
            employees.append(data.get_text().split(':'))

    return employees

######################################################################
# get_courses will look for links to view employee's courses.        #
######################################################################


def get_courses(emp_name, page_code):

    sup = bsup(page_code, 'html.parser')
    table = sup.find('table', attrs={'id': 'candidate_list'})
    rows = table.find_all('tr')

    start = 0
    for row in rows:
        if start == 0:
            for data in row:
                if emp_name in data:
                    start = 1
                if start == 1:
                    if 'View' in data.get_text():
                        view_link = data.find('a').get('href')
                        return view_link

#################################################
# get_data scrapes data related to each course. #
#################################################


def get_data(emp_name, page_code):

    sup = bsup(page_code, 'html.parser')
    table = sup.find('table', attrs={'class': 'annotated responsive'})
    data = table.find_all('td')
    purify = table.find_all('h3')
    impurities = []
    for impurity in purify:
        impurities.append(impurity.get_text())

    raw_data = []
    for datum in data:
        if datum.get_text() in impurities:
            pass
        else:
            raw_data.append(datum.get_text())

    parameters = []
    courses = []
    for x in range(1, len(raw_data) + 1):
        parameters.append(raw_data[x - 1])
        if x % 7 == 0:
            new_course = Course(parameters[0], parameters[1], parameters[2], parameters[3], parameters[4],
                                parameters[5], parameters[6])

            courses.append(new_course)
            parameters = []

    new_employee = Employee(emp_name, courses)
    employees_data.append(new_employee)


def convert_to_csv():

    ######################################################
    # The main problem of converting this data into csv  #
    # was that each employee could have different number #
    # of courses assigned to them. Some employees had    #
    # 52, others 57.                                     #
    ######################################################
    with open('courses.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        ##############################################
        # First, the code looks for all the courses. #
        # This is to check how many courses are      #
        # there in total. Number of all courses      #
        # might change with time.                    #
        ##############################################

        columns = []
        for emp in employees_data:
            for course in emp.courses_data:
                if course.name not in columns:
                    columns.append(course.name)

        ################################################
        # This code could be refactored in the future. #
        ################################################
        # Data needs to be prepared for csv.           #
        # As each employee has different number of     #
        # courses, if an employee has less than the    #
        # maximum number of courses, missing data      #
        # needs to be filled with 'N/A'.               #
        ################################################

        rows = {}
        header = ['Employees']
        data = []

        for emp in employees_data:
            courses = {}
            rows[emp.name] = [emp.name]
            for course in emp.courses_data:
                courses[course.name] = course.expiry
            for col in columns:
                if col not in header:
                    header.append(col)
                if col in courses:
                    rows[emp.name].append(courses[col])
                elif col not in courses:
                    rows[emp.name].append('N/A')
        for row in rows:
            data.append(rows[row])

        writer.writerow(header)
        writer.writerows(data)




