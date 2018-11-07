'''
Author: Ashish Singh

Repository() class is the container for Student and Instructor objects. The main() method may print summary pretty tables or
return a list of results for testing. Set parameter table=False for testing e.g. rep = Repository(path,table=False)

Student objects include cwid,name,course, and grades_dictionary instance attributes

Instructor objects include cwid, name, department and course_students_count = defaultdict(int) attributes

TestSuite class has test methods for the Repository class.

file_reader is a generator that reads each line from a file, splits the line based on a separator and yields the results as a tuple.
Note that the generator does not allow blank values except for grades.

'''

import os
import prettytable
from collections import defaultdict
import unittest

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
        print("File closed")


class Student():
    __slots__ = ['cwid','name','major','grades_dictionary']

    def __init__(self,cwid,name,major):
        self.cwid = cwid
        self.name = name
        self.major = major
        self.grades_dictionary = defaultdict(str)
    
    def add_grade(self,course,grade):
        self.grades_dictionary[course]=grade


class Instructor():
    __slots__= ['cwid','name','department','course_students_count']


    def __init__(self,cwid,name,department):
        self.cwid = cwid
        self.name = name
        self.department = department
        self.course_students_count = defaultdict(int)

    def add_course_count(self,course):
        self.course_students_count[course]+=1


class Repository():
    
    #if table == True return the summary as a list for testing, otherwise print prettytable
    def __init__(self,path,table=True):
        self.path = path
        self.table = table
    
    def main(self):
        
        #The line below will create a dictionary structure: {Stevens: {students:{id1:Student(),id2:Student()}},{instructors:{id1:{course1:count1,course2:count2}}}
        college_repository = defaultdict(lambda: defaultdict(lambda:dict()))
        college_name = os.path.basename(self.path) 
                   
        
            #read students.txt, create Student() instance and add  to repository
        num_fields=3
        separator="\t"
        file_name='students'
        path = os.path.join(self.path,"students.txt")
        for cwid,name,major in file_reader(path,num_fields,separator,file_name):
            student = Student(cwid,name,major)            
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
        #student prettytable
        if not self.table:
            summary_list = defaultdict(list)
        else:
            print("Student Summary")
            pt_student = prettytable.PrettyTable(field_names=['CWID','Name','Completed Courses'])
        
        for cwid,student in college_repository[college_name]['students'].items():
            sorted_dict = sorted(student.grades_dictionary)
            if not self.table:
                summary_list['students'].append([student.cwid,student.name,sorted_dict])
            else:
                pt_student.add_row([student.cwid,student.name,sorted_dict])
        if self.table:
            print(pt_student)
        
        #instructor prettytable
        if self.table:
            print("Instructor Summary")
            pt_instructor = prettytable.PrettyTable(field_names=['CWID','Name','Dept','Course','Students'])
        for cwid,instructor in college_repository[college_name]['instructors'].items():                
            for course,count in instructor.course_students_count.items():
                if not self.table:
                    summary_list['instructors'].append([instructor.cwid,instructor.name,instructor.department,course,count])
                else:
                    pt_instructor.add_row([instructor.cwid,instructor.name,instructor.department,course,count])
                #print(instructor.cwid,instructor.name,instructor.department,course,count)
        
        if not self.table:
            return summary_list
        else:
            print(pt_instructor)
                
    

class TestSuite(unittest.TestCase):
    
    def test_repository(self):
        #these test files are in correct format
        
        test = Repository(r'C:\Python\Test scripts\810\StudentDatabase\TestFiles',table=False)
        repository_test = test.main()
        self.assertEqual(repository_test['students'],[['10103', 'Baldwin, C', ['CS 501', 'SSW 564', 'SSW 567', 'SSW 687']],['10115', 'Wyatt, X', ['CS 545', 'SSW 564', 'SSW 567', 'SSW 687']]])
        self.assertEqual(repository_test['instructors'],[['98765', 'Einstein, A', 'SFEN', 'SSW 567', 2], ['98764', 'Feynman, R', 'SFEN', 'SSW 564', 2], ['98764', 'Feynman, R', 'SFEN', 'SSW 687', 2], ['98764', 'Feynman, R', 'SFEN', 'CS 501', 1], ['98764', 'Feynman, R', 'SFEN', 'CS 545', 1]])
        
        test_dict = {"TestFilesBlankValues":ValueError,"TestFilesMissingStudent":KeyError,"TestFilesMissingInstructor":KeyError}
        #Tests for:
        # TestFilesBlankValues - grades.txt file has missing values (allows missing values for grades, raises exception for all others)
        # TestFilesMissingStudent - grades.txt file has a grade or course for a student but no student with that cwid in students.txt
        # TestFilesMissingInstructor - grades.txt file has course taught by an instructor but no instructor with that cwid in instructors.txt
        for key, errortype in test_dict.items():
            test= Repository(r'C:\Python\Test scripts\810\StudentDatabase\\'+key,table=False)
            with self.assertRaises(errortype):
                repository_test = test.main()


def main():
    try:
        stevens = Repository(r'C:\Python\Test scripts\810\StudentDatabase\Stevens') # read files and generate prettytables
        stevens.main()
    except FileNotFoundError as e:
        print(e)
    except ValueError as e:
        print(e)
    except KeyError as e:
        print(e)
main()

if __name__=="__main__":
    unittest.main(verbosity=2,exit=False)


    
