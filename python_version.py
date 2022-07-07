from re import findall
import json
from requests import *
import time

my_headers = {
    'Referer': 'http://login.sust.edu.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53'
}
HOST = "http://bkjw.sust.edu.cn"

COMMENT_LIST_URL = HOST + "/eams/quality/stdEvaluate.action?_=1609766969972"
COMMENT_SUBMIT_URL = HOST + "/eams/quality/stdEvaluate!finishAnswer.action"
evaluationLessonRegex = "(?<=evaluationLesson.id=).*?(?=\")"
headers = {
    'Host': 'bkjw.sust.edu.cn',
    'Connection': 'keep-alive',
    'Content-Length': '10355',
    'Accept': '*/*',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'http://bkjw.sust.edu.cn',
    'Referer': 'http://bkjw.sust.edu.cn/eams/quality/stdEvaluate!answer.action?evaluationLesson.id=35583&teacher.id=326321',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,vi;q=0.5',
}


def get_xsrf() -> dict:
    """
    :return:
    """
    url_xs = 'http://login.sust.edu.cn/cas/login?service=http%3A%2F%2Fbkjw.sust.edu.cn%3A80%2Feams%2Fsso%2Flogin.action%3FtargetUrl%3Dbase64aHR0cDovL2Jrancuc3VzdC5lZHUuY246ODAvZWFtcy9ob21lLmFjdGlvbg%3D%3D'
    req_xs = get(url=url_xs, headers=my_headers)
    return req_xs.cookies.get_dict()


def get_cookies(User: dict) -> dict:
    """
    :param User:
    :return:
    """
    url = 'http://login.sust.edu.cn/cas/login?service=http%3A%2F%2Fbkjw.sust.edu.cn%3A80%2Feams%2Fsso%2Flogin.action%3FtargetUrl%3Dbase64aHR0cDovL2Jrancuc3VzdC5lZHUuY246ODAvZWFtcy9ob21lLmFjdGlvbg%3D%3D'
    data = {
        'username': User['user'],
        'password': User['password'],
        'currentMenu': '1',
        'execution': 'e1s1',
        '_eventId': 'submit',
        'geolocation': '',
        'submit': '稍等片刻……'.encode(),
        # 'execution': get_execution()
    }
    my_cookies = get_xsrf()
    req_add = post(url=url, data=data, cookies=my_cookies, allow_redirects=False)
    if req_add.status_code == 401:
        print("密码错误")
        return None
    else:
        print("登录成功")
    header = req_add.headers
    header[
        'User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36 Edg/94.0.992.31'
    response = get(url=req_add.url, headers=header, cookies=req_add.cookies.get_dict(), allow_redirects=True)
    cookie: dict[str, str] = {}
    for i in response.request.headers['Cookie'].split(';'):
        i = list(i.strip().split('='))
        if i[0] == 'TGC':
            continue
        cookie[i[0]] = i[1]
    return cookie


def packet_callback(teacher_id, lesson_id) -> dict:
    """
    :param teacher_id:
    :param lesson_id:
    :return:
    """
    info = {'teacher.id': str(teacher_id),
            'semester.id': '162',
            'evaluationLesson.id': str(lesson_id),
            'result1_0.questionName': '教师责任心强，对学生有爱心，耐心。（4分））',
            'result1_0.questionType': '教学态度',
            'result1_0.content': 'D 4',
            'result1_0.score': '4',
            'result1_1.questionName': '教师治学严谨，认真负责精神饱满，讲课有热情。（4分）',
            'result1_1.questionType': '教学态度',
            'result1_1.content': 'D 4',
            'result1_1.score': '4',
            'result1_2.questionName': '既教书又育人，注意对学生的教育引导，以身作则。（4分）',
            'result1_2.questionType': '教学态度',
            'result1_2.content': 'D 4',
            'result1_2.score': '4',
            'result1_3.questionName': '教师遵守教学纪律，无迟到、提前下课、随意调停课情况。（3分）',
            'result1_3.questionType': '教学态度',
            'result1_3.content': 'C 3',
            'result1_3.score': '3',
            'result1_4.questionName': '备课认真，教学目标明确，教学内容完备、充实、无科学性、政策性错误。利用优质教学资源，适用性强。（7分）',
            'result1_4.questionType': '教学内容',
            'result1_4.content': 'G 7',
            'result1_4.score': '7.000000000000001',
            'result1_5.questionName': '坚持立德树人，课程融入思想政治教育元素（教师挖掘各门专业课程所蕴含的思想政治教育元素，把做人做事的基本道理、社会主义核心价值观的要求、实现民族复兴的理想和责任融入专业课程教学中）。（7分）',
            'result1_5.questionType': '教学内容',
            'result1_5.content': 'G 7',
            'result1_5.score': '7.000000000000001',
            'result1_6.questionName': '对标高阶性、创新性和挑战度要求，推动金课建设之高阶性指能够把知识、能力、素质有机融合，培养解决复杂问题的综合能力和高级思维。（7分）',
            'result1_6.questionType': '教学内容',
            'result1_6.content': 'G 7',
            'result1_6.score': '7.000000000000001',
            'result1_7.questionName': '对标高阶性、创新性和挑战度要求，推动金课建设之创新性是指课程内容要反映前沿性和时代性，教学形式呈现先进性和互动性，学习结果具有探究性和个性化。（7分）',
            'result1_7.questionType': '教学内容',
            'result1_7.content': 'G 7',
            'result1_7.score': '7.000000000000001',
            'result1_8.questionName': '对标高阶性、创新性和挑战度要求，推动金课建设之挑战度是指课程有一定难度，需要跳一跳才能够得着，老师备课和学生课下有较高要求。（7分）',
            'result1_8.questionType': '教学内容',
            'result1_8.content': 'G 7',
            'result1_8.score': '7.000000000000001',
            'result1_9.questionName': '理论联系实际，能结合学生、社会需求的实际组织教学，善于启发思维。（5分）',
            'result1_9.questionType': '教学方法手段',
            'result1_9.content': 'E 5',
            'result1_9.score': '5',
            'result1_10.questionName': '教学设计合理，板书规范、布局有规划，多媒体和板书融合自然、互为有益补充。有效利用信息化手段，加大课程改革创新。（5分）',
            'result1_10.questionType': '教学方法手段',
            'result1_10.content': 'E 5',
            'result1_10.score': '5',
            'result1_11.questionName': '创新方式方法选择恰当，初步形成一定的创新型教育模式，实现了“以学生为中心，产出为导向，持续改进”教学理念。（10分）',
            'result1_11.questionType': '教学方法手段',
            'result1_11.content': 'J 10',
            'result1_11.score': '10',
            'result1_12.questionName': '课堂讲授富有吸引力，学生思维活跃，师生互动充分，探究有深度。（5分）',
            'result1_12.questionType': '教学方法手段',
            'result1_12.content': 'E 5',
            'result1_12.score': '5',
            'result1_13.questionName': '课堂教学组织严密，时间安排合理，张弛得当。（4分）',
            'result1_13.questionType': '教学管理',
            'result1_13.content': 'D 4',
            'result1_13.score': '4',
            'result1_14.questionName': '善于管理，师生关系和谐。（3分）',
            'result1_14.questionType': '教学管理',
            'result1_14.content': 'C 3',
            'result1_14.score': '3',
            'result1_15.questionName': '敢于管理，课堂纪律好。（3分）',
            'result1_15.questionType': '教学管理',
            'result1_15.content': 'C 3',
            'result1_15.score': '3',
            'result1_16.questionName': '完成教学计划，多数学生能够接受并掌握课程的主要内容。（5分）',
            'result1_16.questionType': '教学效果',
            'result1_16.content': 'E 5',
            'result1_16.score': '5',
            'result1_17.questionName': '学生能初步运用所学知识解决实际问题。（3分）',
            'result1_17.questionType': '教学效果',
            'result1_17.content': 'C 3',
            'result1_17.score': '3',
            'result1_18.questionName': '学生学习能力、动手能力、创新能力和综合素质有提高。（2分）',
            'result1_18.questionType': '教学效果',
            'result1_18.content': 'B 2',
            'result1_18.score': '2',
            'result1_19.questionName': '进行全方位、多形式、分阶段考核方式；考核评价嵌入教学全过程。（5分）',
            'result1_19.questionType': '教学效果',
            'result1_19.content': 'E 5',
            'result1_19.score': '5',
            'result2_0.questionName': '您对该教师有何建议',
            'result2_0.questionType': '课程建议',
            'result2_0.content': '无',
            'result2_1.questionName': '您对本门课程的开设有何建议？',
            'result2_1.questionType': '课程建议',
            'result2_1.content': '无',
            'result1Num': '20',
            'result2Num': '2'}

    return info


def get_comment_list_page(cookie) -> None:
    """
    :param cookie:
    :return:
    """
    response = post(COMMENT_LIST_URL, cookies=cookie)
    COMMENT_LIST = findall(evaluationLessonRegex, response.text)
    cookie['semester.id'] = 162
    if len(COMMENT_LIST) == 0:
        print('不存在需要评教的课程')
        return
    else:
        print('存在评教的课程数量为:', len(COMMENT_LIST))

    headers[
        'Cookie'] = f"GSESSIONID={cookie['GSESSIONID']}; JSESSIONID={cookie['JSESSIONID']}; QINGCLOUDELB={cookie['QINGCLOUDELB']}; semester.id=162"

    cookie['semester.id'] = '162'
    for i in COMMENT_LIST:
        print(i)
        Lesson_id = i[0:i.index('&')]
        Teacher_id = i[i.index('=') + 1:]
        print('课程id:' + Lesson_id + '\t教师id:' + Teacher_id)

        documents = post(COMMENT_SUBMIT_URL, headers=headers, cookies=cookie,
                         data=(packet_callback(Teacher_id, Lesson_id)), allow_redirects=False)

        if documents.status_code != 302:
            print('评教失败')
        else:
            print('评教成功')

        time.sleep(1)

    verify_response = post(COMMENT_LIST_URL, cookies=cookie)
    verify_LIST = findall(evaluationLessonRegex, response.text)
    if verify_LIST==0:
        print('评教结束')
    else:
        print('未评教科目数量:',len(verify_LIST))
        print("请尝试重新开始评教")
    return


def main(user: dict) -> None:
    """
    :param user:
    :return:
    """
    Cookie = get_cookies(user)
    if Cookie != None:
        # print(Cookie)
        get_comment_list_page(Cookie)


if __name__ == '__main__':
    users = [{
        'name': 'yourNickName',
        'user': "youraccount",
        'password': 'yourpassword'
    }
    ]
    for user in users:
        print('用户name:' + user['name'])
        main(user)
