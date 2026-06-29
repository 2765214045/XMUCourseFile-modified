import os
import json
import requests as r
from tqdm import tqdm
from wcwidth import wcwidth

# from qrcodeLogin import get_session
from passwdLogin import get_session

#import

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


def sanitize_filename(name: str) -> str:
    # Replace characters that are invalid on Windows file systems.
    for ch in '<>:"/\\|?*':
        name = name.replace(ch, "_")
    return name.strip()


def download(url: str, fname: str):
    resp = r.get(url, stream=True, headers=headers, timeout=30)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))

    directory = os.path.dirname(fname)
    if directory and not os.path.exists(directory):
        print(f"目录 '{directory}' 不存在，正在创建...")
        os.makedirs(directory, exist_ok=True)#create dir

    with open(fname, "wb") as file, tqdm(
        desc=fname.split("/")[-1],
        total=total,
        unit="iB",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)


def while_get(url):
    ret = None
    while True:
        ret = session.get(url, headers=headers, timeout=30)
        if ret.ok:
            break
        else:
            try:
                if ret.json()["message"] == "您没有权限完成此操作":
                    print("请确认cookie输入是否正确！")
                    exit(0)
            except:
                print(ret.text)
                print("无效访问")
                exit(0)
    return ret


def response_json(resp):
    # Some endpoints return UTF-8 BOM, which breaks requests.Response.json().
    return json.loads(resp.text.lstrip("\ufeff"))


os.system("md download >nul 2>nul")

session = get_session()
print("登录成功")
course_l_n=[];p=0;course_l_id=[]
data_c=response_json(while_get(f"https://lnt.xmu.edu.cn/api/my-courses"))
for k in data_c["courses"]:
    course_l_n.append(k["name"])
    course_l_id.append(k["id"])
    p+=1
#course

def get_display_width(s):
    return sum(wcwidth(char) for char in s)
if not course_l_n:
    print("未获取到课程列表，请确认账号权限或稍后重试。")
    raise SystemExit(1)

max_name_width = max(get_display_width(name) for name in course_l_n)
with open("courses.txt", "w", encoding="utf-8") as f:
    header = f"{'序号':<5}{'课程名':<{max_name_width}}{'id':<10}\n"
    print(header.strip())
    f.write(header)
    for i, (name, num) in enumerate(zip(course_l_n, course_l_id), start=1):
        name_width = get_display_width(name)
        padding = max_name_width - name_width
        line = f"{i:<5}{name}{' ' * padding}\t{num:<10}\n"
        f.write(line)
        print(line.strip())
#print and save
q=0
while(1):
    choice = input("请输入下载的课程序号：").strip()
    if not choice.isdigit():
        print("输入无效，请输入数字序号。")
        continue

    course_index = int(choice) - 1
    if course_index < 0 or course_index >= len(course_l_id):
        print("序号超出范围，请重新输入。")
        continue

    course_id = course_l_id[course_index]


    if(q>=0):print("下载完成数量",q,"，Ctrl+C 退出程序")

    data_n=response_json(while_get(f"https://lnt.xmu.edu.cn/api/courses/{course_id}"))
    name_of_course=data_n["display_name"]
    safe_course_name = sanitize_filename(name_of_course)
    #name of course

    data = response_json(while_get(f"https://lnt.xmu.edu.cn/api/courses/{course_id}/activities"))

    for e in data["activities"]:
        for i in e["uploads"]:
            reference_id = i["reference_id"]
            name = sanitize_filename(i["name"])
            content = while_get(
                f"https://lnt.xmu.edu.cn/api/uploads/reference/{reference_id}/url"
            )
            content = response_json(content)
            url = content["url"]
            download(url, f"./download/{course_id}-{safe_course_name}/{name}")
            q+=1





    #keyboard.wait('esc')



