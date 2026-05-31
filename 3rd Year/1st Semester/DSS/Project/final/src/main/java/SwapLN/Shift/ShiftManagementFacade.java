package SwapLN.Shift;

import SwapDL.*;
import org.json.JSONArray;
import org.json.JSONObject;

import java.sql.Time;
import java.util.ArrayList;
import java.util.List;

public class ShiftManagementFacade implements IShiftManagement {
    private final ShiftDAO shiftDAO;
    private final SlotDAO slotDAO;
    private final RoomDAO roomDAO;
    private final PoliticDAO politicDAO;
    private final CurricularUnitDAO curricularUnitDAO;

    public ShiftManagementFacade() {
        this.shiftDAO = new ShiftDAO();
        this.slotDAO = new SlotDAO();
        this.roomDAO = new RoomDAO();
        this.politicDAO = new PoliticDAO();
        this.curricularUnitDAO = new CurricularUnitDAO();
    }

    // SHIFTS

    @Override
    public Shift getShift(int shiftID) throws Exception {
        try {
            return shiftDAO.getShift(shiftID);
        } catch (Exception e) {
            throw new Exception("Error retrieving shift with ID " + shiftID + ": " + e.getMessage());
        }
    }

    @Override
    public List<Shift> getScheduleShifts(List<Integer> shiftIDs) throws Exception {
        try {
            return shiftDAO.getShifts(shiftIDs);
        } catch (Exception e) {
            throw new Exception("Error retrieving schedule shifts: " + e.getMessage());
        }
    }

    @Override
    public List<Shift> getShiftsByUC(String curricularUnitCode) throws Exception {
        try {
            return shiftDAO.getShiftsByUC(curricularUnitCode);
        } catch (Exception e) {
            throw new Exception("Error retrieving shifts for UC " + curricularUnitCode + ": " + e.getMessage());
        }
    }

    @Override
    public void addShift(String type, int number, int limit, int building, int roomNumber, int day, String startTime, String endTime, String curricularUnitCode) throws Exception {

        Room room = roomDAO.getOrInsertRoom(building, roomNumber, limit);


        int slotID = slotDAO.insertSlot(day, startTime, endTime, room.getRoomID());


        shiftDAO.insertShift(type, number, limit, slotID, curricularUnitCode);
    }

    @Override
    public void removeAllShifts() throws Exception {
        shiftDAO.removeAllShifts();
        slotDAO.removeAllSlots();
    }

    @Override
    public void updateShiftLimit(int shiftID, int newLimit) throws Exception {
        try {
            shiftDAO.updateShiftLimit(shiftID, newLimit);
        } catch (Exception e) {
            throw new Exception("Error updating shift limit for shift ID " + shiftID + ": " + e.getMessage());
        }
    }

    @Override
    public void importShifts(JSONArray shiftData) throws Exception {
        for (int i = 0; i < shiftData.length(); i++) {
            JSONObject shiftJSON = shiftData.getJSONObject(i);

            String shiftValue = shiftJSON.getString("shift");
            String type = shiftValue.replaceAll("\\d", "");
            int number = Integer.parseInt(shiftValue.replaceAll("\\D", ""));
            int building = Integer.parseInt(shiftJSON.getString("building").replace("CP", ""));
            int roomNumber = Integer.parseInt(shiftJSON.getString("room").replace(".", ""));
            int day = shiftJSON.getInt("day");
            String startTime = shiftJSON.getString("start");
            String endTime = shiftJSON.getString("end");
            int curricularUnitID = shiftJSON.getInt("id");
            int limit = shiftJSON.getInt("limit");

            addShift(type, number, limit, building, roomNumber, day, startTime + ":00", endTime + ":00", String.valueOf(curricularUnitID));
        }
        System.out.println("Shifts added successfully from JSON.");
    }


    // CURRICULAR UNITS

    @Override
    public CurricularUnit getCurricularUnit(String code) throws Exception {
        try {
            return curricularUnitDAO.getCurricularUnit(code);
        } catch (Exception e) {
            throw new Exception("Error retrieving curricular unit with code " + code + ": " + e.getMessage());
        }
    }

    @Override
    public List<CurricularUnit> getAllCurricularUnits() throws Exception {
        try {
            return curricularUnitDAO.getAllCurricularUnits();
        } catch (Exception e) {
            throw new Exception("Error retrieving all curricular units: " + e.getMessage());
        }
    }

    @Override
    public void removeAllCurricularUnits() throws Exception {
        try {
            curricularUnitDAO.removeAllCurricularUnits();
        } catch (Exception e) {
            throw new Exception("Error removing all curricular units: " + e.getMessage());
        }
    }

    @Override
    public void addCurricularUnit(CurricularUnit unit) throws Exception {
        try {
            curricularUnitDAO.insertCurricularUnit(unit);
        } catch (Exception e) {
            throw new Exception("Error adding curricular unit: " + e.getMessage());
        }
    }

    public void importCurricularUnits(JSONArray curricularUnitsData) throws Exception {
        for (int i = 0; i < curricularUnitsData.length(); i++) {
            JSONObject unitJSON = curricularUnitsData.getJSONObject(i);

            String code = String.valueOf(unitJSON.getInt("id"));
            String name = unitJSON.getString("name");
            String shortName = unitJSON.getString("short_name");
            int year = unitJSON.getInt("year");
            int semester = unitJSON.getInt("semester");
            boolean optional = unitJSON.getString("opcional").equalsIgnoreCase("yes");

            CurricularUnit unit = new CurricularUnit(code, name, shortName, year, semester, 1, optional);
            addCurricularUnit(unit);
        }
        System.out.println("Curricular units imported successfully.");
    }


    // SLOTS
    @Override
    public Slot getSlot(int slotID) throws Exception {
        try {
            return slotDAO.getSlot(slotID);
        } catch (Exception e) {
            throw new Exception("Error retrieving slot with ID " + slotID + ": " + e.getMessage());
        }
    }

    // ROOMS
    @Override
    public Room getRoom(int roomID) throws Exception {
        try {
            return roomDAO.getRoom(roomID);
        } catch (Exception e) {
            throw new Exception("Error retrieving room with ID " + roomID + ": " + e.getMessage());
        }
    }

    // POLITICS
    @Override
    public void addPoliticToCurricularUnit(int subjectId, int politicID) throws Exception {
        try {
            curricularUnitDAO.updatePolitic(subjectId, politicID);
        } catch (Exception e) {
            throw new Exception("Error adding politic to curricular unit: " + e.getMessage());
        }
    }

    @Override
    public void importPolitics(JSONArray politicData) throws Exception {
        for (int i = 0; i < politicData.length(); i++) {
            JSONObject politicJSON = politicData.getJSONObject(i);

            int subjectId = politicJSON.getInt("subjectId");
            String politicType = politicJSON.getString("politic");

            int politicID = switch (politicType.toLowerCase()) {
                case "limit" -> 2;
                case "group" -> 3;
                default -> throw new IllegalArgumentException("Invalid politic type: " + politicType);
            };

            addPoliticToCurricularUnit(subjectId, politicID);
        }
        System.out.println("Politics imported successfully.");
    }

    @Override
    public void resetPoliticsToDefault() throws Exception {
        try {
            curricularUnitDAO.resetAllPoliticsToDefault();
        } catch (Exception e) {
            throw new Exception("Error resetting all politics: " + e.getMessage());
        }
    }

    @Override
    public boolean hasShifts() throws Exception {
        return shiftDAO.hasShifts();
    }
}
