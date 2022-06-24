
# File Download
RDF로 생성한 파일은 아래의 링크에서 받을 수 있습니다.  
https://joyhong.notion.site/OpenDict-Triple-4854049089eb4672be9144b5d438df71

# 단어에 대한 의미 검색 
```
PREFIX ont: <http://localhost/ontology/>
SELECT ?word ?ws (group_concat(?wordsense; SEPARATOR=",") as ?sense)
 (group_concat(?definition; SEPARATOR=",") as ?sense_definition)
WHERE {
?s a ont:Word.
?s rdfs:label ?word.
FILTER(?word = '도적')
?s ont:hasSense ?ws.
?ws rdfs:label ?wordsense.
?ws ont:definition ?definition.
} GROUP BY ?ws ?word
```

# 단어 의미에 대한 정의 및 관계 검색
```
PREFIX ont: <http://localhost/ontology/>
SELECT ?s ?p ?o
WHERE {
{select ?word
where {
?word a ont:WordSense.
?word rdfs:label "아파트".
} LIMIT 100 }
{?word ?p ?ob.
VALUES ?p {rdf:type dc:title ont:definition ont:pos ont:wordType ont:wordUnit ont:category rdfs:label ont:abbreviation ont:antonym ont:broader ont:dialect ont:honorific ont:idiom ont:intimate ont:narrower ont:oldsaying ont:originally ont:proverb ont:reference ont:similar}
BIND (if( regex(str(?ob), "http://localhost/resource/cat_"), replace(str(?ob), "http://localhost/resource/cat_", ""), ?ob) as ?o ) 
BIND (?word as ?s) }
UNION {
?word  ?pp ?oo.
VALUES ?pp {ont:abbreviation ont:antonym ont:broader ont:dialect ont:honorific ont:idiom ont:intimate ont:narrower ont:oldsaying ont:originally ont:proverb ont:reference ont:similar}
?oo ?p ?ob.
VALUES ?p {rdf:type dc:title ont:definition ont:pos ont:wordType ont:wordUnit ont:category rdfs:label  }
BIND (if( regex(str(?ob), "http://localhost/resource/cat_"), replace(str(?ob), "http://localhost/resource/cat_", ""), ?ob) as ?o ) 
BIND (?oo as ?s) }
} ORDER BY ?s
```
