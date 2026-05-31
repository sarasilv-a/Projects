package SwapDL;

import SwapLN.Shift.Type.T;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class ScheduleDAO {
    public List<Integer> getShifts(String studentNumber) throws Exception {
        String query = "SELECT shift FROM Schedule WHERE student = ?";
        List<Integer> shiftIDs = new ArrayList<>();

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {

            stm.setString(1, studentNumber);
            try (ResultSet rs = stm.executeQuery()) {
                while (rs.next()) {
                    shiftIDs.add(rs.getInt("shift"));
                }
            }
        } catch (SQLException e) {
            throw new Exception("Error fetching shifts for student: " + e.getMessage());
        }
        return shiftIDs;
    }

    public List<String> getStudents(int shiftID) throws Exception {
        String query = "SELECT student FROM Schedule WHERE shift = ?";
        List<String> studentNumbers = new ArrayList<>();

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {

            stm.setInt(1, shiftID);
            try (ResultSet rs = stm.executeQuery()) {
                while (rs.next()) {
                    studentNumbers.add(rs.getString("student"));
                }
            }
        } catch (SQLException e) {
            throw new Exception("Error fetching students for shift: " + e.getMessage());
        }
        return studentNumbers;
    }

    public void allocateStudentToShift(String studentNumber, int shiftID) throws Exception {
        String query = "INSERT INTO Schedule (student, shift) VALUES (?, ?)";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setString(1, studentNumber);
            stm.setInt(2, shiftID);
            stm.executeUpdate();
        } catch (SQLException e) {
            throw new Exception("Error allocating student to shift: " + e.getMessage());
        }
    }

    public boolean addShiftStudent(String studentNumber, int shiftID) throws Exception {
        String checkQuery = "SELECT COUNT(*) FROM Schedule s " +
                "JOIN Shift sh ON s.shift = sh.id " +
                "WHERE s.student = ? AND sh.type = (SELECT type FROM Shift WHERE id = ?) " +
                "AND sh.curricularUnit = (SELECT curricularUnit FROM Shift WHERE id = ?)";

        String insertQuery = "INSERT INTO Schedule (student, shift) VALUES (?, ?)";

        try (Connection conn = Conn.getConnection();
             PreparedStatement checkStm = conn.prepareStatement(checkQuery);
             PreparedStatement insertStm = conn.prepareStatement(insertQuery)) {

            // Check if the student is already in a shift of the same type and unit
            checkStm.setString(1, studentNumber);
            checkStm.setInt(2, shiftID);
            checkStm.setInt(3, shiftID);

            try (ResultSet rs = checkStm.executeQuery()) {
                if (rs.next() && rs.getInt(1) > 0) {
                    return false; // Student already in a shift of the same type and curricular unit
                }
            }

            insertStm.setString(1, studentNumber);
            insertStm.setInt(2, shiftID);
            insertStm.executeUpdate();
        } catch (SQLException e) {
            throw new Exception("Error adding student to shift: " + e.getMessage(), e);
        }
        return true;
    }

    public void removeShiftStudent(String studentNumber, int shiftID) throws Exception {
        String query = "DELETE FROM Schedule WHERE student = ? AND shift = ?";

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {

            // Substituir os placeholders no SQL pela string `studentNumber` e o int `shiftID`
            stm.setString(1, studentNumber);
            stm.setInt(2, shiftID);
            stm.executeUpdate();

        } catch (SQLException e) {
            throw new Exception("Error removing student from shift: " + e.getMessage(), e);
        }
    }

    public void removeAllSchedules() throws Exception {
        String query = "DELETE FROM Schedule";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.executeUpdate();
        } catch (SQLException e) {
            throw new Exception("Error removing all schedules: " + e.getMessage());
        }
    }
}
