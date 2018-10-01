#!/usr/bin/env python3

import sys
import re

SPLUNKWEB_PATTERN = r'^(?P<client>\S+) (?P<userid>\S+) \S+ \[(?P<datetime>[^\.]+).[^\]]+\] "(?P<method>[A-Z]+)(?P<request>[^"]+)?HTTP/[0-9.]+" (?P<status>[0-9]{3}) (?P<size>[0-9]+|-) "(?P<referrert>[^"]*)" "(?P<user_agent>[^"]+)".*$'
TARGET_FORMAT = r'\g<client> - \g<userid> [\g<datetime> +0000] "\g<method>\g<request>HTTP/1.1" \g<status> \g<size>'

first = True
for line in sys.stdin:
    line = re.sub(SPLUNKWEB_PATTERN, TARGET_FORMAT, line)
    if not first:
        line = '\n' + line 
    sys.stdout.write(line)
    sys.stdout.flush()
