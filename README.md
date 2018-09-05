## Test preparation

### 1. Prepare the Neo4j instances

Create a folder to host the three different instances of Neo4j. For example: `~/flights/neo4j`, this will be known as the *parent* folder.

#### Plain Neo4j 

1. Download Neo4j 3.4.0 and place it in the *parent* folder
2. Rename the folder containing it to `installation-3.4.0-plain`
3. Replace the contents of the file `installation-3.4.0-plain/conf/neo4j.conf` for the ones given in [this file](https://github.com/fferegrino/n4j-test-setup/blob/master/conf-files/neo4j-plain.conf).

#### Neo4j with APOC plugins

1. Download Neo4j 3.4.0 and place it in the *parent* folder
2. Rename the folder containing it to `installation-3.4.0-apoc`
3. Download the APOC plugins from this url [https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/tag/3.4.0.2](https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/tag/3.4.0.2) and paste them in the folder `installation-3.4.0-apoc/plugins` 
4. Replace the contents of the file `installation-3.4.0-apoc/conf/neo4j.conf` for the ones given in [this file](https://github.com/fferegrino/n4j-test-setup/blob/master/conf-files/neo4j-apoc.conf).

#### Neo4j with Document support

1. Download the source code for Neo4j with Document support from this release: [https://github.com/fferegrino/neo4j/releases/tag/3.5.0-final-release](https://github.com/fferegrino/neo4j/releases/tag/3.5.0-final-release).
2. In the root directory generate the binaries for Neo4j using the instructions given in the previous link.
3. From the folder `packaging/standalone/target` extract the binaries for Unix and place it in the *parent* folder
4. Rename the folder containing it to `installation-3.5.0-maps`
5. Replace the contents of the file `installation-3.5.0-maps/conf/neo4j.conf` for the ones given in [this file](https://github.com/fferegrino/n4j-test-setup/blob/master/conf-files/neo4j-maps.conf).

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

This program must be running in order to execute the following step.

### 6.  Execute the `run.sh` script

The script requires a single parameter: the number of times you want the different executions to run, for example to execute 5 rounds of insertions and retrievals, the following command should be used

```
sh run.sh 5
```

## Test results

The tests execution will generate a single file per run that consists of TSV file, where the columns are:
 - **run**: the number of run this info is about
 - **data**: whether that row refers to an insertion/retrieval of flight nodes or airports+airlines (denoted as other), depending on the value of this field the interpretation of times changes
 - **instance**: the instance that was used for insertion/retrieval, there are three posibilities: `3.4.0-plain`, `3.4.0-apoc` and `3.5.0-maps`
 - **records**: the number of records that were inserted, this number is only relevant when the row is about insertions of flights
 - **insertion**: the time (in seconds) that it took to insert the records in the specified instance. When the row refers to flights, this measures the insertion of flights, otherwise this refers to the insertion of airports.
 - **ins_retrieve**: when the row is about flights, this column holds the retrieval time of the flight nodes.  Otherwise this is the value in time of the insertion of airlines. Both are measured in seconds.
 - **retrieve**: when the row is not about flights, this contains the time of retrieval of airport nodes
 - **date**: date time formatted as MMDDhhmm
 
