echo "Start"
date
iters=$1

current="`date +%m%d%H%M`";
counter=1

neo4jloc=~/flights/neo4j
dataloc="/home/dspg17/flights/delays/"
resultsloc=~/flights/test/results
webendpoint="http://localhost:8888"
resultsfile=$resultsloc/results-$current.txt

declare -a limits=(10000 50000 100000 200000 500000 1000000)
declare -a instances=("3.4.0-plain" "3.4.0-apoc" "3.5.0-maps")

curl $webendpoint/load -d "location=$dataloc" -XGET

touch $resultsfile

while [ $counter -le $(($iters)) ]
do
    for limit in "${limits[@]}"
    do
        for instance in "${instances[@]}"
        do
            DATE=`date '+%Y-%m-%d %H:%M:%S'`
            echo "Start $DATE: \t$instance \t$counter\t$limit"

            #make clean
            rm -rf $neo4jloc/installation-$instance/data/*
            $neo4jloc/installation-$instance/bin/neo4j-admin set-initial-password tokyo > /tmp/neostart
            #make start
            $neo4jloc/installation-$instance/bin/neo4j start > /tmp/neostart

            printf "%d\t" "$counter" >> $resultsfile
            curl -s $webendpoint/other -d "location=$dataloc&instance=$instance" -XGET >> $resultsfile
            printf "%d\t" "$counter" >> $resultsfile
            curl -s $webendpoint/flights -d "location=$dataloc&instance=$instance&flights=$limit" -XGET >> $resultsfile

            sleep 5

            #make stop
            $neo4jloc/installation-$instance/bin/neo4j stop > /tmp/neostop
            
            DATE=`date '+%Y-%m-%d %H:%M:%S'`
            echo "End $DATE: \t$instance \t$counter\t$limit"
            date
            
        done
    done
    ((counter++))
done
echo "I'm done!"
