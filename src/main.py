import asyncio
import json
import random
import re
import time
from textwrap import dedent
from typing import Any, Dict, List, Union

import requests


def login():
    '''登录，cookie由session处理
    
    如果登录失败直接退出
    '''
    print(dedent('''\
        **********  Created By Avenshy & SSmJaE  **********
                        Version : 0.3.0
           基于GPL3.0，完全开源，免费，禁止二次倒卖或商用
                    经改动后，适用于只刷课文
           https://www.github.com/Avenshy/WELearnToSleeep
                        仅供学习，勿滥用
        ***************************************************
    '''))

    username = input('Username: ')
    password = input('Password: ')

    print('Login...', end=' ')
    response = session.get(
        'https://sso.sflep.com/cas/login?service=http%3a%2f%2fwelearn.sflep.com%2f2019%2fuser%2floginredirect.aspx')
    lt = re.search('name="lt" value="(.*?)"', response.text).group(1)

    response = session.post(
        'https://sso.sflep.com/cas/login?service=http%3a%2f%2fwelearn.sflep.com%2f2019%2fuser%2floginredirect.aspx',
        data={
            'username': username,
            'password': password,
            'lt': lt,
            '_eventId': 'submit',
            'submit': 'LOGIN'
        }
    )

    if '请登录' in response.text:
        input('Fail!!')
        exit(0)
    else:
        print('Success!!\n\n')


def get_target_course_info():
    global cid, uid, classid, courseInfo

    # get course list
    response = session.get(
        'https://welearn.sflep.com/ajax/authCourse.aspx?action=gmc',
        headers={
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; Mi 10 Pro Build/RKQ1.200826.002)",
            'Referer': 'https://welearn.sflep.com/2019/student/index.aspx'
        }
    )
    courseList = response.json()['clist']
    print('\n')
    for index, course in enumerate(courseList, start=1):
        print('[id:{:>2d}]  完成度 {:>3d}%  {}'.format(index, course['per'], course['name']))

    #  get cid(course id) and uid(user id) and class id
    index = int(input('\n请输入需要刷时长的课程id（id为上方[]内的序号）: '))
    cid = str(courseList[index - 1]['cid'])
    response = session.get(
        'https://welearn.sflep.com/2019/student/course_info.aspx?cid=' + cid,
        headers={
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; Mi 10 Pro Build/RKQ1.200826.002)",
            'Referer': 'https://welearn.sflep.com/2019/student/index.aspx'
        }
    )
    uid = re.search('"uid":(.*?),', response.text).group(1)
    classid = re.search('"classid":"(.*?)"', response.text).group(1)

    # get target course's units
    req = session.get(
        'https://welearn.sflep.com/ajax/StudyStat.aspx',
        params={
            'action': 'courseunits',
            'cid': cid,
            'uid': uid
        },
        headers={
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; Mi 10 Pro Build/RKQ1.200826.002)",
            'Referer': 'https://welearn.sflep.com/2019/student/course_info.aspx'
        }
    )
    courseInfo = req.json()['info']


def choose_unit():
    global unitIndex

    print("\n\n")
    print('[id: 0]  按顺序刷全部单元学习时长')
    for index, unit in enumerate(courseInfo, start=1):
        print(f"""[id:{index:>2d}]  {unit['unitname']}  {unit['name']}""")

    print("\n\n")
    unitIndex = int(input('请选择要刷时长的单元id（id为上方[]内的序号，输入0为刷全部单元）： '))


def input_time():
    global targetTime

    print("\n\n")
    print(dedent('''\
        模式1:每个练习增加指定学习时长，请直接输入时间
        如:希望每个练习增加30秒，则输入 30
        模式2:每个练习增加随机时长，请输入时间上下限并用英文逗号隔开
        如:希望每个练习增加10～30秒，则输入 10,30
    '''))
    print("\n\n")

    input_ = input("请严格按照以上格式输入: ")
    if(',' in input_):
        try:
            targetTime = [int(temp) for temp in input_.split(',')]
        except:
            print("格式异常")
            exit(0)
    else:
        targetTime = int(input_)


def generate_learning_time():
    """每一次模拟都重新生成一次随机学习时间"""
    global targetTime

    if type(targetTime) is int:
        learntime = targetTime
    else:
        learntime = random.randint(targetTime[0], targetTime[1])
    return learntime


def output_results():
    print('运行结束!!\n错误:', len(errors), '个')
    for index, error in enumerate(errors, start=1):
        print(f"第{index}个错误:{ error}")

    print("\n\n")
    print(dedent('''\
        **********  Created By Avenshy & SSmJaE  **********
                        Version : 0.3.0
           基于GPL3.0，完全开源，免费，禁止二次倒卖或商用
                    经改动后，适用于只刷课文
           https://www.github.com/Avenshy/WELearnToSleeep
                        仅供学习，勿滥用
        ***************************************************
    '''))
    print("\n\n")
    input("Press any key to exit...")


async def simulate(learningTime: int, chapter: Dict):
    print(f"""章节 : {chapter['location']}""")
    print(f"""已学 : {chapter['learntime']} 将学 : {learningTime}""")

    commonHeaders = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; Mi 10 Pro Build/RKQ1.200826.002)",
        'Referer': 'https://welearn.sflep.com/student/StudyCourse.aspx'
    }

    scoid = chapter['id']
    # print(scoid)
    commonData = {
        'uid': uid,
        'cid': cid,
        'scoid': scoid
    }

    await asyncio.sleep(REQUEST_INTERVAL)
    response = session.post(
        AJAX_URL,
        data={
            **commonData,
            'action': 'getscoinfo_v7',
        },
        headers=commonHeaders
    )

    if('学习数据不正确' in response.text):  # 重试
        await asyncio.sleep(REQUEST_INTERVAL)

        response = session.post(
            AJAX_URL,
            data={
                **commonData,
                'action': 'startsco160928',
            },
            headers=commonHeaders
        )
        response = session.post(
            AJAX_URL,
            data={
                **commonData,
                'action': 'getscoinfo_v7',
            },
            headers=commonHeaders
        )

        if('学习数据不正确' in response.text):
            print('\n错误:', chapter['location'])
            errors.append(chapter['location'])
            return

    returnJson = response.json()['comment']
    if('cmi' in returnJson):
        cmi = json.loads(returnJson)['cmi']

        crate = cmi['score']['scaled']
        cstatus = cmi['completion_status']
        progress = cmi['progress_measure']
        total_time = cmi['total_time']
        session_time = cmi['session_time']
    else:
        crate = ''
        cstatus = 'not_attempted'
        progress = '0'
        total_time = '0'
        session_time = '0'

    await asyncio.sleep(REQUEST_INTERVAL)
    session.post(
        AJAX_URL,
        data={
            **commonData,
            'action': 'keepsco_with_getticket_with_updatecmitime',
            'session_time': session_time,
            'total_time': total_time
        },
        headers=commonHeaders
    )

    for currentTime in range(1, learningTime + 1):
        await asyncio.sleep(1)

        if(currentTime % 60 == 0):
            session.post(
                AJAX_URL,
                data={
                    **commonData,
                    'action': 'keepsco_with_getticket_with_updatecmitime',
                    'session_time': session_time,
                    'total_time': total_time},
                headers=commonHeaders
            )

    await asyncio.sleep(REQUEST_INTERVAL)
    session.post(
        AJAX_URL,
        data={
            **commonData,
            'action': 'savescoinfo160928',
            'crate': crate,
            'cstatus': cstatus,
            'status': 'unknown',
            'progress': progress,
            'trycount': '0'
        },
        headers=commonHeaders
    )


async def heartbeat():
    startTime = time.time()
    for _ in range(maxLearningTime+4*REQUEST_INTERVAL):
        print(
            f"""\r预计学习时长 : {maxLearningTime+4*REQUEST_INTERVAL} 已学习时长 : {int(time.time()-startTime)}""", end="")
        await asyncio.sleep(HEARTBEAT_INTERVAL)


async def watcher():
    global maxLearningTime

    onlytext = int(input('\n请输入数字，表示是否只刷两篇课文（1表示只刷课文，其他表示全部刷）: '))
    while True:
        get_target_course_info()
        choose_unit()
        input_time()

        if(unitIndex == 0):
            startIndex = 0
            endIndex = len(courseInfo)
        else:
            startIndex = unitIndex-1
            endIndex = unitIndex

        tasks = []
        for unit in range(startIndex, endIndex):
            response = session.get(
                f"https://welearn.sflep.com/ajax/StudyStat.aspx?action=scoLeaves&cid={cid}&uid={uid}&unitidx={str(unit)}&classid={classid}",
                headers={
                    "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; Mi 10 Pro Build/RKQ1.200826.002)",
                    'Referer': 'https://welearn.sflep.com/2019/student/course_info.aspx?cid=' + cid
                }
            )

            for chapter in response.json()['info']:
                learningTime = generate_learning_time()

                if learningTime > maxLearningTime:
                    maxLearningTime = learningTime

                # print(chapter['id'])
                res = re.match(r'm-\d-\d-(\d*)', chapter['id'])
                rss = res.group(1)
                # print(rss)
                rss = int(rss)
                if onlytext == 1:
                    if rss == 4:
                        tasks.append(asyncio.create_task(simulate(learningTime, chapter)))
                    elif rss == 16:
                        tasks.append(asyncio.create_task(simulate(learningTime, chapter)))
                else:
                    tasks.append(asyncio.create_task(simulate(learningTime, chapter)))

        await heartbeat()
        [await task for task in tasks]

        if (unitIndex == 0):  # 如果已经刷完所有单元
            break
        else:  # 如果只刷了指定单元
            print("\n\n")
            print(f'本单元结束！错误 : {len(errors)}个')

            for index, error in enumerate(errors, start=1):
                print(f"第{index}个错误章节 : {error}")

            print('回到选课处！！')
            print("\n\n")
            maxLearningTime = 0


async def main():
    await asyncio.gather(
        watcher()
    )


if __name__ == "__main__":
    REQUEST_INTERVAL = 2
    HEARTBEAT_INTERVAL = 1
    AJAX_URL = "https://welearn.sflep.com/Ajax/SCO.aspx"

    cid: str
    uid: str
    classid: str
    courseInfo: List[Any]
    unitIndex: int
    targetTime: Union['int', List['int']]

    errors: List[str] = []
    maxLearningTime: int = 0
    session = requests.Session()

    login()
    asyncio.run(main())
    output_results()
