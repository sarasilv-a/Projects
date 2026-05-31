package SwapDL;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class Database {
    public Database() {
        try {
            initializeDatabase();
        } catch (Exception e) {
            System.err.println("Error initializing database: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public void initializeDatabase() throws Exception {
        // Create and use the database
        try (Connection conn = Conn.getBaseConnection();
             PreparedStatement createDbStm = conn.prepareStatement("CREATE DATABASE IF NOT EXISTS swap;")) {
            createDbStm.executeUpdate();
        }
        try (Connection conn = Conn.getConnection();
             PreparedStatement useDbStm = conn.prepareStatement("USE swap;")) {
            useDbStm.executeUpdate();
        }

        // Create Room table
        try (Connection conn = Conn.getConnection();
             PreparedStatement createRoomTable = conn.prepareStatement(
                     "CREATE TABLE IF NOT EXISTS Room (" +
                             "id INT AUTO_INCREMENT PRIMARY KEY, " +
                             "building INT NOT NULL, " +
                             "number INT NOT NULL, " +
                             "capacity INT NOT NULL)")) {
            createRoomTable.executeUpdate();
        }

        // Create CourseDirector table
        try (Connection conn = Conn.getConnection();
             PreparedStatement createCourseDirectorTable = conn.prepareStatement(
                     "CREATE TABLE IF NOT EXISTS CourseDirector (" +
                             "id INT AUTO_INCREMENT PRIMARY KEY, " +
                             "password VARCHAR(45) NOT NULL)")) {
            createCourseDirectorTable.executeUpdate();
        }
        try (Connection conn = Conn.getConnection();
             PreparedStatement insertCourseDirector = conn.prepareStatement(
                     "INSERT IGNORE INTO CourseDirector (id, password) VALUES (1, 'admin')")) {
            insertCourseDirector.executeUpdate();
        }

        // Create Politic table
        try (Connection conn = Conn.getConnection();
             PreparedStatement createPoliticTable = conn.prepareStatement(
                     "CREATE TABLE IF NOT EXISTS Politic (" +
                             "id INT AUTO_INCREMENT PRIMARY KEY, " +
                             "type ENUM('Default', 'Limit', 'Groups') NOT NULL)")) {
            createPoliticTable.executeUpdate();
        }

        // Insert Default Politic
        try (Connection conn = Conn.getConnection();
             PreparedStatement insertDefaultPolitic = conn.prepareStatement(
                     "INSERT IGNORE INTO Politic (id, type) VALUES (1, 'Default')")) {
            insertDefaultPolitic.executeUpdate();
        }

        // Insert Limit Politic
        try (Connection conn = Conn.getConnection();
             PreparedStatement insertLimitPolitic = conn.prepareStatement(
                     "INSERT IGNORE INTO Politic (id, type) VALUES (2, 'Limit')")) {
            insertLimitPolitic.executeUpdate();
        }

        // Insert Groups Politic
        try (Connection conn = Conn.getConnection();
             PreparedStatement insertGroupsPolitic = conn.prepareStatement(
                     "INSERT IGNORE INTO Politic (id, type) VALUES (3, 'Groups')")) {
            insertGroupsPolitic.executeUpdate();
        }

        // Create Slot table
        try (Connection conn = Conn.getConnection();
             PreparedStatement createSlotTable = conn.prepareStatement(
                     "CREATE TABLE IF NOT EXISTS Slot (" +
                             "id INT AUTO_INCREMENT PRIMARY KEY, " +
                             "weekDay INT NOT NULL, " +
                             "startTime TIME NOT NULL, " +
                             "endTime TIME NOT NULL, " +
                             "room INT NOT NULL, " +
                             "FOREIGN KEY (room) REFERENCES Room(id))")) {
            createSlotTable.executeUpdate();
        }

        // Create CurricularUnit table
        try (Connection conn = Conn.getConnection();
             PreparedStatement createCurricularUnitTable = conn.prepareStatement(
                     "CREATE TABLE IF NOT EXISTS CurricularUnit (" +
                             "code CHAR(10) PRIMARY KEY, " +
                             "name VARCHAR(45) NOT NULL, " +
                             "shortname CHAR(10) NOT NULL, " +
                             "year INT NOT NULL, " +
                             "semester INT NOT NULL, " +
                             "type ENUM('Optional', 'Mandatory') NOT NULL, " +
                             "politic INT NOT NULL, " +
                             "FOREIGN KEY (politic) REFERENCES Politic(ID))")) {
            createCurricularUnitTable.executeUpdate();
        }

        // Create Shift table
        try (Connection conn = Conn.getConnection();
             PreparedStatement createShiftTable = conn.prepareStatement(
                     "CREATE TABLE IF NOT EXISTS Shift (" +
                             "id INT AUTO_INCREMENT PRIMARY KEY, " +
                             "number INT NOT NULL, " +
                             "type ENUM('PL', 'TP', 'T') NOT NULL, " +
                             "studentsEnrolled INT DEFAULT 0, " +
                             "slot INT NOT NULL, " +
                             "shiftLimit INT NOT NULL, " +
                             "curricularUnit CHAR(10) NOT NULL, " +
                             "FOREIGN KEY (slot) REFERENCES Slot(id), " +
                             "FOREIGN KEY (curricularUnit) REFERENCES CurricularUnit(code))")) {
            createShiftTable.executeUpdate();
        }

        // Create Student table
        try (Connection conn = Conn.getConnection();
             PreparedStatement createStudentTable = conn.prepareStatement(
                     "CREATE TABLE IF NOT EXISTS Student (" +
                             "number CHAR(10) PRIMARY KEY, " +
                             "name VARCHAR(60) NOT NULL, " +
                             "password VARCHAR(60) NOT NULL DEFAULT '123aluno', " +
                             "status ENUM('Athlete', 'Associate', 'Worker', 'SpecialNeeds') DEFAULT NULL)")) {
            createStudentTable.executeUpdate();
        }

        // Create Schedule table
        try (Connection conn = Conn.getConnection();
             PreparedStatement createScheduleTable = conn.prepareStatement(
                     "CREATE TABLE IF NOT EXISTS Schedule (" +
                             "student CHAR(10) NOT NULL, " +
                             "shift INT NOT NULL, " +
                             "PRIMARY KEY (student, shift), " +
                             "FOREIGN KEY (student) REFERENCES Student(number), " +
                             "FOREIGN KEY (shift) REFERENCES Shift(id))")) {
            createScheduleTable.executeUpdate();
        }

        // Create Enrollment table
        try (Connection conn = Conn.getConnection();
             PreparedStatement createEnrollmentTable = conn.prepareStatement(
                     "CREATE TABLE IF NOT EXISTS Enrollment (" +
                             "student CHAR(10) NOT NULL, " +
                             "curricularUnit CHAR(10) NOT NULL, " +
                             "PRIMARY KEY (student, curricularUnit), " +
                             "FOREIGN KEY (student) REFERENCES Student(number), " +
                             "FOREIGN KEY (curricularUnit) REFERENCES CurricularUnit(code))")) {
            createEnrollmentTable.executeUpdate();
        }

        // Create Trigger to update studentsEnrolled in Shift table
        try (Connection conn = Conn.getConnection();
             PreparedStatement createInsertTrigger = conn.prepareStatement(
                     "CREATE TRIGGER IF NOT EXISTS after_schedule_insert " +
                             "AFTER INSERT ON Schedule " +
                             "FOR EACH ROW " +
                             "BEGIN " +
                             "UPDATE Shift SET studentsEnrolled = studentsEnrolled + 1 WHERE id = NEW.shift; " +
                             "END;")) {
            createInsertTrigger.executeUpdate();
        }

        // Create Trigger to update studentsEnrolled in Shift table
        try (Connection conn = Conn.getConnection();
             PreparedStatement createDeleteTrigger = conn.prepareStatement(
                     "CREATE TRIGGER IF NOT EXISTS after_schedule_delete " +
                             "AFTER DELETE ON Schedule " +
                             "FOR EACH ROW " +
                             "BEGIN " +
                             "UPDATE Shift SET studentsEnrolled = studentsEnrolled - 1 WHERE id = OLD.shift; " +
                             "END;")) {
            createDeleteTrigger.executeUpdate();
        }
    }
}
