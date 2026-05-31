package SwapDL;

import SwapLN.Shift.Slot;

import java.sql.*;

public class SlotDAO {
    public Slot getSlot(int slotID) throws Exception {
        String query = "SELECT * FROM Slot WHERE id = ?";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setInt(1, slotID);
            ResultSet rs = stm.executeQuery();
            if(rs.next()){
                int slotId = rs.getInt("id");
                Time startTime = rs.getTime("startTime");
                Time endTime = rs.getTime("endTime");
                int roomID = rs.getInt("room");
                int weekDay = rs.getInt("weekDay");

                return new Slot(slotId, startTime, endTime, roomID, weekDay);
            }
            return null;
        }
        catch (SQLException e) {
            throw new Exception("Error getting slot: " + e.getMessage());
        }
    }

    public int insertSlot(int day, String startTime, String endTime, int roomID) throws Exception {
        String query = "INSERT INTO Slot (weekDay, startTime, endTime, room) VALUES (?, ?, ?, ?)";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query, Statement.RETURN_GENERATED_KEYS)) {
            stm.setInt(1, day);
            stm.setString(2, startTime);
            stm.setString(3, endTime);
            stm.setInt(4, roomID);
            stm.executeUpdate();

            try (ResultSet rs = stm.getGeneratedKeys()) {
                if (rs.next()) {
                    return rs.getInt(1);
                }
            }
        }
        throw new Exception("Error inserting slot.");
    }

    public void removeAllSlots() throws Exception {
        String query = "DELETE FROM Slot";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.executeUpdate();
        } catch (SQLException e) {
            throw new Exception("Error removing all slots: " + e.getMessage());
        }
    }

}
