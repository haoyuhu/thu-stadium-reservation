## required
* requests: http://docs.python-requests.org/en/master/
* pywin32: https://sourceforge.net/projects/pywin32/files/pywin32/
* pycrypto: https://pypi.python.org/pypi/pycrypto

## `unit`
* `time`: 时间单位为`second/minute/hour`；
* `week`: 从周一至周日分别对应0-6；
* `section`: 早上8:00-12:00，下午12:00-18:00，晚上18:00-22:00。

## `candidates`
* `candidates`为一个主列表；
* 主列表每个元素均为一个子列表，称为任务组，任务组中各任务的时间互斥，当程序完成其中一个预订任务后就会标记该任务组已完成；
* 主列表的任务组之间不互斥，可以约定多个场地；

## 任务详细参数
* `week`为周次对应的`index`;
* `wish`为期望的起始和终止时间;
* `length`为持续时长;
* `section`为时间段（早上、下午、晚上）;
* `fixed`为是否强制采用`wish`规定的起止时间。当`fixed`为`false`时，当没有找到符合`wish`的空余场地时，会在规定的`section`时间段内寻找符合`length`的空余场地。

## accounts.json
```
{
  "your_name": {
    "id": "your_student_id",
    "username": "your_username",
    "password": "your_password",
    "phone": "your_phone_number",
    "user_type": "student"
  },
  "other_name": {
    "id": "other_student_id",
    "username": "other_username",
    "password": "other_password",
    "phone": "other_phone_number",
    "user_type": "student"
  }
}
```