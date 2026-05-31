package SwapLN;

import SwapLN.CourseDirector.CourseDirectorManagementFacade;
import SwapLN.Shift.CurricularUnit;
import SwapLN.Shift.Politic;
import SwapLN.Shift.Room;
import SwapLN.Schedule.ScheduleManagementFacade;
import SwapLN.Shift.Shift;
import SwapLN.Shift.ShiftManagementFacade;
import SwapLN.Shift.Slot;
import SwapLN.Student.StudentManagementFacade;
import SwapLN.Student.Student;
import SwapUtils.JSONParser;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;


import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.sql.Time;
import java.time.LocalTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class MainFacade {
    private final CourseDirectorManagementFacade courseDirectorManagementFacade = new CourseDirectorManagementFacade();
    private final StudentManagementFacade studentManagementFacade = new StudentManagementFacade();
    private final ShiftManagementFacade shiftManagementFacade = new ShiftManagementFacade();
    private final ScheduleManagementFacade scheduleManagementFacade = new ScheduleManagementFacade();

    // AUTHENTICATION

    public boolean authenticateCourseDirector(String password) throws Exception {
        return courseDirectorManagementFacade.authenticateCourseDirector(password);
    }

    public void updatePassword(String newPassword) throws Exception {
        courseDirectorManagementFacade.updatePassword(newPassword);
    }

    public void updateStudentPassword(String studentNumber, String newPassword) throws Exception {
        studentManagementFacade.updatePassword(studentNumber, newPassword);
    }

    public boolean authenticateStudent(String studentNumber, String password) throws Exception {
        return studentManagementFacade.authenticateStudent(studentNumber, password);
    }


    // SHIFTS

    public Shift getShift(int shiftID) throws Exception {
        return shiftManagementFacade.getShift(shiftID);
    }

    public List<Shift> getScheduleShifts(List<Integer> shiftIDs) throws Exception {
        return shiftManagementFacade.getScheduleShifts(shiftIDs);
    }

    public List<Shift> getShiftsByUC(String curricularUnitCode) throws Exception {
        return shiftManagementFacade.getShiftsByUC(curricularUnitCode);
    }

    public void importShiftsFromJSON(String filePath) throws Exception {
        JSONArray shiftData = JSONParser.parseJSONFile(filePath);
        shiftManagementFacade.importShifts(shiftData);
    }

    public void removeAllShifts() throws Exception {
        shiftManagementFacade.removeAllShifts();
    }

    public void updateShiftLimit(int shiftID, int limit) throws Exception {
        shiftManagementFacade.updateShiftLimit(shiftID, limit);
    }


    // STUDENTS

    public List<Student> getAllStudents() throws Exception {
        return studentManagementFacade.getAllStudents();
    }

    public void removeAllStudents() throws Exception {
        studentManagementFacade.removeAllStudents();
    }

    public void importStudentsFromJSON(String filePath) throws Exception {
        JSONArray studentData = JSONParser.parseJSONFile(filePath);
        studentManagementFacade.importStudents(studentData);
    }

    public List<CurricularUnit> getEnrolledCurricularUnits(String studentNumber) throws Exception {
        return studentManagementFacade.getEnrolledCurricularUnits(studentNumber);
    }

    public boolean studentExists(String studentNumber) throws Exception {
        return studentManagementFacade.studentExists(studentNumber);
    }

    public List<Student> getStudentsWithIncompleteSchedules() throws Exception {
        return studentManagementFacade.getStudentsWithIncompleteSchedules();
    }


    // SLOT

    public Slot getSlot(int slotID) throws Exception {
        return shiftManagementFacade.getSlot(slotID);
    }


    // ROOM

    public Room getRoom(int roomID) throws Exception {
        return shiftManagementFacade.getRoom(roomID);
    }


    // POLITICS

    public void addPoliticsFromJSON(String filePath) throws Exception {
        JSONArray politicData = JSONParser.parseJSONFile(filePath);
        shiftManagementFacade.importPolitics(politicData);
    }

    public void removeAllPolitics() throws Exception {
        shiftManagementFacade.resetPoliticsToDefault();
    }


    // CURRICULAR UNITS

    public CurricularUnit getCurricularUnit(String curricularUnitCode) throws Exception {
        return shiftManagementFacade.getCurricularUnit(curricularUnitCode);
    }

    public List<CurricularUnit> getAllCurricularUnits() throws Exception {
        return shiftManagementFacade.getAllCurricularUnits();
    }

    public void removeAllCurricularUnits() throws Exception {
        shiftManagementFacade.removeAllCurricularUnits();
    }

    public void importCurricularUnitsFromJSON(String filePath) throws Exception {
        JSONArray curricularUnitsData = JSONParser.parseJSONFile(filePath);
        shiftManagementFacade.importCurricularUnits(curricularUnitsData);
    }


    // SCHEDULES

    public List<Integer> getShifts(String studentNumber) throws Exception {
        return scheduleManagementFacade.getShifts(studentNumber);
    }

    public List<String> getStudents(int shiftID) throws Exception {
        return scheduleManagementFacade.getStudents(shiftID);
    }

    public void allocateStudentToShift(String studentNumber, int shiftID) throws Exception {
        scheduleManagementFacade.allocateStudentToShift(studentNumber, shiftID);
    }

    public boolean addShiftStudent(String studentNumber, int shiftID) throws Exception {
        return scheduleManagementFacade.addShiftStudent(studentNumber, shiftID);
    }

    public void removeAllSchedules() throws Exception {
        scheduleManagementFacade.removeAllSchedules();
    }

    public void removeShiftStudent(String studentNumber, int shiftID) throws Exception {
        scheduleManagementFacade.removeShiftStudent(studentNumber, shiftID);
    }

    public void exportStudentScheduleToJSON(String studentNumber, String filePath) throws Exception {
        List<Integer> shiftIDs = scheduleManagementFacade.getShifts(studentNumber);
        if (shiftIDs == null || shiftIDs.isEmpty()) {
            throw new Exception("No schedule found for student " + studentNumber);
        }

        List<Shift> shifts = shiftManagementFacade.getScheduleShifts(shiftIDs);

        Map<Integer, Slot> slots = new HashMap<>();
        Map<Integer, Room> rooms = new HashMap<>();
        Map<String, CurricularUnit> curricularUnits = new HashMap<>();

        for (Shift shift : shifts) {
            int slotID = shift.getSlotID();
            if (!slots.containsKey(slotID)) {
                slots.put(slotID, shiftManagementFacade.getSlot(slotID));
            }

            int roomID = slots.get(slotID).getRoomID();
            if (!rooms.containsKey(roomID)) {
                rooms.put(roomID, shiftManagementFacade.getRoom(roomID));
            }

            String curricularUnitCode = shift.getCurricularUnitCode();
            if (!curricularUnits.containsKey(curricularUnitCode)) {
                curricularUnits.put(curricularUnitCode, shiftManagementFacade.getCurricularUnit(curricularUnitCode));
            }
        }

        scheduleManagementFacade.exportScheduleToJSON(studentNumber, filePath, shifts, slots, rooms, curricularUnits);
    }

    public boolean hasShifts() throws Exception {
        return shiftManagementFacade.hasShifts();
    }
}