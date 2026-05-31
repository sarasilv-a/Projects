import SwapDL.Database;
import SwapUI.UserInterface;

import java.sql.*;

public class Main {
    public static void main(String[] args) {
        if (args.length < 1 || !(args[0].equals("director") || args[0].equals("student"))) {
            System.out.println("Use: gradle run --args=\"director|student\"");
            return;
        }

        new Database();
        System.out.println("Database initialized successfully!");

        String role = args[0];

        switch (role) {
            case "director":
                System.out.println("Starting Director system...");
                break;

            case "student":
                System.out.println("Starting Student system...");
                break;
        }

        new UserInterface(args[0].equals("director")).run();

//        String url = "jdbc:mysql://localhost:3306/swap";
//        String usr = "root";
//        String pwd = "root";
//
//        try (Connection conn = DriverManager.getConnection(url, usr, pwd)) {
//            System.out.println("Connected successfully!");
//        } catch (SQLException e) {
//            System.out.println("Failed to connect: " + e.getMessage());
//        }
    }
}
