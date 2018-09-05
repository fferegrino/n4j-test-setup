# n4j-test-setup
"Stress-testing" the feature introduced in https://github.com/fferegrino/neo4j

### 1. Prepare the Neo4j instances

Create a folder to host the three different instances of Neo4j. For example: `~/flights/neo4j`

#### Plain Neo4j 

1. Download Neo4j 3.4.0 and place it in the chosen folder
2. Replace the file 

#### Neo4j with APOC plugins

1. Download Neo4j 3.4.0 and place it in the chosen folder
2. Replace the file 

#### Neo4j with Document support

1. Download the source code for Neo4j with Document support from:
2. In the root directory generate the binaries for Neo4j using the following command:
```
mvn clean install -DskipTests -Drevapi.skip=true
```
3. From the folder `packaging/standalone/target` and extract the binaries for Unix

### 2. Prepare the data set  

1. Download the data set from this link:
2. Extract the contents of that file to an empty folder, so that there are at least three different *csv* files (for example `~/flights/delays/`)

### 3. Configure the Web server (optional)

If you wish to modify the execution port of the web application modify the line 50 in the file `Web.py` to run in other port different than `8888`.

### 4. Modify the file `run.sh` 

This is needed to make it point to the right directories, from the line 8 to 11:

 - **neo4jloc** (line 8), this needs to point to the location where the three different instances of Neo4j exist:, for example: `neo4jloc=~/flights/neo4j`
 - **dataloc** (line 9), this needs to be an absolute route pointing to the folder that contains the three different csv files, for example: `dataloc="/home/dspg17/flights/delays/"`.
- **resultsloc** (line 10), this is the route to an already existing folder where you want the results to be placed, for example: `resultsloc=~/flights/test/results`
- **webendpoint** (line 11), if you modified the Web.py file in the step #3, you need to change the address, if not, leave the configuration by default, for example:`webendpoint="http://localhost:8888"`

### 5. Run the web application

Execute the web server using the following command: 

```
python Web.py
```

### 6.  Execute the `run.sh` script

The script requires a single parameter: the number of times you want the different executions to run, for example to execute 5 rounds of insertions and retrievals, the following command should be used

```
sh run.sh 5
```

