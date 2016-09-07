# elasticdiff
Elasticsearch diff between indices

![project logo](https://raw.githubusercontent.com/szborows/elasticdiff/master/elasticdiff.png)

Tested with ES version 2.3.

Example usage:
`python3 elasticdiff.py -q -t documentType -i myKey http://1.2.3.4/index1 http://2.3.4.5/index1`

How does output look like?
--------------------------

Example assumes `test/create_sample.sh` was ran before.

```
only in left: a5
only in left: a1
only in right: a4
only in right: a2
entries for key a3 differ
--- 

+++ 

@@ -1,4 +1,4 @@

 {
   "key": "a3",
-  "value": "DEF"
+  "value": "XYZ"
 }
Summary:
2 entries only in left index
2 entries only in right index
1 common entries
  0 of them are the same
  1 of them differ
```
