import urllib2
import time
import sys


def measure(url, proxy_address, headers=True):
    if proxy_address:
        proxy = {'http': 'http://{0}'.format(proxy_address),
                 'https': 'https://{0}'.format(proxy_address)}
        proxy_handler = urllib2.ProxyHandler(proxy)
        opener = urllib2.build_opener(proxy_handler)
        urllib2.install_opener(opener)
    req = urllib2.Request(url)
    # req.add_header("Accept", "image/*")
    # req.add_header("Referer", "https://i.imgur.com/")
    # req.add_header("User-agent", 'Mozilla/5.0')
    t = time.time()
    try:
        f = urllib2.urlopen(req)
    except urllib2.URLError as e:
        print e
    else:
        dt = time.time() - t
        if headers:
            print f.info()
        print "response: {}".format(dt)
        t = time.time()
        n = len(f.read())
        dt = time.time() - t
        print "complete: {}".format(dt)
        print "read bytes: {}".format(n)
        print "speed: {} kbps".format(n / dt * 8 / 1000.0)


def options(args):
    proxy_address = None
    url = None
    opts = {"interactive": False, "headers": True}
    for a in args:
        if a == "-i":
            opts["interactive"] = True
        elif a == "-H":
            opts["headers"] = False
        elif url is None:
            url = a
        else:
            proxy_address = a
    return (url, proxy_address, opts)


def interact(url, *args):
    try:
        while True:
            measure(url, raw_input("proxy>> ").strip(), *args)
    except EOFError:
        pass


def main():
    (url, proxy_address, opts) = options(sys.argv[1:])
    if url is None:
        print "proxychecker.py [-i] URL [proxy_address]"
    elif opts["interactive"]:
        interact(url, opts["headers"])
    else:
        measure(url, proxy_address, opts["headers"])


if __name__ == '__main__':
    main()
