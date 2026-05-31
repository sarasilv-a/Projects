package SwapDL;

import SwapLN.Shift.Room;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.Statement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class RoomDAO {
    public Room getRoom(int roomID) throws Exception {
        String query = "SELECT * FROM Room WHERE id = ?";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setInt(1, roomID);
            ResultSet rs = stm.executeQuery();
            if(rs.next()){
                int roomId = rs.getInt("id");
                int building = rs.getInt("building");
                int roomNumber = rs.getInt("number");
                int capacity = rs.getInt("capacity");

                return new Room(roomId, building, roomNumber, capacity);
            }
            return null;
        }
        catch (SQLException e) {
            throw new Exception("Error getting room: " + e.getMessage());
        }
    }

    public Room getOrInsertRoom(int building, int roomNumber, int limit) throws Exception {
        String query = "SELECT * FROM Room WHERE building = ? AND number = ?";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setInt(1, building);
            stm.setInt(2, roomNumber);
            ResultSet rs = stm.executeQuery();

            if (rs.next()) {
                return new Room(
                        rs.getInt("id"),
                        rs.getInt("building"),
                        rs.getInt("number"),
                        rs.getInt("capacity")
                );
            } else {
                return insertRoom(building, roomNumber, limit);
            }
        }
    }

    public Room insertRoom(int building, int roomNumber, int limit) throws Exception {
        String query = "INSERT INTO Room (building, number, capacity) VALUES (?, ?, ?)";

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query, Statement.RETURN_GENERATED_KEYS)) {
            stm.setInt(1, building);
            stm.setInt(2, roomNumber);
            stm.setInt(3, limit);
            stm.executeUpdate();

            try (ResultSet rs = stm.getGeneratedKeys()) {
                if (rs.next()) {
                    return new Room(rs.getInt(1), building, roomNumber, limit);
                }
            }
        }
        throw new Exception("Error inserting room.");
    }
}
