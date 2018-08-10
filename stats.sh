 #!/bin/bash
 find . -regextype posix-egrep -regex ".*\.(py|enbf|ray|sh)$" | xargs wc