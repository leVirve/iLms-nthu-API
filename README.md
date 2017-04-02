# iLMS NTHU

An iLMS client for stduents, assistants and developers.

## Install

```bash
pip install -U ilms-nthu
```

*Note: develop and test on Python3.5+*


## Sample code

```python
from ilms.core import User
from ilms.core import Core as iLms


user = User('<user_id>', '<password>')
user.login()
ilms = iLms(user)

''' 1. get your profile '''
profile = ilms.get_profile()

''' 2. iterate through all your courses '''
for cou in ilms.get_courses():

    ''' 2.a find out all homewrok information '''
    for homework in cou.get_homeworks():

        ''' 3. if you're TA, you should get this feature
               to explore all the students' works !
               [View the detail / Download files]
        '''
        for handin in homework.handin_list:
            pprint(handin.detail)
            handin.download()

    ''' 4. You can download all materials in few lines ! '''
    for material in cou.get_materials():
        print(material.detail)
        material.download()

    print(cou.get_forum_list().result)
```

### Smart query container

Even, with `smart query` feature

```python

courses = ilms.get_courses()

''' get the specific course with keyword '''
course = courses.find(course_id='CS35700')

homeworks = course.get_homeworks()

''' get the specific homework (in two ways) '''
hw1 = homeworks.get(0)
hw1 = homeworks.find(title='Homework1')

''' get the specific haned_in homework '''
handin = hw1.get(87)
handin = hw1.handin_list.find(authour='王曉明')
handin = hw1.handin_list.find(date='2017-03-25')

```
