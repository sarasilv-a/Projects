package SwapDL;

import java.sql.*;

public class Conn {
    private static final String urlBase = "jdbc:mysql://localhost:3306/";
    private static final String databaseName = "swap";
    private static final String urlWithDatabase = urlBase + databaseName;
    private static final String usr = "root";
    private static final String pwd = "root";

    public static Connection getConnection() {
        try {
            return DriverManager.getConnection(urlWithDatabase, usr, pwd);
        } catch (SQLException e) {
            System.out.println("Connection failed! " + e.getMessage());
            return null;
        }
    }

    public static Connection getBaseConnection() {
        try {
            return DriverManager.getConnection(urlBase, usr, pwd);
        } catch (SQLException e) {
            System.out.println("Connection failed! " + e.getMessage());
            return null;
        }
    }
}

