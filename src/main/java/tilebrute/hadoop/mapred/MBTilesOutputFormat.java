package tilebrute.hadoop.mapred;

import java.io.IOException;
import java.sql.Connection;
import java.sql.SQLException;

import org.apache.commons.codec.binary.Base64;
import org.apache.hadoop.fs.FileSystem;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapred.FileOutputFormat;
import org.apache.hadoop.mapred.JobConf;
import org.apache.hadoop.mapred.RecordWriter;
import org.apache.hadoop.mapred.Reporter;
import org.apache.hadoop.util.Progressable;

import tilebrute.MBTiles;
import tilebrute.MBTiles.Coordinate;
import tilebrute.MBTiles.Format;
import tilebrute.MBTiles.Tile;
import tilebrute.MBTiles.Type;

/**
 * Write tiles to an MBTiles database. Databases produced by multiple
 * producers must be merged externally to create a complete tileset.
 */
public class MBTilesOutputFormat extends FileOutputFormat<Text, Text> {

  public static class MBTilesRecordWriter implements RecordWriter<Text, Text> {
    Connection conn;

    public MBTilesRecordWriter(String connDetails) throws IOException {
      try {
        this.conn = MBTiles.open(connDetails);
        MBTiles.createTileset(conn, "", Type.baselayer, "", "", Format.png);
      } catch (SQLException e) {
        throw new IOException(e);
      }
    }

    public void write(Text tileId, Text tile) throws IOException {

      // figure out where this tile goes.
      String[] tileIdSplits = tileId.toString().split(",");
      assert tileIdSplits.length == 3;
      int tx = Integer.parseInt(tileIdSplits[0]);
      int ty = Integer.parseInt(tileIdSplits[1]);
      int zoom = Integer.parseInt(tileIdSplits[2]);

      // decode the tile data
      byte[] buf = Base64.decodeBase64(tile.toString());

      // write the data
      try {
        MBTiles.putTile(conn, new Coordinate(zoom, tx, ty), new Tile(Format.png, buf));
      } catch (SQLException e) {
        throw new IOException(e);
      }
    }

    public void close(Reporter arg0) throws IOException {
      try {
        MBTiles.close(conn);
      } catch (SQLException e) {
        throw new IOException(e);
      }
    }
  }

  public RecordWriter<Text, Text> getRecordWriter(FileSystem ignored, JobConf job, String name,
      final Progressable progress) throws IOException {

    Path outputDir = FileOutputFormat.getOutputPath(job);
    Path outputPath = new Path(outputDir, FileOutputFormat.getUniqueName(job, "mbtiles"));
    FileSystem fs = outputPath.getFileSystem(job);
    fs.mkdirs(outputDir);

    return new MBTilesRecordWriter(outputPath.toString().split(":")[1]);
  }
}
