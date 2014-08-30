 #!/bin/bash
 for i in `seq 0 9999`;
 do
     echo "curl web.archive.org/web/timemap/link/http://www.stackoverflow.com/users/$i* > $i-"
     curl web.archive.org/web/timemap/link/http://www.stackoverflow.com/users/$i* > $i-
 done 