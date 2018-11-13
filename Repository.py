'''
author: Ashish Singh

Repository() class is the container for Student,Instructor and Major objects. It also adds the required and elective courses 
for each of the majors in a dictionary, where the key is the major and the items are sets containing the courses. The main() method may print summary pretty tables or
return a list of results for testing. Set parameter table=False for testing e.g. rep = Repository(path to data files,table=False)

Student objects include cwid,name,course, and grades_dictionary instance attributes

Instructor objects include cwid, name, department and course_students_count = defaultdict(int) attributes

TestSuite class has test methods for the Repository class.

file_reader is a generator that reads each line from a file, splits the line based on a separator and yields the results as a tuple.
Note that the generator does not allow blank values except for grades.

prettytable_from_db() method establishes a database connection and queries 'instructors' and 'grades' tables to generate instructors summary

'''

import os
import prettytable
from collections import defaultdict
import unittest
import sqlite3

def file_reader(path,num_fields,separator,file_name,header=False):
    try:        
        fp = open(path,'r')        
    except FileNotFoundError:
        #raise Exception to be handled by the calling object
        raise FileNotFoundError("File Not Found:",path)
    else:
        with fp:
            line_num=1
            if header:
                chars = fp.readline().rstrip("\n").split(separator)
                #check if the first line has exactly the required number of fields otherwise raise ValueError
                length = len(chars)
                if length!=num_fields:
                    raise ValueError("{} has {} fields on line {} but expected {}".format(path,length,line_num,num_fields))
                #next(fp)
                line_num+=1     
            for line in fp:
                chars = line.rstrip("\n").split(separator)
                #check if a line has exactly the required number of fields otherwise raise ValueError
                length = len(chars)
                if length!=num_fields:
                    raise ValueError("{} has {} fields on line {} but expected {}".format(path,length,line_num,num_fields))
                #No blank values allowed except grades
                if file_name=="grades":
                    for ch in range(4): #raise error if any value except grade value is blank
                        if ch==2:
                            continue
                        else:
                            if chars[ch].strip()=="":
                                raise ValueError("One or more values in {} file, line {} is blank".format(file_name,line_num))
                else:
                    for ch in chars: #raise error if any value is blank
                        if ch.strip()=='':
                            raise ValueError("One or more values in {} file, line {} is blank".format(file_name,line_num))
                #All checks complete. Yield values
                yield tuple(chars)
                line_num+=1
        #print("File closed")


class Student():
    __slots__ = ['cwid','name','major','majorobj','completed_courses','required_remaining','electives_remaining']

    valid_grades = ('A','A-','B+','B','B-','C+','C')  

    def __init__(self,cwid,name,major,majorobj):
        self.cwid = cwid
        self.name = name
        self.major = major
        self.majorobj = majorobj
        self.completed_courses = defaultdict(str)
          
    
    def add_grade(self,course,grade):       
        if grade in Student.valid_grades:
            self.completed_courses[course]=grade

 
class Instructor():
    __slots__= ['cwid','name','department','course_students_count']

    def __init__(self,cwid,name,department):
        self.cwid = cwid
        self.name = name
        self.department = department
        self.course_students_count = defaultdict(int)

    def add_course_count(self,course):
        self.course_students_count[course]+=1

class Majors():
    __slots__= ['majors_list']

    def __init__(self,majors_list):   
        self.majors_list = majors_list

class Repository():
    
    majors_list = defaultdict(lambda: defaultdict(set))  
    #if table == True return the summary as a list for testing, otherwise print prettytable
    def __init__(self,path,table=True):
        self.path = path
        self.table = table
        self.summary_list = defaultdict(list)
    
    def print_prettytable(self,label,table_name,fieldnames,obj):
        
        pt = prettytable.PrettyTable(field_names=fieldnames)
              
        if(table_name=='majors'):
            if self.table:
                print(label)
            for major in obj.majors_list:
                if self.table:
                    pt.add_row([major,sorted(obj.majors_list[major]['R']),sorted(obj.majors_list[major]['E'])])
                else:
                    self.summary_list['majors'].append([major,sorted(obj.majors_list[major]['R']),sorted(obj.majors_list[major]['E'])])
            if self.table:
                print(pt)
        elif(table_name=="instructors"):
            if self.table:
                print(label)         
            for cwid,instructor in obj.items():                
                for course,count in instructor.course_students_count.items():
                    if self.table:
                        pt.add_row([instructor.cwid,instructor.name,instructor.department,course,count])
                    else:
                        self.summary_list['instructors'].append([instructor.cwid,instructor.name,instructor.department,course,count])
            if self.table:  
                print(pt)
                #instructor prettytable from database                
        elif(table_name=='students'):
            if self.table:
                print(label)
            for cwid,student in obj.items():
                sorted_dict = sorted(student.completed_courses)
                self.check_required_remaining_courses(student)
                if self.table:
                    pt.add_row([student.cwid,student.name,sorted_dict,student.required_remaining,student.electives_remaining])
                else:
                    self.summary_list['students'].append([student.cwid,student.name,sorted_dict,student.required_remaining,student.electives_remaining])
            if self.table:
                print(pt)

        if not self.table:
            return self.summary_list
        
    def prettytable_from_db(self,label,fieldnames,DB_FILE,query):
            print(label)
            db = sqlite3.connect(DB_FILE)
            pt_instructor_db = prettytable.PrettyTable(field_names=fieldnames)
            for row in db.execute(query):
                pt_instructor_db.add_row(list(row))
            print(pt_instructor_db)
            db.close()    
    
    def check_required_remaining_courses(self,student):
            #sorted_dict = sorted(student.completed_courses)
            #check remaining required and elective courses
            electives_completed = set()
            required_completed = set()
            for course in student.completed_courses:
                if course in student.majorobj.majors_list[student.major]['R']:
                    required_completed.add(course)
                elif course in student.majorobj.majors_list[student.major]['E']:
                    electives_completed.add(course)
            
            required_remaining = student.majorobj.majors_list[student.major]['R'] - required_completed       
                        
            if(len(required_remaining)==0):
                student.required_remaining = 'None'
            else:
                student.required_remaining = student.majorobj.majors_list[student.major]['R'] - required_completed
            
            if(len(electives_completed)>0):
                student.electives_remaining = 'None'
            else:
                student.electives_remaining = student.majorobj.majors_list[student.major]['E'] - electives_completed
        

    def main(self):
        
        #The line below will create a dictionary structure: {Stevens: {students:{id1:Student(),id2:Student()}},{instructors:{id1:{course1:count1,course2:count2}}}
        college_repository = defaultdict(lambda: defaultdict(dict))
        college_name = os.path.basename(self.path)
        majors = set()


        #read majors.txt and add the list of required and electives for each major to class variable majors_list
        num_fields=3
        separator="\t"
        file_name='majors'
        path = os.path.join(self.path,'majors.txt')
        #majors_list is a dictionary of type: majors_list[major]['R' or 'E'] = {cours1,course2...}
        for major,course_type,course in file_reader(path,num_fields,separator,file_name):
            Repository.majors_list[major][course_type].add(course)
            majors.add(major)
        #create Majors object and add to college_repository
        majorobj = Majors(Repository.majors_list)
        college_repository[college_name]['majors']=majorobj

        #read students.txt, create Student() instance and add  to repository
        num_fields=3
        separator="\t"
        file_name='students'
        path = os.path.join(self.path,"students.txt")
        for cwid,name,major in file_reader(path,num_fields,separator,file_name):
            #check if the major is provided
            if major not in majors:
                raise ValueError('Attempting to add major - {} for student cwid - {}. This major is not provided by {}'.format(major,cwid,college_name))
            student = Student(cwid,name,major,majorobj)
            #add Student object to college_repository
            college_repository[college_name]['students'][cwid]=student            

        #read instructors.txt, create Instructor() instance and add to repository
        num_fields=3
        separator="\t"
        file_name='instructors'
        path = os.path.join(self.path,"instructors.txt")
        for cwid,name,department in file_reader(path,num_fields,separator,file_name):
            instructor = Instructor(cwid,name,department)                
            #add instructor object to college_repository
            college_repository[college_name]['instructors'][cwid]=instructor
            
                            
        #read grades.txt, add courses and grades to Student defaultdict(str), add courses to Instructor and increase count for each student
        num_fields=4
        separator="\t"
        file_name='grades'
        path = os.path.join(self.path,"grades.txt")
        for cwid,course,grade,instructor_cwid in file_reader(path,num_fields,separator,file_name):            
            #add course and grade to Student
            try: #Raise KeyError if student cwid from grades.txt is not present in students.txt
                college_repository[college_name]['students'][cwid].add_grade(course,grade)
            except KeyError:
                raise KeyError("Attempting to add grades for student id {}. Information for this student id is not present in the students.txt file".format(cwid))

            #increase course count for instructor
            try: #Raise KeyError if student cwid from grades.txt is not present in students.txt
                college_repository[college_name]['instructors'][instructor_cwid].add_course_count(course)
            except KeyError:
                raise KeyError("Attempting to add course for instructor id {}. Information for this instructor id is not present in instructors.txt".format(instructor_cwid))


        #-------------------------------- PRINT SUMMARY TABLES--------------------------------------------------
        #if table==False return list else print prettytable        
        
        #majors prettytable
        label = "Majors Summary"
        table_name='majors'
        field_names = ['Dept','Required','Electives']
        self.print_prettytable(label,table_name,field_names,college_repository[college_name][table_name])
        
        #student prettytable
        
        label = "Student Summary"
        table_name='students'
        field_names = ['CWID','Name','Completed Courses','Remaining Required','Remaining Electives']
        self.print_prettytable(label,table_name,field_names,college_repository[college_name]['students'])

        #instructors prettytable
        label = "Instructor Summary"
        table_name='instructors'
        field_names=['CWID','Name','Dept','Course','Students']
        self.print_prettytable(label,table_name,field_names,college_repository[college_name]['instructors'])

        #For testing
        if not self.table:
            return self.summary_list         
    

class TestSuite(unittest.TestCase):
    
    def test_repository(self):
        #these test files are in correct format
        
        test = Repository(r'StudentDatabase\TestFiles',table=False)
        repository_test = test.main()
        
        self.assertEqual(repository_test['students'],[['10103', 'Baldwin, C', ['CS 501', 'SSW 564', 'SSW 567', 'SSW 687'],{'SSW 555', 'SSW 540'}, 'None'],['10115', 'Wyatt, X', ['SSW 564', 'SSW 567', 'SSW 687'],{'SSW 555', 'SSW 540'},{'CS 501', 'CS 513', 'CS 545'}]])
        self.assertEqual(repository_test['instructors'],[['98765', 'Einstein, A', 'SFEN', 'SSW 567', 2], ['98764', 'Feynman, R', 'SFEN', 'SSW 564', 2], ['98764', 'Feynman, R', 'SFEN', 'SSW 687', 2], ['98764', 'Feynman, R', 'SFEN', 'CS 501', 1], ['98764', 'Feynman, R', 'SFEN', 'CS 545', 1]])
        self.assertEqual(repository_test['majors'],[['SFEN', ['SSW 540', 'SSW 555', 'SSW 564', 'SSW 567'], ['CS 501', 'CS 513', 'CS 545']], ['SYEN', ['SYS 612', 'SYS 671', 'SYS 800'], ['SSW 540', 'SSW 565', 'SSW 810']]])

        test_dict = {"TestFilesBlankValues":ValueError,"TestFilesMissingStudent":KeyError,"TestFilesMissingInstructor":KeyError,"TestFilesUnknownMajor":ValueError}
        #Tests for:
        # TestFilesBlankValues - grades.txt file has missing values (allows mi
        # ssing values for grades, raises exception for all others)
        # TestFilesMissingStudent - grades.txt file has a grade or course for a student but no student with that cwid in students.txt
        # TestFilesMissingInstructor - grades.txt file has course taught by an instructor but no instructor with that cwid in instructors.txt
        # TestFilesUnknownMajor - students.txt has 'UNKNOWN_MAJOR' as the major for student cwid 11788
        for key, errortype in test_dict.items():
            test= Repository(r'StudentDatabase\\'+key,table=False)
            with self.assertRaises(errortype):
                repository_test = test.main()

def main():
    try:
        stevens = Repository(r'StudentDatabase\Stevens') # read files and generate prettytables
        stevens.main()

        #print instructor prettytable from database
        DB_FILE = r"810_startup.db"
        field_names=['CWID','Name','Dept','Course','Students']        
        query="""select i.*, g.course,count(*) as students from instructors i join grades g on g.'Grade Instructor_CWID'=i.CWID 
        group by course order by i.Dept, count(*) DESC"""
        label = "Instructor Summary from Database"        
        stevens.prettytable_from_db(label,field_names,DB_FILE,query)
        

    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    except KeyError as e:
        print(e)
main()

if __name__=="__main__":
    unittest.main(verbosity=2,exit=False)   
