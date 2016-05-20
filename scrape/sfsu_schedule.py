#!/usr/bin/env python2

import urllib
import urllib2

import cookielib

from bs4 import BeautifulSoup

import sys

# 6543 = Schedule Number

class Course(object):
    def __init__(self, subject, number, title, ext=None):
        self.subject = subject
        self.number = number
        self.ext = ext
        self.title = title

class Section(object):
    def __init__(self, klass, number, section, time, room, instructor, date, description=False, term=None):
        self.klass = klass
        self.number = number
        self.section = section
        self.description = description
        self.time = time
        self.room = room
        self.instructor = instructor
        self.date = date

    def __str__(self):
        if self.klass is not None:
            return "{} {}-{} {} by {}".format(self.klass.subject, self.klass.number, self.number, self.klass.title.encode('latin-1'), self.instructor.encode('latin-1'))
        else:
            return "UNKNOWN UNKNOWN-UNKNOWN {} by {}".format(self.number, self.instructor)

class ResultsPage(object):
    def __init__(self, soup):
        self.soup = soup
        self.classes = {}

    def parse_class(self, element):
        raise NotImplementedError()

    def class_iter(self):
        raise NotImplementedError()

    def course_iter(self):
        raise NotImplementedError()


class ElementNotFoundError(ValueError): pass

def select_one_text(soup, selector):
    elements = soup.select(selector)
    if len(elements) < 1:
        raise ElementNotFoundError()

    return elements[0].text

import re

course_info_regex = re.compile(r'Collapse section\s+((\w+\s+)*\w+)\s+(\d+)(\w*)\s+-\s+(\w.*\S)\s*$')
#times = re.compile()
section_number_regex = re.compile(r'^(\d+)\s*-')

import datetime

def iter_courses(uri, soup, jar, opener, term):
    courses = {}
    class_offerings = {}

    form = StatefulQueryFactory(uri, jar)

    i = 0
    while True:
        try:
            # TODO: retrieve class number/name
            schedule_number = int(select_one_text(soup, "#MTG_CLASS_NBR$" + str(i)))

            number_element = soup.select("#MTG_CLASS_NBR$" + str(i))[0]

            course = None
            for table in number_element.find_parents('table', class_='PABACKGROUNDINVISIBLEWBO'):
                images = table.find_all('img', class_="PTCOLLAPSE")

                if len(images) != 1:
                    continue

                infostr = images[0].attrs.get('alt')

                match = course_info_regex.match(infostr)

                if not match:
                    #import pdb; pdb.set_trace()
                    continue

                course_category = match.group(1)
                course_number = int(match.group(3))
                course_ext = match.group(4)
                course_title = match.group(5)

                course = courses.get((course_category, course_number)) or Course(course_category, course_number, course_title)
                courses[(course_category, course_number)] = course

            # TODO: parse
            time = select_one_text(soup, "#MTG_DAYTIME$" + str(i))

            instructor = select_one_text(soup, "#MTG_INSTR$" + str(i))

            room = select_one_text(soup, "#MTG_ROOM$" + str(i))
            date = select_one_text(soup, "#MTG_TOPIC$" + str(i))

            section = select_one_text(soup, "#MTG_CLASSNAME$" + str(i))
            try:
                match = section_number_regex.match(section)
                section_number = int(match.group(1))
            except ValueError:
                section_number = 0
            
            request = form.from_form(soup, {"ICAction": "MTG_CLASS_NBR$" + str(i)})

            detail_soup = BeautifulSoup(opener.open(request))

            try:
                description = detail_soup.select("#DERIVED_CLSRCH_DESCRLONG")[0].text
            except IndexError:
                description = ""

            # XXX: ignoring result for now, maybe we only need to 
            #return_form = StatefulQueryFactory(uri, jar)
            #request = form.from_form(soup, {"ICAction", "CLASS_SRCH_WRK2_SSR_PB_BACK"})
            
            #_ = BeautifulSoup(opener.open(request))

            #import pdb; pdb.set_trace()
			
            if course is None:
                print  >> sys.stderr, "ERROR", Section(course, schedule_number, section_number, time, room, instructor, date, description, term)
            else:
                yield Section(course, schedule_number, section_number, time, room, instructor, date, description, term)

            i += 1
        except ElementNotFoundError:
            break

from functools import wraps 

def iter_courses_for_term(term):
    @wraps(iter_courses)
    def iter_courses2(uri, soup, jar, opener):
        return iter_courses(uri, soup, jar, opener, term)
    return iter_courses2

def scrape_hidden(soup):
    form = {}
    for i in soup.find_all("input", attrs={"type": "hidden"}):
        value = i.attrs['value']
        if value != '' and value != None:
            form[i.attrs['name']] = value

    return form

from collections import namedtuple

Option = namedtuple("Option", "name value")
Select = namedtuple("Select", "name options")

def iter_selects(soup):
    for select in soup.find_all("select"):
        options = []
        for option in select.find_all("option"):
            options.append(Option(option.text, option.attrs["value"]))
        yield Select(select.attrs["name"], options)

class StatefulQueryFactory(object):
    def __init__(self, uri, jar):
        self.uri = uri
        self.jar = jar

    def from_form(self, soup, fields={}):
        if self.uri is None:
            form_element = soup.find_all('form')[0]
            uri = form_element.attrs["action"]
        else:
            uri = self.uri
        form = scrape_hidden(soup)
        form.update(fields)
        data = urllib.urlencode(form)
        return urllib2.Request(uri, data)

class CourseQuery(object):
    SEARCH_URI = "https://cmsweb.sfsu.edu/psc/HSFPRDF/EMPLOYEE/HRMS/c/COMMUNITY_ACCESS.CLASS_SEARCH.GBL"

    def __init__(self, class_parser=None):
        self.jar = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))
        self.factory = StatefulQueryFactory(self.SEARCH_URI, self.jar)
        self.class_parser = class_parser or iter_courses

    def _request_search_page(self):
        request = urllib2.Request(self.SEARCH_URI)
        return self._get_soup(request)

    def _get_soup(self, request):
        return BeautifulSoup(self.opener.open(request))

    def query(self, fields):
        soup = self._request_search_page()

        form = fields.copy()
        form['ICAction'] = 'CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH'

        search_request = self.factory.from_form(soup, form)
        soup = self._get_soup(search_request)

        #FIXME: need to detect need for confirmation

        form = fields.copy()
        form['ICAction'] = '#ICSave'
        confirm_request = self.factory.from_form(soup, form)
        soup = self._get_soup(confirm_request)

        return self.class_parser(self.SEARCH_URI, soup, self.jar, self.opener)

    @classmethod
    def subjects(cls):
        soup = cls()._request_search_page()

        subjects = soup.find('select', attrs={'name': 'SSR_CLSRCH_WRK_SUBJECT_SRCH$1'})

        for subject in subjects.find_all('option'):
            if 'value' in subject.attrs:
                yield subject.attrs['value']

class Database(object):
    def __init__(self, connection):
        self.connection = connection
        self.professors = {}

    def _prof_id(self, name):
        if name in self.professors:
            return self.professors[name]
        else:
            try:
                first_name, last_name = name.split(' ', 1)
            except ValueError:
                first_name = name
                last_name = None

            cursor = self.connection.cursor()
            try:
                cursor.execute('SELECT id FROM "Professors" WHERE first_name = %s AND last_name = %s;', (first_name, last_name))
                prof = cursor.fetchone()

                if prof is not None:
                    prof_id = prof[0]

                    self.professors[name] = prof_id
                    return prof_id
            except psycopg2.ProgrammingError:
                pass
            except ValueError:
                pass

            cursor.execute('INSERT INTO "Professors" (first_name, last_name) VALUES(%s, %s) RETURNING id;', (first_name, last_name))
            #cursor.execute('SELECT LASTVAL()')
            prof_id = cursor.fetchone()[0] #['lastval']
            self.professors[name] = prof_id
            return prof_id

    def insert_section(self, section):
        """ NOTE: Inconsistent naming, table is "Courses"
        """
        instructor_id = self._prof_id(section.instructor)

        cursor = self.connection.cursor()
        if section.klass is None:
            cursor.execute('INSERT INTO "Courses" '
                           '(teacher_id, course_time, course_meeting_day, section_number)'
                           'VALUES(%s, %s, %s, %s)',
                           (instructor_id, section.time, section.date, section.number))
        else:
            cursor.execute('INSERT INTO "Courses" '
                           '(teacher_id,'
                           ' course_subject, course_number, course_name, course_description, course_time, course_meeting_day, course_schedule_number, section_number)'
                           'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                           (instructor_id, section.klass.subject, section.klass.number, section.klass.title, section.description,
                           section.time, section.date, section.number, section.section))

import psycopg2
if __name__ == "__main__":
    connection = psycopg2.connect("dbname=sfsudroid")
    db = Database(connection)
    courses = CourseQuery(iter_courses_for_term("SP2016"))

    for subject in CourseQuery.subjects():
        form = {}
        form['SSR_CLSRCH_WRK_SESSION_CODE$0'] = '1'
        form['SSR_CLSRCH_WRK_SUBJECT_SRCH$1'] = subject #'ACCT'
        for klass in courses.query(form):
            db.insert_section(klass)
            print klass
	connection.commit()

    connection.close()
