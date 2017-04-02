# iLMS NTHU

An iLMS client for stduents, assistants and developers.

## Install

```bash
pip install -U ilms-nthu
```

*Note: develop and test on Python3.5+*


## Sample code

```python
from ilms.ilms import User
from ilms.ilms import System as iLms

    user = User('<user_id>', '<password>')
    assert user.login()

    ilms = iLms(user)

    profile = ilms.get_profile()

    for cou in ilms.get_courses():

        for homework in cou.get_homeworks():

            for handin in homework.handin_list:
                pprint(handin.detail)
                handin.download()

        for material in cou.get_materials():
            print(material.detail)
            material.download()

        print(cou.get_forum_list().result)
```
