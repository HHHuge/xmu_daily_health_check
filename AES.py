import execjs


class AesEncrypt:
    def __init__(self, key):
        self.key = key

        with open("encrypt.js", "r") as f:
            js_script = f.read()
        self.ctx = execjs.compile(js_script)

    def encrypt(self, data):
        return self.ctx.call("encryptAES", data, self.key)


if __name__ == "__main__":
    encrypter = AesEncrypt("y6gzd713fcXOXags")
    print(encrypter.encrypt("123456"))
