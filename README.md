rep-man
=======

Online Reputation Management

Download twitter4j
=======

Download twitter4j-3.0.3.zip from http://twitter4j.org/en/index.html and unzip
the jar files twitter4j-{core,async,stream, media-support}3.0.3.jar into the root directory
of this git project. I am not sure that all the jar files are needed (probably just the core
that is needed as of now), however it does not hurt and will make improving the project easier
to have them all.

Twitter4j is the only java interface mentioned on twitter.com as seems stable enough. Plus it
provides a REALLY good abstraction level that is very welcome.


Compile & Run
=======

To compile use
> make

PLEASE NOTE: for this program to run it will need to use OAuth to the twitter servers. I have created
an application on twitter.com for us. I will try to invite you if its possible. For now you can
authenticate using the twitter4j.properties.kalle file by renaming it to twitter4j.properties. This 
will authenticate using my twitter account, however, the application is set to read-only so it should
be safe for you to use.

Server Side
======

To be able to run the server, one has to download additional python packages.
It works with a postgreSQL database that one should import before running the
server (look at the file dump.db)

Start by installing the Machine Learning package: sklearn
(http://scikit-learn.org/stable/install.html)
Then the drivers for the postgreSQL are included into the psycopg2 module
(http://initd.org/psycopg/download/)

Set Up the Database
======

Open the file machineLearning/setup-db.sql and copy and paste the SQL commands
into psgql
The data is located into lexicon.csv
The table structure used is into setup-dn.sql

How to run the server
======

The server service is implemented into the file server.py
To run it use
> python server.py

Tools
======

To train a classifier (SVM), one can use the script train.py
To run it use
> python machineLearning/train.py

Some arguments can be added to decide how many positive, negative, neutral
instances the model has to take into consideration

Train the model with 10 positive tweets
> train.py -p 10

Train the model with 20 negative tweets
> train.py -n 20

Train the model with 100 neutral tweets
> train.py -e 10

Save the classifier in the file
> train.py -f classifier.txt

To have a look at all the parameters available, please look at the train.py
script file.

To test the performance of a set of classifiers, use:
> python machineLearning/perf.py

To train the 6 basic classifiers use:
> machineLearning/trainer.sh

Notice
=======
Good results are obtained with RBF as kernel function and the following
command:

> train.py -p 400 -n 400 -e 200

Performance = 64.30 %


Troubleshooting
=======

Firstly change the info inside machineLearning/database.properties to the info
that corresponds to the local database.

If the program complains about not providing a password change in the file
/etc/postgresql/\<version_number\>/main/pg\_hba.conf to use the METHOD trust on
local users. (I had to change users from localhost to trust as well as local.

