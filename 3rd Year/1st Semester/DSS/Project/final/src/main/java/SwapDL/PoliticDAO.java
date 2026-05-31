package SwapDL;

import SwapLN.Shift.Politic;

import java.sql.*;

public class PoliticDAO {
    public Politic getPolitic(int politicID) throws Exception {
        String query = "SELECT * FROM Politic WHERE politicID = ?";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setInt(1, politicID);
            ResultSet rs = stm.executeQuery();
            if(rs.next()){
                int politicId = rs.getInt("ID");
                String type = rs.getString("type");

                return new Politic(politicID, type);
            }
            return null;
        }
        catch (SQLException e) {
            throw new Exception("Error getting politic: " + e.getMessage());
        }
    }
}
