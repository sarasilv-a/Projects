package SwapLN.Schedule;

import SwapDL.ScheduleDAO;
import SwapLN.Shift.CurricularUnit;
import SwapLN.Shift.Room;
import SwapLN.Shift.Shift;
import SwapLN.Shift.Slot;
import SwapUtils.JSONWriter;
import org.json.JSONArray;
import org.json.JSONObject;

import java.util.List;
import java.util.Map;

public class ScheduleManagementFacade implements IScheduleManagement {

    private final ScheduleDAO scheduleDAO;

    public ScheduleManagementFacade() {
        this.scheduleDAO = new ScheduleDAO();
    }

    @Override
    public List<Integer> getShifts(String studentNumber) throws Exception {
        try {
            return scheduleDAO.getShifts(studentNumber);
        } catch (Exception e) {
            throw new Exception("Error retrieving shifts with student number " + studentNumber + ": " + e.getMessage());
        }
    }

    @Override
    public List<String> getStudents(int shiftID) throws Exception {
        try {
            return scheduleDAO.getStudents(shiftID);
        } catch (Exception e) {
            throw new Exception("Error retrieving students with shift ID " + shiftID + ": " + e.getMessage());
        }
    }

    @Override
    public boolean addShiftStudent(String studentNumber, int shiftID) throws Exception {
        return scheduleDAO.addShiftStudent(studentNumber, shiftID);
    }

    @Override
    public void removeShiftStudent(String studentNumber, int shiftID) throws Exception {
        scheduleDAO.removeShiftStudent(studentNumber, shiftID);
    }

    @Override
    public void allocateStudentToShift(String studentNumber, int shiftID) throws Exception {
        scheduleDAO.allocateStudentToShift(studentNumber, shiftID);
    }

    @Override
    public void removeAllSchedules() throws Exception {
        scheduleDAO.removeAllSchedules();
    }

    @Override
    public void exportScheduleToJSON(String studentNumber, String filePath, List<Shift> shifts, Map<Integer, Slot> slots, Map<Integer, Room> rooms, Map<String, CurricularUnit> curricularUnits) throws Exception {
        // Criar o JSON
        JSONObject studentSchedule = new JSONObject();
        studentSchedule.put("studentNumber", studentNumber);

        JSONArray shiftsArray = new JSONArray();
        for (Shift shift : shifts) {
            JSONObject shiftObject = createShiftJSONObject(shift, slots, rooms, curricularUnits);
            shiftsArray.put(shiftObject);
        }

        studentSchedule.put("shifts", shiftsArray);

        // Escrever o JSON para o ficheiro
        JSONWriter.writeJSONToFile(studentSchedule, filePath);
        System.out.println("Schedule exported successfully to: " + filePath);
    }

    private JSONObject createShiftJSONObject(
            Shift shift,
            Map<Integer, Slot> slots,
            Map<Integer, Room> rooms,
            Map<String, CurricularUnit> curricularUnits
    ) {
        Slot slot = slots.get(shift.getSlotID());
        Room room = rooms.get(slot.getRoomID());
        CurricularUnit curricularUnit = curricularUnits.get(shift.getCurricularUnitCode());

        JSONObject shiftObject = new JSONObject();
        shiftObject.put("shiftID", shift.getShiftID());
        shiftObject.put("curricularUnit", curricularUnit.getName());
        shiftObject.put("shortName", curricularUnit.getShortName());
        shiftObject.put("day", slot.getWeekDay());
        shiftObject.put("startTime", slot.getStartTime().toString());
        shiftObject.put("endTime", slot.getEndTime().toString());
        shiftObject.put("room", room.getBuilding() + " - Room " + room.getRoomNumber());
        shiftObject.put("capacity", room.getCapacity());

        return shiftObject;
    }


}
