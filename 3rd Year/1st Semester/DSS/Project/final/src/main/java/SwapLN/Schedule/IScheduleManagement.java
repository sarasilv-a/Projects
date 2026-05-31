package SwapLN.Schedule;

import SwapLN.Shift.CurricularUnit;
import SwapLN.Shift.Room;
import SwapLN.Shift.Shift;
import SwapLN.Shift.Slot;

import java.util.List;
import java.util.Map;

public interface IScheduleManagement {

    List<Integer> getShifts(String studentNumber) throws Exception;

    List<String> getStudents(int shiftID) throws Exception;

    boolean addShiftStudent(String studentNumber, int shiftID) throws Exception;

    void removeShiftStudent(String studentNumber, int shiftID) throws Exception;

    void allocateStudentToShift(String studentNumber, int shiftID) throws Exception;

    void removeAllSchedules() throws Exception;

    void exportScheduleToJSON(String studentNumber, String filePath, List<Shift> shifts, Map<Integer, Slot> slots, Map<Integer, Room> rooms, Map<String, CurricularUnit> curricularUnits) throws Exception;
}
