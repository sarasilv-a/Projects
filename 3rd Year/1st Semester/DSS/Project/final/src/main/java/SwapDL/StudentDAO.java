package SwapDL;

import SwapLN.Shift.CurricularUnit;
import SwapLN.Student.Status.*;
import SwapLN.Student.Student;

import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Map.Entry;
import java.util.List;
import java.util.Objects;

public class StudentDAO {
    public boolean validateStudent(String studentNumber, String password) throws Exception {
        String query = "SELECT password FROM Student WHERE number = ?";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setString(1, studentNumber);
            ResultSet rs = stm.executeQuery();

            if (rs.next()) {
                String storedPassword = rs.getString("password");
                return storedPassword.equals(password); // Valida a password
            } else {
                return false; // O estudante não foi encontrado
            }
        } catch (SQLException e) {
            throw new Exception("Error validating student: " + e.getMessage(), e);
        }
    }

    public void setPassword(String studentNumber, String password) throws Exception {
        String query = "UPDATE Student SET password = ? WHERE number = ?";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setString(1, password);
            stm.setString(2, studentNumber);
            int rowsAffected = stm.executeUpdate();

            if (rowsAffected == 0) {
                throw new Exception("No student found with number: " + studentNumber);
            }
            System.out.println("Password updated successfully for student: " + studentNumber);
        } catch (SQLException e) {
            throw new Exception("Error updating password: " + e.getMessage(), e);
        }
    }

    public List<Student> getAllStudents() throws Exception {
        String query = "SELECT number, name, status FROM Student";
        List<Student> students = new ArrayList<>();

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query);
             ResultSet rs = stm.executeQuery()) {

            while (rs.next()) {
                String number = rs.getString("number");
                String name = rs.getString("name");
                String statusType = rs.getString("status");

                Status status = null; // Define um valor padrão para o status
                if (statusType != null) { // Verifica se o status não é nulo
                    switch (statusType) {
                        case "Athlete":
                            status = new Athlete("Athlete");
                            break;
                        case "Associate":
                            status = new Associate("Associate");
                            break;
                        case "Worker":
                            status = new Worker("Worker");
                            break;
                        case "SpecialNeeds":
                            status = new SpecialNeeds("SpecialNeeds");
                            break;
                        default:
                            throw new IllegalArgumentException("Invalid status type: " + statusType);
                    }
                }

                students.add(new Student(number, name, status));
            }
        } catch (SQLException e) {
            throw new Exception("Error retrieving students: " + e.getMessage());
        }
        return students;
    }

    public void removeAllStudents() throws Exception {
        String deleteSchedule = "DELETE FROM Schedule";
        String deleteEnrollment = "DELETE FROM Enrollment";
        String deleteStudents = "DELETE FROM Student";

        try (Connection conn = Conn.getConnection()) {
            conn.setAutoCommit(false); // Inicia uma transação

            try (PreparedStatement stm1 = conn.prepareStatement(deleteSchedule);
                 PreparedStatement stm2 = conn.prepareStatement(deleteEnrollment);
                 PreparedStatement stm3 = conn.prepareStatement(deleteStudents)) {
                stm1.executeUpdate();
                stm2.executeUpdate();
                stm3.executeUpdate();

                conn.commit(); // Confirma a transação
            } catch (SQLException e) {
                conn.rollback(); // Reverte as alterações em caso de erro
                throw new Exception("Error removing all students: " + e.getMessage(), e);
            }
        } catch (SQLException e) {
            throw new Exception("Error establishing connection: " + e.getMessage(), e);
        }
    }

    public void insertStudents(List<Entry<Student, List<String>>> studentEnrollments) {
        String studentQuery = "INSERT INTO Student (number, name, status) VALUES (?, ?, ?)";
        String enrollmentQuery = "INSERT INTO Enrollment (student, curricularUnit) VALUES (?, ?)";

        try (Connection conn = Conn.getConnection();
             PreparedStatement studentStmt = conn.prepareStatement(studentQuery);
             PreparedStatement enrollmentStmt = conn.prepareStatement(enrollmentQuery)) {

            // Insert students into the Student table
            for (Entry<Student, List<String>> entry : studentEnrollments) {
                Student student = entry.getKey();
                studentStmt.setString(1, String.valueOf(student.getStudentNumber()));
                studentStmt.setString(2, student.getName());
                if (!Objects.equals(student.getStatus(), "No status")) {
                    studentStmt.setString(3, student.getStatus());
                } else {
                    studentStmt.setNull(3, java.sql.Types.VARCHAR);
                }
                studentStmt.addBatch();
            }

            studentStmt.executeBatch();
            System.out.println(studentEnrollments.size() + " students inserted successfully.");

            // Insert enrollments into the Enrollment table
            for (Entry<Student, List<String>> entry : studentEnrollments) {
                Student student = entry.getKey();
                List<String> curricularUnits = entry.getValue();

                if (curricularUnits != null) {
                    for (String unit : curricularUnits) {
                        enrollmentStmt.setString(1, String.valueOf(student.getStudentNumber()));
                        enrollmentStmt.setString(2, unit);
                        enrollmentStmt.addBatch();
                    }
                }
            }

            enrollmentStmt.executeBatch();
            System.out.println("Enrollment data inserted successfully.");
        } catch (SQLException e) {
            throw new RuntimeException("Error inserting students and enrollments: " + e.getMessage(), e);
        }
    }

    public List<CurricularUnit> getEnrolledCurricularUnits(String studentNumber) throws Exception {
        String query = """
        SELECT cu.code, cu.name, cu.shortname, cu.year, cu.semester, cu.type, cu.politic 
        FROM Enrollment e
        JOIN CurricularUnit cu ON e.curricularUnit = cu.code
        WHERE e.student = ?
    """;

        List<CurricularUnit> units = new ArrayList<>();

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setString(1, studentNumber);

            try (ResultSet rs = stm.executeQuery()) {
                while (rs.next()) {
                    String code = rs.getString("code");
                    String name = rs.getString("name");
                    String shortName = rs.getString("shortname");
                    int year = rs.getInt("year");
                    int semester = rs.getInt("semester");
                    String type = rs.getString("type");
                    int politicID = rs.getInt("politic");

                    boolean isOptional = type.equalsIgnoreCase("Optional");

                    CurricularUnit unit = new CurricularUnit(code, name, shortName, year, semester, politicID, isOptional);
                    units.add(unit);
                }
            }
        } catch (SQLException e) {
            throw new Exception("Error fetching enrolled curricular units: " + e.getMessage(), e);
        }

        return units;
    }

    public boolean studentExists(String studentNumber) throws Exception {
        String query = "SELECT 1 FROM Student WHERE number = ?";
        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query)) {
            stm.setString(1, studentNumber);
            ResultSet rs = stm.executeQuery();
            return rs.next();
        } catch (SQLException e) {
            throw new Exception("Error checking if student exists: " + e.getMessage());
        }
    }

    public List<Student> getStudentsWithIncompleteSchedules() throws Exception {
        String query = """
        SELECT DISTINCT s.number, s.name, s.status
        FROM Student s
        JOIN Enrollment e ON s.number = e.student
        LEFT JOIN Shift sh ON e.curricularUnit = sh.curricularUnit
        LEFT JOIN Schedule sc ON s.number = sc.student AND sc.shift = sh.id
        WHERE (
            SELECT COUNT(DISTINCT sh_inner.type)
            FROM Shift sh_inner
            JOIN Schedule sc_inner ON sc_inner.shift = sh_inner.id
            WHERE sc_inner.student = s.number
            AND sh_inner.curricularUnit = e.curricularUnit
        ) < 2
    """;

        List<Student> students = new ArrayList<>();

        try (Connection conn = Conn.getConnection();
             PreparedStatement stm = conn.prepareStatement(query);
             ResultSet rs = stm.executeQuery()) {

            while (rs.next()) {
                String number = rs.getString("number");
                String name = rs.getString("name");
                String statusType = rs.getString("status");

                Status status = null;
                if (statusType != null) {
                    switch (statusType) {
                        case "Athlete":
                            status = new Athlete("Athlete");
                            break;
                        case "Associate":
                            status = new Associate("Associate");
                            break;
                        case "Worker":
                            status = new Worker("Worker");
                            break;
                        case "SpecialNeeds":
                            status = new SpecialNeeds("SpecialNeeds");
                            break;
                        default:
                            throw new IllegalArgumentException("Invalid status type: " + statusType);
                    }
                }

                students.add(new Student(number, name, status));
            }
        } catch (SQLException e) {
            throw new Exception("Error fetching students with incomplete schedules: " + e.getMessage());
        }

        return students;
    }
}
