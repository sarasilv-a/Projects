package SwapDL;

import SwapLN.Shift.*;
import SwapLN.Shift.Type.PL;
import SwapLN.Shift.Type.T;
import SwapLN.Shift.Type.TP;

import java.sql.*;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class ShiftDAO {

    public Shift getShift(int shiftID) throws Exception {
        String query = "SELECT * FROM Shift WHERE id = ?";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setInt(1, shiftID);
            try (ResultSet rs = stm.executeQuery()) {
                if (rs.next()) {
                    return mapShift(rs);
                }
            }
        } catch (SQLException e) {
            throw new Exception("Error fetching shift with ID " + shiftID + ": " + e.getMessage());
        }
        return null;
    }

    public List<Shift> getShifts(List<Integer> shiftIDs) throws Exception {
        if (shiftIDs == null || shiftIDs.isEmpty()) {
            return new ArrayList<>();
        }

        StringBuilder query = new StringBuilder("SELECT * FROM Shift WHERE id IN (");
        for (int i = 0; i < shiftIDs.size(); i++) {
            query.append("?").append(i < shiftIDs.size() - 1 ? "," : "");
        }
        query.append(")");

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query.toString())) {
            for (int i = 0; i < shiftIDs.size(); i++) {
                stm.setInt(i + 1, shiftIDs.get(i));
            }

            List<Shift> shifts = new ArrayList<>();
            try (ResultSet rs = stm.executeQuery()) {
                while (rs.next()) {
                    shifts.add(mapShift(rs));
                }
            }
            return shifts;
        } catch (SQLException e) {
            throw new Exception("Error fetching multiple shifts: " + e.getMessage());
        }
    }

    public List<Shift> getShiftsByUC(String curricularUnitCode) throws Exception {
        String query = "SELECT * FROM Shift WHERE curricularUnit = ?";
        List<Shift> shifts = new ArrayList<>();

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setString(1, curricularUnitCode);
            try (ResultSet rs = stm.executeQuery()) {
                while (rs.next()) {
                    shifts.add(mapShift(rs));
                }
            }
        } catch (SQLException e) {
            throw new Exception("Error fetching shifts for UC: " + e.getMessage());
        }
        return shifts;
    }

    private Shift mapShift(ResultSet rs) throws SQLException {
        int shiftID = rs.getInt("id");
        int number = rs.getInt("number");
        int limit = rs.getInt("shiftLimit");
        int studentsEnrolled = rs.getInt("studentsEnrolled");
        int slotID = rs.getInt("slot");
        String curricularUnitCode = rs.getString("curricularUnit");
        String type = rs.getString("type");

        switch (type) {
            case "PL":
                return new PL(shiftID, number, limit, slotID, curricularUnitCode, studentsEnrolled);
            case "TP":
                return new TP(shiftID, number, limit, slotID, curricularUnitCode, studentsEnrolled);
            case "T":
                return new T(shiftID, number, limit, slotID, curricularUnitCode, studentsEnrolled);
            default:
                throw new SQLException("Unknown shift type: " + type);
        }
    }

    public void insertShift(String type, int number, int limit, int slotID, String curricularUnitCode) throws Exception {
        String query = "INSERT INTO Shift (number, type, slot, shiftLimit, curricularUnit) VALUES (?, ?, ?, ?, ?)";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setInt(1, number);
            stm.setString(2, type);
            stm.setInt(3, slotID);
            stm.setInt(4, limit);
            stm.setString(5, curricularUnitCode);
            stm.executeUpdate();
        }
    }

    public void removeAllShifts() throws Exception {
        String query = "DELETE FROM Shift";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.executeUpdate();
        } catch (SQLException e) {
            throw new Exception("Error removing all shifts: " + e.getMessage());
        }
    }

    public void updateShiftLimit(int shiftID, int newLimit) throws Exception {
        String query = "UPDATE Shift SET shiftLimit = ? WHERE id = ?";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setInt(1, newLimit);
            stm.setInt(2, shiftID);
            int rowsAffected = stm.executeUpdate();
            if (rowsAffected == 0) {
                throw new Exception("No shift found with ID " + shiftID);
            }
        } catch (SQLException e) {
            throw new Exception("Error updating shift limit: " + e.getMessage());
        }
    }

    public boolean hasShifts() throws Exception {
        String query = "SELECT COUNT(*) AS shiftCount FROM Shift";

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query);
             ResultSet rs = stm.executeQuery()) {

            if (rs.next()) {
                return rs.getInt("shiftCount") > 0;
            }
        } catch (SQLException e) {
            throw new Exception("Error checking shifts existence: " + e.getMessage());
        }

        return false;
    }
}
