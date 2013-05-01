
### Deployment

 - evaluate MRJob (et al) vs shell scripts

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
