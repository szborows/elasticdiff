#!/bin/bash

curl -XDELETE localhost:9200/test

curl -XPOST localhost:9200/test -d '{
    "settings" : {
        "number_of_shards" : 1
    },
    "mappings" : {
        "type1" : {
            "properties" : {
                "key" : { "type" : "string", "index" : "not_analyzed" },
                "value" : { "type" : "string", "index" : "analyzed" }
            }
        }
    }
}'

curl -XPOST localhost:9200/test/type1/ -d '{"key" : "a1", "value": "ABC"}'
curl -XPOST localhost:9200/test/type1/ -d '{"key" : "a3", "value": "DEF"}'
curl -XPOST localhost:9200/test/type1/ -d '{"key" : "a5", "value": "GHI"}'


curl -XDELETE localhost:9200/test1

curl -XPOST localhost:9200/test1 -d '{
    "settings" : {
        "number_of_shards" : 1
    },
    "mappings" : {
        "type1" : {
            "properties" : {
                "key" : { "type" : "string", "index" : "not_analyzed" },
                "value" : { "type" : "string", "index" : "analyzed" }
            }
        }
    }
}'

curl -XPOST localhost:9200/test1/type1/ -d '{"key" : "a2", "value": "ABC"}'
curl -XPOST localhost:9200/test1/type1/ -d '{"key" : "a3", "value": "XYZ"}'
curl -XPOST localhost:9200/test1/type1/ -d '{"key" : "a4", "value": "GHI"}'
