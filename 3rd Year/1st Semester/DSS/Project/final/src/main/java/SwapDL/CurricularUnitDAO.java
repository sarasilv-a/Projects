package SwapDL;

import SwapLN.Shift.CurricularUnit;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class CurricularUnitDAO {
    public CurricularUnit getCurricularUnit(String curricularUnitCode) throws Exception {
        String query = "SELECT * FROM CurricularUnit WHERE code = ?";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setString(1, curricularUnitCode);
            ResultSet rs = stm.executeQuery();
            if(rs.next()){
                String curricularUnitDBCode = rs.getString("code");
                String name = rs.getString("name");
                String shortName = rs.getString("shortName");
                int year = rs.getInt("year");
                int semester = rs.getInt("semester");
                int politic = rs.getInt("politic");
                String optional = rs.getString("type");
                boolean opt = optional.equals("Optional");

                return new CurricularUnit(curricularUnitDBCode, name, shortName, year, semester, politic, opt);
            }
            return null;
        }
        catch (SQLException e) {
            throw new Exception("Error getting curricular unit: " + e.getMessage());
        }
    }

    public List<CurricularUnit> getAllCurricularUnits() throws Exception {
        String query = "SELECT * FROM CurricularUnit";
        List<CurricularUnit> units = new ArrayList<>();

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query);
             ResultSet rs = stm.executeQuery()) {

            while (rs.next()) {
                String code = rs.getString("code");
                String name = rs.getString("name");
                String shortName = rs.getString("shortName");
                int year = rs.getInt("year");
                int semester = rs.getInt("semester");
                int politic = rs.getInt("politic");
                String optional = rs.getString("type");
                boolean opt = optional.equals("Optional");

                units.add(new CurricularUnit(code, name, shortName, year, semester, politic, opt));
            }
        } catch (SQLException e) {
            throw new Exception("Error retrieving curricular units: " + e.getMessage());
        }

        return units;
    }

    public void removeAllCurricularUnits() throws Exception {
        String query = "DELETE FROM CurricularUnit";

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            int rowsAffected = stm.executeUpdate();
            if (rowsAffected == 0) {
                throw new Exception("No curricular units found to remove.");
            }
        } catch (SQLException e) {
            throw new Exception("Error removing all curricular units: " + e.getMessage());
        }
    }

    public void insertCurricularUnit(CurricularUnit unit) throws Exception {
        String query = "INSERT INTO CurricularUnit (code, name, shortName, year, semester, type, politic) VALUES (?, ?, ?, ?, ?, ?, ?)";

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {

            stm.setString(1, unit.getCode());
            stm.setString(2, unit.getName());
            stm.setString(3, unit.getShortName());
            stm.setInt(4, unit.getYear());
            stm.setInt(5, unit.getSemester());
            stm.setString(6, unit.isOptional() ? "Optional" : "Mandatory");
            stm.setInt(7, unit.getPoliticID());

            stm.executeUpdate();
        } catch (SQLException e) {
            throw new Exception("Error inserting curricular unit: " + e.getMessage());
        }
    }

    public void updatePolitic(int subjectId, int politicID) throws Exception {
        String query = "UPDATE CurricularUnit SET politic = ? WHERE code = ?";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setInt(1, politicID);
            stm.setInt(2, subjectId);
            stm.executeUpdate();
        } catch (SQLException e) {
            throw new Exception("Error updating politic: " + e.getMessage());
        }
    }

    public void resetAllPoliticsToDefault() throws Exception {
        String query = "UPDATE CurricularUnit SET politic = 1";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.executeUpdate();
        } catch (SQLException e) {
            throw new Exception("Error resetting all politics to default: " + e.getMessage());
        }
    }
}
