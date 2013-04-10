package tilebrute.hadoop.mapred;

import java.io.IOException;

import org.apache.commons.codec.binary.Base64;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileOutputFormat;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.RecordWriter;
import org.apache.hadoop.mapred.Reporter;
import org.apache.hadoop.util.Progressable;

/**
 * Write tiles out to disk in as "output-path/{z}/{x}/{y}.png". Generates lots
 * of small files and will likely make NN unhappy, but great for KVFS
 * implementations.
 */
public class MapTileOutputFormat extends FileOutputFormat<Text, Text> {

  public RecordWriter<Text, Text> getRecordWriter(FileSystem ignored, JobConf job, String name,
      final Progressable progress) throws IOException {

    final Path outputPath = FileOutputFormat.getOutputPath(job);
    final FileSystem fs = outputPath.getFileSystem(job);

    return new RecordWriter<Text, Text>() {

      public void write(Text tileId, Text tile) throws IOException {

        // figure out where this tile goes.
        String[] tileIdSplits = tileId.toString().split(",");
        assert tileIdSplits.length == 3;
        String tx = tileIdSplits[0];
        String ty = tileIdSplits[1];
        String zoom = tileIdSplits[2];

        // create the destination path as necessary
        Path tilePath = new Path(outputPath, zoom + "/" + tx + "/" + ty + ".png");
        fs.mkdirs(tilePath.getParent());

        // decode the tile data
        byte[] buf = Base64.decodeBase64(tile.toString());

        // write the data
        final FSDataOutputStream fout = fs.create(tilePath, progress);
        fout.write(buf);
        fout.close();
      }

      public void close(Reporter arg0) throws IOException {}
    };
  }

}
