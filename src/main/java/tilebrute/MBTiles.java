package tilebrute;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Support for MBTiles file format, version 1.1.
 *
 * MBTiles (http://mbtiles.org) is a specification for storing tiled map data in
 * SQLite databases for immediate use and for transfer. The files are designed for
 * portability of thousands, hundreds of thousands, or even millions of standard
 * map tile images in a single file.
 *
 * A more-or-less direct port of the TileStache MBTiles implementation,
 * https://github.com/migurski/TileStache/blob/master/TileStache/MBTiles.py
 */
public class MBTiles {

  static {
    try {
      Class.forName("org.sqlite.JDBC");
    } catch (ClassNotFoundException e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * MBTiles spec allows for overlay or baselayer collection types.
   */
  public static enum Type {
    overlay, baselayer
  }

  /**
   * MBTiles spec supports tiles of the following formats.
   */
  public static enum Format {
    png("image/png"),
    jpg("image/jpeg"),
    json("text/json");

    public String mime;
    Format(String mime) { this.mime = mime; }
  }

  /**
   * Container class for holding (x,y,z) coordinates in an unspecified
   * coordinate system.
   */
  public static class Coordinate {
    public int z, x, y;
    public Coordinate(int z, int x, int y) { this.z = z; this.x = x; this.y = y; }
  }

  /**
   * Container class for holding a map tile.
   */
  public static class Tile {
    public Format format;
    public byte[] bytes;
    public Tile(Format format, byte[] bytes) { this.format = format; this.bytes = bytes; }
  }

  /**
   * Invert a Y coordinate between TMS tile and Google tile origins.
   */
  static int invertY(int y, int z) {
    return (int) (Math.pow(2.0, z) - 1 - y);
  }

  /**
   * Open an MBTiles files.
   */
  public static Connection open(String filename) throws SQLException {
    return DriverManager.getConnection(String.format("jdbc:sqlite:%s", filename));
  }

  /**
   * Close an open {@link Connection}.
   */
  public static void close(Connection conn) throws SQLException {
    if (null != conn) conn.close();
  }

  /**
   * Initialize a new MBTiles database.
   */
  public static void createTileset(Connection conn, final String name, final Type type,
      final String version, final String description, final Format format) throws SQLException {
    createTileset(conn, name, type, version, description, format, null);
  }

  /**
   * Initialize a new MBTiles database.
   */
  public static void createTileset(Connection conn, final String name, final Type type,
      final String version, final String description, final Format format, final String bounds)
      throws SQLException {

    conn.prepareStatement("CREATE TABLE metadata (name TEXT, value TEXT, PRIMARY KEY (name))").executeUpdate();
    conn.prepareStatement("CREATE TABLE tiles (zoom_level INTEGER, tile_column INTEGER, tile_row INTEGER, tile_data BLOB)").executeUpdate();
    conn.prepareStatement("CREATE UNIQUE INDEX coord ON tiles (zoom_level, tile_column, tile_row)").executeUpdate();

    @SuppressWarnings("serial")
    Map<String, String> data = new HashMap<String, String>() {{
      put("name", name);
      put("type", type.toString());
      put("version", version);
      put("description", description);
      put("format", format.toString());
      if (null != bounds) put("bounds", bounds);
    }};

    for (Map.Entry<String, String> e : data.entrySet()) {
      PreparedStatement stmt = conn.prepareStatement("INSERT INTO metadata VALUES (?, ?)");
      stmt.setString(1, e.getKey());
      stmt.setString(2, e.getValue());
      stmt.executeUpdate();
    }
  }

  /**
   * Return true if this database contains any tiles, false otherwise.
   */
  public static boolean tilesetExists(Connection conn) throws SQLException {
    PreparedStatement stmt = conn.prepareStatement("SELECT name, value FROM metadata LIMIT 1");
    if (!stmt.execute()) return false;
    stmt = conn.prepareStatement("SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles LIMIT 1");
    if (!stmt.execute()) return false;

    return true;
  }

  /**
   * Retrieve the database metadata.
   */
  public static Map<String, String> tilesetInfo(Connection conn) throws SQLException {
    PreparedStatement stmt;
    Map<String, String> ret = new HashMap<String, String>(6);

    for (String key : new String[] { "name", "type", "version", "description", "format", "bounds" }) {
      stmt = conn.prepareStatement("SELECT value FROM metadata WHERE name = ?");
      stmt.setString(1, key);
      ResultSet rs = stmt.executeQuery();
      if (!rs.first()) continue;
      ret.put(key, rs.getString("value"));
    }
    return ret;
  }

  /**
   * Retrieve a list of tiles in the database.
   */
  public static List<Coordinate> listTiles(Connection conn) throws SQLException {
    PreparedStatement stmt;
    List<Coordinate> ret = new ArrayList<Coordinate>();

    stmt = conn.prepareStatement("SELECT zoom_level, tile_column, tile_row FROM tiles");
    ResultSet rs = stmt.executeQuery();
    while (rs.next()) {
      int z = rs.getInt("zoom_level"),
          x = rs.getInt("tile_column"),
          y = rs.getInt("tile_row");
      ret.add(new Coordinate(z, x, y));
    }
    return ret;
  }

  /**
   * Retrieve a specific tile.
   */
  public static Tile getTile(Connection conn, Coordinate coord) throws SQLException {
    PreparedStatement stmt;
    Format fmt = null;

    stmt = conn.prepareStatement("SELECT value FROM metadata WHERE name='format'");
    ResultSet rs = stmt.executeQuery();
    if (rs.first()) fmt = Format.valueOf(rs.getString("value"));

    stmt = conn.prepareStatement("SELECT tile_data FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?");
    stmt.setInt(1, coord.z);
    stmt.setInt(2, coord.x);
    stmt.setInt(3, coord.y);
    rs = stmt.executeQuery();
    if (!rs.first()) return null;
    return new Tile(fmt, rs.getBytes("tile_data"));
  }

  /**
   * Delete a tile from the database.
   */
  public static void deleteTile(Connection conn, Coordinate coord) throws SQLException {
    PreparedStatement stmt;

    stmt = conn.prepareStatement("DELETE FROM tiles WHERE zoom_level=? AND tile_column=? AND tile_row=?");
    stmt.setInt(1, coord.z);
    stmt.setInt(2, coord.x);
    stmt.setInt(3, coord.y);
    stmt.executeUpdate();
  }

  /**
   * Add a tile to the database. Overwrites any existing tile at this
   * coordinate.
   */
  public static void putTile(Connection conn, Coordinate coord, Tile tile) throws SQLException {
    PreparedStatement stmt;
    stmt = conn.prepareStatement("REPLACE INTO tiles (zoom_level, tile_column, tile_row, tile_data) VALUES (?, ?, ?, ?)");
    stmt.setInt(1, coord.z);
    stmt.setInt(2, coord.x);
    stmt.setInt(3, coord.y);
    stmt.setBytes(4, tile.bytes);
    stmt.executeUpdate();
  }
}
