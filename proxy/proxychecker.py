import urllib2
import time
import sys


def measure(url, proxy_address):
    if proxy_address:
        proxy = {'http': 'http://{0}'.format(proxy_address),
                 'https': 'https://{0}'.format(proxy_address)}
        proxy_handler = urllib2.ProxyHandler(proxy)
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
    req = urllib2.Request(url)
    #req.add_header("Accept", "image/*")
    #req.add_header("Referer", "https://i.imgur.com/")
    #req.add_header("User-agent", 'Mozilla/5.0')
    t = time.time()
    try:
        f = urllib2.urlopen(req)
    except urllib2.URLError as e:
        print e
    else:
        dt = time.time() - t
        print f.info()
        print dt
        t = time.time()
        n = len(f.read())
        print n
        dt = time.time() - t
        print dt
        print n / dt * 8 / 1000.0, "kbps"


def main():
    proxy_address = ""
    url = ""
    if len(sys.argv) > 2:
        proxy_address = sys.argv[2]
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print "proxychecker.py URL [proxy_address]"
    measure(url, proxy_address)


if __name__ == '__main__':
    main()
