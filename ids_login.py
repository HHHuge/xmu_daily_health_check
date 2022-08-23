import httpx
from fake_useragent import UserAgent
from httpx_ja3 import SSLFactory
from lxml import etree
from AES import AesEncrypt


def new_client() -> httpx.Client:
    sslgen = SSLFactory()
    client = httpx.Client(headers={"User-Agent": UserAgent().random}, http2=True, verify=sslgen())
    return client


def ids_login(uname: str, pwd: str, client: None or httpx.Client = None):
    BASE_URL = "https://ids.xmu.edu.cn"
    IDS_URL = BASE_URL + "/authserver/login"

    if client is None:
        client = new_client()

    response = client.get(IDS_URL)
    html = etree.HTML(response.text)
    hidden_inputs = html.xpath("//form//input[@type='hidden']")
    hidden_inputs = {input.get("name", input.get("id")): input.attrib["value"] for input in hidden_inputs}
    data = hidden_inputs.copy()
    salt = data["pwdDefaultEncryptSalt"]
    data.update({"username": uname, "password": AesEncrypt(salt).encrypt(pwd)})
    response = client.post(IDS_URL, data=data)
    return response.status_code == 302, client


if __name__ == "__main__":
    UNAME = "xxxxx"
    PWD = "xxxxx"
    success, client = ids_login(UNAME, PWD)
    print(success)
    print(client.headers)
    print(client.cookies)
