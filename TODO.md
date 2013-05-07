
### Deployment

 - [✓] evaluate MRJob (et al) vs shell scripts
 - [✓] add RunIf condition to restore_python.sh so master can be i686

### Output Formats

 - Store png in MBtiles
   - [mbtiles.org](https://github.com/mapbox/mbtiles-spec)
   - how to merge output from multiple reducers?
   - how to serve mbtiles data?
 - Store png in HBase
   - quadtree key instead of z/x/y ?
   - serve directly from REST gateway?

### Viewer Enhancements
 - add simple where-am-i information
 - add "jump to coordinates"
 - support switching tile layer source (local fs, s3, &c)

### Performance

 - typed bytes instead of base64
 - [✓] hdfs vs s3? writing directly to s3 on small dataset is equally
   performant as writing to HDFS. Re-evaluate with larger input.
 - [✓] more reducers!
 - lzo compress input
 - investigate large jumps in reducer progress
 - can a TOP help even our reducer load in small datasets?
