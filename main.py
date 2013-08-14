#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import jinja2
import os
import cgi
from google.appengine.api import rdbms
from datetime import datetime
from pytz import timezone
import pytz

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'])

_INSTANCE_NAME = "prinya-th-2013:prinya-db"


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

class DetailCourseHandler(webapp2.RequestHandler):
    def get(self):
    	course_id = self.request.get('course_code');
    	# course_id = "BIS-101"

    	conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
    	cursor = conn.cursor()
        sql="SELECT * FROM course WHERE course_code = '%s'"%(course_id)
    	cursor.execute(sql);

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="SELECT co.course_code FROM course co,prerequsite_course pre\
            WHERE prerequsite_id=co.course_id AND pre.course_id=\
            (SELECT course_id FROM course WHERE course_code='%s')"%(course_id)
        cursor2.execute(sql2);
        pre_code=""
        for row in cursor2.fetchall():
            pre_code=row[0]

        templates = {
    		'course' : cursor.fetchall(),
            'prerequisite_code' : pre_code,
    	}
    	get_template = JINJA_ENVIRONMENT.get_template('course_detail.html')
    	self.response.write(get_template.render(templates));
        conn.close();
        conn2.close();

class ModifyCourseHandler(webapp2.RequestHandler):
    def get(self):
    	course_id = self.request.get('course_id');

    	conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
    	cursor = conn.cursor()
        sql="SELECT * FROM course WHERE course_code = '%s'"%(course_id)
        cursor.execute(sql);

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="SELECT course_id,course_code from course where course_code not like '%s'"%(course_id)
        cursor2.execute(sql2);

        conn3 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor3 = conn3.cursor()
        sql3="SELECT section_id,section_number,UPPER(CONCAT(CONCAT(firstname,' '),lastname)),enroll,capacity\
            FROM section sec JOIN staff st ON teacher_id=staff_id\
            WHERE regiscourse_id=(SELECT regiscourse_id FROM regiscourse WHERE course_id=\
            (SELECT course_id from course where course_code='%s')) ORDER BY section_number"%(course_id)
        cursor3.execute(sql3);

        conn4 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor4 = conn4.cursor()
        sql4="SELECT co.course_id,co.course_code FROM course co,prerequsite_course pre\
            WHERE prerequsite_id=co.course_id AND pre.course_id=\
            (SELECT course_id FROM course WHERE course_code='%s')"%(course_id)
        # sql4="SELECT prerequisite , CASE prerequisite WHEN '0' THEN '- NONE - ' \
        #     ELSE (SELECT course_code FROM course WHERE course_id=\
        #     (SELECT prerequisite FROM course WHERE course_code='%s'))\
        #     END FROM course WHERE  course_code='%s'"%(course_id,course_id)
        cursor4.execute(sql4);
        pre_id=""
        pre_code=""
        for row in cursor4.fetchall():
            pre_id=row[0]
            pre_code=row[1]

        templates = {
    		'course' : cursor.fetchall(),
            'course2' : cursor2.fetchall(),
            'course3' : cursor3.fetchall(),
            'course_id' : course_id,
            'prerequisite_id' : pre_id,
            'prerequisite_code' : pre_code,
    	}
    	get_template = JINJA_ENVIRONMENT.get_template('course_modify.html')
    	self.response.write(get_template.render(templates));
        conn.close();
        conn2.close();
        conn3.close();
        conn4.close();


class UpdateCourseHandler(webapp2.RequestHandler):
    def post(self):
    	course_id = self.request.get('course_id');
        course_name = self.request.get('course_name');
        prerequisite = self.request.get('prerequisite');
        if prerequisite!="":
            prerequisite=int(prerequisite)
        course_description = self.request.get('course_description');
    	credit_lecture = self.request.get('credit_lecture');
        credit_lecture=int(credit_lecture)
        credit_lab = self.request.get('credit_lab');
        credit_lab=int(credit_lab)
        credit_learning = self.request.get('credit_learning');
        credit_learning=int(credit_learning)
    	faculity = self.request.get('faculity');
        department = self.request.get('department');

    	conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
    	cursor = conn.cursor()
        sql="UPDATE course SET course_code = '%s' , \
        course_name = '%s' , course_description = '%s' , \
         credit_lecture = '%d' , credit_lab = '%d' , \
         credit_learning = '%d' , department = '%s' , \
         faculity = '%s' WHERE course_code = '%s'"%(course_id,course_name,course_description,credit_lecture,credit_lab,credit_learning,department,faculity,course_id)
    	cursor.execute(sql);
        conn.commit();
              
        conn3 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor3 = conn3.cursor()
        sql3="DELETE FROM prerequsite_course\
                    WHERE course_id=(SELECT course_id FROM course WHERE course_code = '%s')"%(course_id)
        cursor3.execute(sql3)        
        conn3.commit()
        
        if prerequisite!="":
            conn4 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
            cursor4 = conn4.cursor()
            sql4="INSERT INTO prerequsite_course\
                        (course_id,type,prerequsite_id) VALUES((SELECT course_id FROM course WHERE course_code = '%s'),1,'%s')"%(course_id,prerequisite)
            cursor4.execute(sql4)        
            conn4.commit()
            conn4.close();


        

        utc = pytz.utc
        date_object = datetime.today()
        utc_dt = utc.localize(date_object);
        bkk_tz = timezone("Asia/Bangkok");
        bkk_dt = bkk_tz.normalize(utc_dt.astimezone(bkk_tz))
        time_insert = bkk_dt.strftime("%H:%M:%S")

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="INSERT INTO log (staff_id,course_id,day,time,type)\
            VALUES(3,(SELECT course_id FROM course WHERE course_code = '%s'),CURDATE(),'%s',4)"%(course_id,time_insert)
        cursor2.execute(sql2)        
        conn2.commit()
        conn2.close();
        conn.close();
        conn3.close();
        
        self.redirect("/ModifyCourse?course_id="+course_id)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class AddSectionHandler(webapp2.RequestHandler):
    def get(self):
        
        course_id=self.request.get('course_id');

        templates = {
            'course_id' : course_id,
        }
        get_template = JINJA_ENVIRONMENT.get_template('section.html')
        self.response.write(get_template.render(templates));

class InsSectionHandler(webapp2.RequestHandler):
    def post(self):

    	course_id=self.request.get('course_id');
        section_number=self.request.get('section_number');
        section_number=int(section_number)
        teacher=self.request.get('teacher');
        capacity=self.request.get('capacity');
        capacity=int(capacity)

        # conncheck = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        # cursorcheck = conncheck.cursor()
        # sqlcheck="INSERT INTO section (regiscourse_id,section_number,teacher_id,capacity,enroll) \
        #     VALUES ((SELECT course_id FROM course where course_code = '%s'),'%d',\
        #     (SELECT staff_id FROM staff WHERE firstname = '%s'),'%d','0')"%(course_id,section_number,teacher,capacity)
        # cursorcheck.execute(sqlcheck);
        # conncheck.commit();
        # conncheck.close();


        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()
        sql="INSERT INTO section (regiscourse_id,section_number,teacher_id,capacity,enroll) \
            VALUES ((SELECT course_id FROM course where course_code = '%s'),'%d',\
            (SELECT staff_id FROM staff WHERE firstname = '%s'),'%d','0')"%(course_id,section_number,teacher,capacity)
        cursor.execute(sql);
        conn.commit();
        conn.close();

        utc = pytz.utc
        date_object = datetime.today()
        utc_dt = utc.localize(date_object);
        bkk_tz = timezone("Asia/Bangkok");
        bkk_dt = bkk_tz.normalize(utc_dt.astimezone(bkk_tz))
        time_insert = bkk_dt.strftime("%H:%M:%S")

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="INSERT INTO log (staff_id,course_id,day,time,type)\
            VALUES(3,(SELECT course_id FROM course WHERE course_code = '%s'),CURDATE(),'%s',2)"%(course_id,time_insert)
        cursor2.execute(sql2)        
        conn2.commit()
        conn2.close();

        self.redirect("/ModifyCourse?course_id="+course_id)

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class DetailSectionHandler(webapp2.RequestHandler):
    def get(self):
        
        course_id=self.request.get('course_id');
        section_id=self.request.get('section_id');
        section_id=int(section_id)
        section_number=self.request.get('section_number');
        section_number=int(section_number)

        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()

        sql="SELECT section_number,firstname,capacity\
            FROM section sec JOIN staff st ON teacher_id=staff_id\
            WHERE section_id='%d' AND section_number='%d'"%(section_id,section_number)
        cursor.execute(sql);

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="SELECT sectime_id, CASE day WHEN '1' THEN 'Sunday'\
            WHEN '2' THEN 'Monday'\
            WHEN '3' THEN 'Tuesday'\
            WHEN '4' THEN 'Wednesday'\
            WHEN '5' THEN 'Thursday'\
            WHEN '6' THEN 'Friday'\
            WHEN '7' THEN 'Saturday'\
            ELSE 'ERROR' END,CONCAT(CONCAT(start_time,'-'),end_time),room FROM section_time WHERE section_id='%d'"%(section_id)
        cursor2.execute(sql2);



        templates = {
            'section' : cursor.fetchall(),
            'time' : cursor2.fetchall(),
            'course_id' : course_id,
            'section_id' : section_id,
            'section_number' : section_number,
        }
        get_template = JINJA_ENVIRONMENT.get_template('secdetail.html')
        self.response.write(get_template.render(templates));
        conn.close();
        conn2.close();

class ModifySectionHandler(webapp2.RequestHandler):
    def get(self):

        course_id=self.request.get('course_id');
        section_id=self.request.get('section_id');
        section_id=int(section_id)
        section_number=self.request.get('section_number');
        section_number=int(section_number)
        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()

        sql="SELECT section_number,firstname,capacity\
            FROM section sec JOIN staff st ON teacher_id=staff_id\
            WHERE section_id='%d' AND section_number='%d'"%(section_id,section_number)
        cursor.execute(sql);

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="SELECT sectime_id, CASE day WHEN '1' THEN 'Sunday'\
            WHEN '2' THEN 'Monday'\
            WHEN '3' THEN 'Tuesday'\
            WHEN '4' THEN 'Wednesday'\
            WHEN '5' THEN 'Thursday'\
            WHEN '6' THEN 'Friday'\
            WHEN '7' THEN 'Saturday'\
            ELSE 'ERROR' END,CONCAT(CONCAT(start_time,'-'),end_time),room FROM section_time WHERE section_id='%d'"%(section_id)
        cursor2.execute(sql2);

        templates = {
            'section' : cursor.fetchall(),
            'time' : cursor2.fetchall(),
            'course_id' : course_id,
            'section_id' : section_id,
            'section_number' : section_number,
        }
        get_template = JINJA_ENVIRONMENT.get_template('section_modify.html')
        self.response.write(get_template.render(templates));
        conn.close();
        conn2.close();

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class AddSectimeHandler(webapp2.RequestHandler):
    def get(self):
        
        course_id=self.request.get('course_id');
        section_id=self.request.get('section_id');
        section_id=int(section_id)
        section_number=self.request.get('section_number');
        section_number=int(section_number)

        templates = {
            'course_id' : course_id,
            'section_id' : section_id,
            'section_number' : section_number,
        }
        get_template = JINJA_ENVIRONMENT.get_template('section_time.html')
        self.response.write(get_template.render(templates));

class InsSectimeHandler(webapp2.RequestHandler):
    def post(self):

        course_id=self.request.get('course_id');
        section_id=self.request.get('section_id');
        section_id=int(section_id)
        section_number=self.request.get('section_number');
        section_number=int(section_number)
        day=self.request.get('day');
        day=int(day)
        start_time=self.request.get('start_time');
        end_time=self.request.get('end_time');
        room=self.request.get('roomid');

        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()
        sql="INSERT INTO section_time (day,start_time,end_time,room,section_id)\
            VALUES ('%d','%s','%s','%s','%d')"%(day,start_time,end_time,room,section_id)
        cursor.execute(sql);
        conn.commit();
        conn.close();

        utc = pytz.utc
        date_object = datetime.today()
        utc_dt = utc.localize(date_object);
        bkk_tz = timezone("Asia/Bangkok");
        bkk_dt = bkk_tz.normalize(utc_dt.astimezone(bkk_tz))
        time_insert = bkk_dt.strftime("%H:%M:%S")

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="INSERT INTO log (staff_id,course_id,day,time,type)\
            VALUES(3,(SELECT course_id FROM course WHERE course_code = '%s'),CURDATE(),'%s',3)"%(course_id,time_insert)
        cursor2.execute(sql2)        
        conn2.commit()
        conn2.close();

        self.redirect("/ModifySection?course_id="+str(course_id)+"&section_id="+str(section_id)+"&section_number="+str(section_number));

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

class DeleteCourseHandler(webapp2.RequestHandler):
    def get(self):
        
        course_id=self.request.get('course_id')
        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()
        sql="DELETE FROM regiscourse  WHERE course_id=(SELECT course_id FROM course WHERE course_code='%s')"%(course_id)
        cursor.execute(sql);
        conn.commit();
        conn.close();

        conn3 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor3 = conn3.cursor()
        sql3="DELETE FROM course WHERE course_code='%s'"%(course_id)
        cursor3.execute(sql3);
        conn3.commit();
        conn3.close();

        utc = pytz.utc
        date_object = datetime.today()
        utc_dt = utc.localize(date_object);
        bkk_tz = timezone("Asia/Bangkok");
        bkk_dt = bkk_tz.normalize(utc_dt.astimezone(bkk_tz))
        time_insert = bkk_dt.strftime("%H:%M:%S")

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="INSERT INTO log (staff_id,course_id,day,time,type)\
            VALUES(3,(SELECT course_id FROM course WHERE course_code = '%s'),CURDATE(),'%s',7)"%(course_id,time_insert)
        cursor2.execute(sql2)        
        conn2.commit()
        conn2.close();

        self.redirect("http://prinya-ailada.appspot.com/");

class DeleteSectionHandler(webapp2.RequestHandler):
    def get(self):
    	
        course_id=self.request.get('course_id')
        section_id=self.request.get('section_id')
        section_id=int(section_id)
        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()
        sql="DELETE FROM section WHERE section_id='%d'"%(section_id)
        cursor.execute(sql);
        conn.commit();
        conn.close();

        utc = pytz.utc
        date_object = datetime.today()
        utc_dt = utc.localize(date_object);
        bkk_tz = timezone("Asia/Bangkok");
        bkk_dt = bkk_tz.normalize(utc_dt.astimezone(bkk_tz))
        time_insert = bkk_dt.strftime("%H:%M:%S")

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="INSERT INTO log (staff_id,course_id,day,time,type)\
            VALUES(3,(SELECT course_id FROM course WHERE course_code = '%s'),CURDATE(),'%s',6)"%(course_id,time_insert)
        cursor2.execute(sql2)        
        conn2.commit()
        conn2.close();

        self.redirect("/ModifyCourse?course_id="+course_id)

class DeleteSectimeHandler(webapp2.RequestHandler):
    def get(self):
        
        course_id=self.request.get('course_id')
        sectime_id=self.request.get('sectime_id')
        sectime_id=int(sectime_id)
        section_id=self.request.get('section_id')
        section_id=int(section_id)
        section_number=self.request.get('section_number');
        section_number=int(section_number)
        conn = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor = conn.cursor()
        sql="DELETE FROM section_time WHERE sectime_id='%d'"%(sectime_id)
        cursor.execute(sql);
        conn.commit();
        conn.close();

        utc = pytz.utc
        date_object = datetime.today()
        utc_dt = utc.localize(date_object);
        bkk_tz = timezone("Asia/Bangkok");
        bkk_dt = bkk_tz.normalize(utc_dt.astimezone(bkk_tz))
        time_insert = bkk_dt.strftime("%H:%M:%S")

        conn2 = rdbms.connect(instance=_INSTANCE_NAME, database='Prinya_Project')
        cursor2 = conn2.cursor()
        sql2="INSERT INTO log (staff_id,course_id,day,time,type)\
            VALUES(3,(SELECT course_id FROM course WHERE course_code = '%s'),CURDATE(),'%s',7)"%(course_id,time_insert)
        cursor2.execute(sql2)        
        conn2.commit()
        conn2.close();

        self.redirect("/ModifySection?course_id="+course_id+"&section_id="+str(section_id)+"&section_number="+str(section_number));


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/DetailCourse', DetailCourseHandler),
    ('/ModifyCourse',ModifyCourseHandler),
    ('/UpdateCourse',UpdateCourseHandler),
    ('/AddSection',AddSectionHandler),
    ('/InsSection',InsSectionHandler),
    ('/AddSectime',AddSectimeHandler),
    ('/InsSectime',InsSectimeHandler),
    ('/DetailSection',DetailSectionHandler),
    ('/ModifySection',ModifySectionHandler),
    ('/DeleteCourse',DeleteCourseHandler),
    ('/DeleteSection',DeleteSectionHandler),
    ('/DeleteSectime',DeleteSectimeHandler)
], debug=True)
