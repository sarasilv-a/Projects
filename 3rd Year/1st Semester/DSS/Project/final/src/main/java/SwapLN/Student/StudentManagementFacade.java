package SwapLN.Student;

import SwapDL.StudentDAO;
import SwapLN.Shift.CurricularUnit;
import SwapLN.Student.Status.Associate;
import SwapLN.Student.Status.Athlete;
import SwapLN.Student.Status.SpecialNeeds;
import SwapLN.Student.Status.Worker;
import SwapLN.Student.Status.Status;

import org.json.JSONArray;
import org.json.JSONObject;

import java.sql.SQLException;
import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.List;
import java.util.Map.Entry;

public class StudentManagementFacade implements IStudentManagement {
    private final StudentDAO studentDAO;

    public StudentManagementFacade() {
        this.studentDAO = new StudentDAO();
    }

    public boolean authenticateStudent(String studentNumber, String password) throws Exception {
        return studentDAO.validateStudent(studentNumber, password);
    }

    @Override
    public void updatePassword(String studentNumber, String newPassword) throws Exception {
        studentDAO.setPassword(studentNumber, newPassword);
    }

    public List<Student> getAllStudents() throws Exception {
        return studentDAO.getAllStudents();
    }

    public void removeAllStudents() throws Exception {
        studentDAO.removeAllStudents();
    }

    @Override
    public void importStudents(JSONArray studentData) throws Exception {
        List<Entry<Student, List<String>>> studentEnrollments = new ArrayList<>();

        for (int i = 0; i < studentData.length(); i++) {
            JSONObject studentJSON = studentData.getJSONObject(i);

            String studentNumber = studentJSON.getString("Número");
            String name = studentJSON.getString("Nome");

            Status status = null;
            if (studentJSON.has("status")) {
                String statusType = studentJSON.getString("status").trim();
                status = switch (statusType) {
                    case "Athlete" -> new Athlete("Athlete");
                    case "Associate" -> new Associate("Associate");
                    case "Worker" -> new Worker("Worker");
                    case "SpecialNeeds" -> new SpecialNeeds("SpecialNeeds");
                    default -> throw new IllegalArgumentException("Invalid status type: " + statusType);
                };
            }

            List<String> curricularUnits = new ArrayList<>();
            if (studentJSON.has("curricularUnits")) {
                JSONArray unitsArray = studentJSON.getJSONArray("curricularUnits");
                for (int j = 0; j < unitsArray.length(); j++) {
                    curricularUnits.add(String.valueOf(unitsArray.getInt(j)));
                }
            }

            studentEnrollments.add(new AbstractMap.SimpleEntry<>(new Student(studentNumber, name, status), curricularUnits));
        }

        addStudent(studentEnrollments);

        System.out.println("Students imported successfully.");
    }

    @Override
    public boolean studentExists(String studentNumber) throws Exception {
        return studentDAO.studentExists(studentNumber);
    }

    @Override
    public List<Student> getStudentsWithIncompleteSchedules() throws Exception {
        return studentDAO.getStudentsWithIncompleteSchedules();
    }

    @Override
    public List<CurricularUnit> getEnrolledCurricularUnits(String studentNumber) throws Exception {
        return studentDAO.getEnrolledCurricularUnits(studentNumber);
    }

    private void addStudent(List<Entry<Student, List<String>>> studentEnrollments) throws Exception {
        try {
            studentDAO.insertStudents(studentEnrollments);
            System.out.println("Inserted " + studentEnrollments.size() + " students into the database.");
        } catch (Exception e) {
            throw new Exception("Error inserting students: " + e.getMessage(), e);
        }
    }
}