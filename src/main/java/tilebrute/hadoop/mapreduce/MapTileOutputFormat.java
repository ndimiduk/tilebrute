package tilebrute.hadoop.mapreduce;

import java.io.IOException;

import org.apache.commons.codec.binary.Base64;
import org.apache.hadoop.fs.FSDataOutputStream;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.RecordWriter;
import org.apache.hadoop.mapreduce.TaskAttemptContext;
import org.apache.hadoop.mapreduce.lib.output.FileOutputCommitter;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;

/**
 * Don't use me, I don't work with Streaming so I haven't been tested at all!
 */
@Deprecated
public class MapTileOutputFormat extends FileOutputFormat<Text, Text> {

  @Override
  public RecordWriter<Text, Text> getRecordWriter(final TaskAttemptContext context)
      throws IOException, InterruptedException {

    final Path outputPath = FileOutputFormat.getOutputPath(context);
    final Path outputDir = new FileOutputCommitter(outputPath, context).getWorkPath();
    final FileSystem fs = outputDir.getFileSystem(context.getConfiguration());

    return new RecordWriter<Text, Text>() {

      public void write(Text tileId, Text tile) throws IOException {

        // figure out where this tile goes.
        String[] tileIdSplits = tileId.toString().split(",");
        assert tileIdSplits.length == 3;
        String tx = tileIdSplits[0];
        String ty = tileIdSplits[1];
        String zoom = tileIdSplits[2];

        // create the destination path as necessary
        Path tilePath = new Path(outputDir, zoom + "/" + tx + "/" + ty + ".png");
        fs.mkdirs(tilePath.getParent());

        // decode the tile data
        byte[] buf = Base64.decodeBase64(tile.toString());

        // write the data
        final FSDataOutputStream fout = fs.create(tilePath, context);
        fout.write(buf);
        fout.close();
      }

      public void close(TaskAttemptContext context) throws IOException,
          InterruptedException {
      }
    };
  }
}
