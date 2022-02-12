import os, time, re, threading

ips = {}


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+8 to toggle the breakpoint.


def line_check(filepath):
    file = open(filepath, "r")
    notempty = [line.strip("\n") for line in file if line != "\n"]
    file.close()
    return len(notempty)


def unblock_ip(ip_addr):
    print("Unblocking ", ip_addr)
    cmd = "iptables -A INPUT -s " + ip_addr + " ip -j DROP"
    os.system(cmd)
    return


def block_ip(ip_addr):
    print("Over limit, blocking ", ip_addr)
    cmd = "iptables -D INPUT -s " + ip_addr + " ip -j DROP"
    os.system(cmd)
    return


def ip_check(ip):
    if ip in ips:
        return True
    else:
        return False


def ip_get(line):
    ip_pat = "from (.*?) port"
    ip = re.search(ip_pat, line).group(1)
    return ip


def read_last_updates(filepath, LIMIT, TIMEOUT, new_lines):
    file = open(filepath, "r")
    base_check = "sshd"
    pass_check = "Failed password for"
    accepted_check = "Accepted password for"
    id_pat = "\[(.*?)\]"

    ip = "0"
    i = 0

    Lines = file.readlines()
    for line in reversed(Lines):
        i += 1
        if base_check in line:
            if pass_check in line:

                id = int(re.search(id_pat, line).group(1))
                ip = ip_get(line)
                if ip_check(ip):
                    # print(attempts, " ", id)
                    ips[ip] += 1
                    if ips[ip] >= LIMIT:
                        block_ip(ip)
                        threading.Timer(TIMEOUT, unblock_ip, [ip])
                        return
                else:
                    ips[ip] = 1
            elif accepted_check in line:
                ip = ip_get(line)
                if ip_check(ip):
                    del ips[ip]

        if i == new_lines:
            return


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    filepath = "/var/log/secure"
    line_count = line_check(filepath)
    LIMIT = int(input("Enter number of attempts before blocking ip: "))
    TIMEOUT = int(input("Enter time limit for blocking(leave blank for indefinite): "))

    while True:

        check_line = line_check(filepath)
        if check_line != line_count:
            line_dif = check_line - line_count
            line_count = check_line
            read_last_updates(filepath, LIMIT, TIMEOUT, line_dif)

        else:
            continue
    # print("no update")

    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
