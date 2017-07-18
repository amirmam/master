
# run using ./bin/spark-submit --packages com.hortonworks:shc-core:1.1.1-2.1-s_2.11 --repositories http://repo.hortonworks.com/content/groups/public/ ../my_src_files/sparki.py some_words


# todo: 
# understand and change to use pandas 
# pass to sql
# catalog type doesn't matter?
# connectors vs simple mapreduce api. scala & java difference

from __future__ import print_function

import sys
import os

os.listdir("amir_package-1.0-py2.7.egg")

sys.path.append("amir_package-1.0-py2.7.egg/some_module/")

import some_module

# to get arv
import sys
# reduce by key. alternative is to pass lambda expression
from operator import add 
from pyspark.sql import SparkSession

if __name__ == "__main__":

    some_module.test()

    # create session
    spark = SparkSession\
        .builder\
        .appName("PythonWordCount")\
        .getOrCreate()

    # count words using RDD api
    lines = spark.read.text("hdfs://localhost:9000/" + sys.argv[1]).rdd.map(lambda r: r[0])

    counts = lines.flatMap(lambda x: x.split(' ')) \
                  .map(lambda x: (x, 1)) \
                  .reduceByKey(add)
    
    # write to hbase: convert the pipelinedRDD to dataframe, so we can use dataFrameWriter from pyspark api, also for better performance. 
    df = counts.toDF()

    # we will use the hortonworks spark hbase connector(shc) since for some reason the spark-hbase connector could not be recognized by the writer
    # shc: https://github.com/hortonworks-spark/shc
    # pyspark : http://spark.apache.org/docs/2.1.0/api/python/#pyspark.sql.html#pyspark.sql.DataFrame

# define catalog: https://hbase.apache.org/book.html#_sparksql_dataframes
    # _1, _2 are the auto generated column names. the "string" type seem to work fine(?), also the actual type is 'bigint'
    

    catalog = ''.join("""{
    "table":{"namespace":"default", "name":"testtable"},
    "rowkey":"key",
    "columns":{
        "_1":{"cf":"rowkey", "col":"key", "type":"string"},
        "_2":{"cf":"cf", "col":"col1", "type":"bigint"}
    }
 }""".split())

    # if newTable is set, the table will be autogenerated in hbase. otherwise, we need to pre-create it in hbase. 5 is the number of 
    df.write.options(catalog=catalog, newTable="5").format("org.apache.spark.sql.execution.datasources.hbase").save()

    # any word that contains 't' to mysql
    df_t = df.filter(df._1.like('%t%')).collect()

    spark.stop()

