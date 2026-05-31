package SwapLN.Student;

import SwapLN.Shift.CurricularUnit;
import org.json.JSONArray;

import java.util.List;

public interface IStudentManagement {

    boolean authenticateStudent(String studentNumber, String password) throws Exception;

    void updatePassword(String studentNumber, String newPassword) throws Exception;

    List<Student> getAllStudents() throws Exception;

    void removeAllStudents() throws Exception;

    void importStudents(JSONArray studentData) throws Exception;

    boolean studentExists(String studentNumber) throws Exception;

    List<Student> getStudentsWithIncompleteSchedules() throws Exception;

    List<CurricularUnit> getEnrolledCurricularUnits(String studentNumber) throws Exception;
}