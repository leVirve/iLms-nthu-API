# iLMS NTHU

專為 學生/助教/開發者 所寫的 iLMS 通用 API/command-line 環境

- 列出 修課課程 / 作業 / 上課教材
- 下載 作業 / 上課教材
- 上傳 `csv` 檔登記作業分數

## 安裝

- 從 `PyPI` 上安裝
    ```bash
    pip install -U ilms-nthu
    ```
- 從本專案原始碼安裝最新版
    ```bash
    pip install git+https://github.com/leVirve/iLms-nthu-API
    ```

Note: 本專案開發測試在 Python3.5+

## 指令

### 列出 修課課程 / 作業 / 上課教材

- 列出本學期所有課程
    ```bash
    ilms view course
    ```

- 列出所有修過課程
    ```bash
    ilms view course --semester_id all
    ```

- 列出某學期修過課程, e.g.
    ```bash
    ilms view course --semester_id 1051
    ```

- 列出某課程所有作業, e.g.
    ```bash
    ilms view homework --course_id CS65500
    ```

- 完整指令
    ```bash
    Usage: ilms view [OPTIONS] 查詢項目

    選擇查詢項目 課程 / 作業 / 上課教材 ['course', 'homework', 'material']

    Options:
        --semester_id TEXT  學期
        --course_id TEXT    課號關鍵字
        --verbose           顯示詳細資訊
        --help              Show this message and exit.
    ```

### 下載 作業 / 上課教材

- 下載所有上課教材, e.g.

    ```bash
    ilms download material --course_id CS35700

    # 只需輸入課號 (course id) 關鍵字
    ilms download material --course_id 35700

    # 只需輸入課程中英文名稱關鍵字
    ilms download material --course 多媒體
    ilms download material --course CVFX

    ```

- [助教模式 TA mode] 下載所有學生作業, e.g.

    ```bash
    ilms download handin --course_id CS35700 --hw_title Homework1
    ```

- 完整指令
    ```bash
    Usage: ilms download [OPTIONS] NAME

    選擇下載項目 上課教材 / 繳交作業 (助教) ['material', 'handin']

    Options:
        --course_id TEXT  課號關鍵字
        --course TEXT     課程名稱關鍵字
        --hw_title TEXT   作業標題
        --folder TEXT     下載至...資料夾
        --help            Show this message and exit.
    ```

### 登記成績

- [助教模式 TA mode] 透過上傳分數 `csv` 檔登記分數, e.g.

    ```bash
    ilms score --course_id CS35700 --hw_title Homework1 --score_csv hw1-cs3570.csv
    ```

- 完整指令
    ```bash
    Usage: ilms score [OPTIONS]

    Options:
        --course_id TEXT  課號關鍵字
        --hw_title TEXT   作業標題
        --csv TEXT        CSV 成績表
        --help            Show this message and exit.
    ```

## 範例程式 API Demo

### 登入 iLms

- You need login for any operations that need privileges.
- login with helper function `get_account()`

```python
from ilms.core import User
from ilms.core import Core as iLms
from ilms.utils import get_account

user = User(*get_account())
assert user.login()

# You can take your profile
profile = ilms.get_profile()

ilms = iLms(user)
```

### 查詢/搜尋課程

```python
# iterate through courses with loop
for cou in ilms.get_courses():
    cou.course_id
    print(cou)

# query with 'keyword', can be coures_id or partial course name in `en` or `zh`
courses = ilms.get_courses()
cou = courses.find(course_id='CS35700')
cou = courses.find(name='視覺特效')
cou = courses.find(name='Pattern Recog')

```

### 下載所有上課教材

```python
for material in cou.get_materials():
    print(material)
    material.download(root_folder='download/cvfx/')
```

### 下載所有繳交作業檔案

```python
from ilms.utils import load_score_csv

homeworks = cou.get_homeworks()
hw1 = homeworks.find(title='Homework1')

hw1.download_handins()
```

### 為作業登記分數

- Use helper function `load_score_csv()` to load the scores in csv file (contains only two columns, `student id` and `score`)
- Can do some processes on the `score_map`, and then use `score_hanins` method to grading in bulk.

```python
from ilms.utils import load_score_csv

homeworks = cou.get_homeworks()
hw1 = homeworks.find(title='Homework1')

score_map = load_score_csv('hw1-cs35700.csv')
score_map = {
    student_id: math.ceil(score)
    for student_id, score in score_map.items()}

hw1.score_handins(score_map)
```

### 完整範例

```python
from ilms.core import User
from ilms.core import Core as iLms


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

### 智慧查詢資料結構 Smart query container

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
