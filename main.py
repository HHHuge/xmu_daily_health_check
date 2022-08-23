import json
import os
import time
import argparse
from ids_login import ids_login
from email_sender import MailSenderSmtp

BASE_URL = "https://xmuxg.xmu.edu.cn"
LOGIN_URL = BASE_URL + "/login"
CAS_AUTH_URL = "https://ids.xmu.edu.cn/authserver/login?service=https://xmuxg.xmu.edu.cn/login/cas/xmu"


def get_form_date(form_instance):
    return time.strptime(form_instance["data"]["updateTime"], "%Y-%m-%d %H:%M:%S")


def notify_user(message: str):
    # TODO: Notify the user using Email or Something.
    print(message)
    # username = 'xxxxx@163.com'
    # password = 'xxxxx'
    # receiver = 'xxxx@qq.com'
    # sender = MailSenderSmtp(username, password)
    # sender.send_mail(receiver, "健康打卡消息", message)


def parse_opt(config, opts):
    if not opts:
        return config
    names = [x["name"] for x in config["formData"]]
    titles = [x["title"] for x in config["formData"]]

    for s in opts:
        s = s.strip()
        k, v = s.split('=', 1)

        mod = k.split('.')[0]
        k = ".".join(k.split('.')[1:])
        if mod in names:
            index = names.index(mod)
        elif mod in titles:
            index = titles.index(mod)
        else:
            raise ValueError("{} is not a valid option".format(mod))

        cursor = config["formData"][index]
        while True:
            key = k.split(".")[0]
            k = ".".join(k.split(".")[1:])
            if not k:
                cursor[key] = v
                break

            if key not in cursor:
                cursor[key] = {}
            cursor = cursor[key]

    return config


def parse_args():
    parser = argparse.ArgumentParser(description="XmuXg Notifier")
    parser.add_argument("-u", "--username", help="Username")
    parser.add_argument("-p", "--password", help="Password")
    parser.add_argument("-c", "--config", help="Config File", default="submit.json")
    # allow user to modify the config file using command line arguments
    # example: -o input_1611107369344.value.stringValue="男"
    parser.add_argument("-o", "--opt", nargs="*", help="Set Configuration Options")

    arg = parser.parse_args()
    # get username and password from environment variables if not provided
    if arg.username is None or arg.password is None:
        arg.username = os.getenv("XMUXG_USERNAME")
        arg.password = os.getenv("XMUXG_PASSWORD")
        assert arg.username is not None and arg.password is not None, \
            "Username and Password are required, you can set username and password using -u and -p, " + \
            "or set username and password using environment variables XMUXG_USERNAME and XMUXG_PASSWORD"

    post_data = json.loads(open(arg.config, "r").read())
    # allow user to modify the config file using command line arguments
    post_data = parse_opt(post_data, arg.opt)

    return arg.username, arg.password, post_data


if __name__ == "__main__":
    username, password, post_data = parse_args()
    # Login to IDS
    success, client = ids_login(username, password)
    if not success:
        notify_user("[ERROR] Login to IDS failed")
        exit(1)
    response = client.get(CAS_AUTH_URL, follow_redirects=True)

    # get the daily health check form
    daily_health_check_form_url = BASE_URL + "/api/apps/214/settings/forms"
    my_form_instance_url = BASE_URL + "/api/formEngine/business/2382/myFormInstance"
    client.headers.update({"referer": "https://xmuxg.xmu.edu.cn/app/214"})

    my_form_instance = client.get(my_form_instance_url).json()
    forms = client.get(daily_health_check_form_url).json()

    # ensure the form is the same as previous
    if not os.path.exists("form_template.json"):
        print("[Warning] form_template.json not found, creating a new one")
        with open("form_template.json", "w") as f:
            f.write(json.dumps(forms, indent=4, ensure_ascii=False))

    form_template = open("form_template.json", "r").read()
    if hash(json.dumps(forms, indent=4, ensure_ascii=False)) != hash(form_template):
        message = "[Error] form_template.json is not the same as the latest one"
        notify_user(message)
        raise Exception("form template is not the same as previous one")

    # get the previous form submission time
    last_form_instance_update_time = get_form_date(my_form_instance)
    print("Last update time:", time.strftime("%Y-%m-%d %H:%M:%S", last_form_instance_update_time))
    if time.localtime().tm_year == last_form_instance_update_time.tm_year and \
            time.localtime().tm_mon == last_form_instance_update_time.tm_mon and \
            time.localtime().tm_mday == last_form_instance_update_time.tm_mday:
        print("[Info] Today's form has been submitted, no need to submit again")

    # submit the form
    my_form_instance_id = my_form_instance["data"]["id"]
    [x for x in post_data["formData"] if x["name"] == "datetime_1611146487222"][0]["value"]["dateValue"] = \
        time.strftime("%Y-%m-%d %H:%M:%S", last_form_instance_update_time)
    post_url = BASE_URL + f"/api/formEngine/formInstance/{my_form_instance_id}"
    # post_data = json.loads(open("submit.json", "r").read())
    response = client.post(post_url, json=post_data)
    submit_result = response.json()["data"] == "success"
    if not submit_result:
        message = "[Error] Failed to submit the form"
        notify_user(message)
        raise Exception("Failed to submit the form")

    # check if the form is already submitted
    time.sleep(5)
    my_form_instance = client.get(my_form_instance_url).json()
    my_form_instance_update_time = get_form_date(my_form_instance)
    print("New update time:", time.strftime("%Y-%m-%d %H:%M:%S", my_form_instance_update_time))

    # successfully submit the form
    if time.localtime().tm_year == my_form_instance_update_time.tm_year and \
            time.localtime().tm_mon == my_form_instance_update_time.tm_mon and \
            time.localtime().tm_mday == my_form_instance_update_time.tm_mday:
        message = "[Info] Successfully submitted the form"
    else:
        message = "[Error] Failed to submit the form"
    message += "\n last update time: " + time.strftime("%Y-%m-%d %H:%M:%S", last_form_instance_update_time)
    message += "\n new update time: " + time.strftime("%Y-%m-%d %H:%M:%S", my_form_instance_update_time)
    notify_user(message)
