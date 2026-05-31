package SwapDL;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class CourseDirectorDAO {
    public void setPassword(String password) throws Exception {
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement("UPDATE CourseDirector SET password = ?")) {
            stm.setString(1, password);
            stm.executeUpdate();
        }
        catch (SQLException e) {
            throw new Exception("Error defining password: " + e.getMessage());
        }
    }

    public String getPassword() throws Exception {
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement("SELECT password FROM CourseDirector")) {
            ResultSet rs = stm.executeQuery();
            rs.next();
            return rs.getString("password");
        }
        catch (SQLException e) {
            throw new Exception("Error getting password: " + e.getMessage());
        }
    }
}
