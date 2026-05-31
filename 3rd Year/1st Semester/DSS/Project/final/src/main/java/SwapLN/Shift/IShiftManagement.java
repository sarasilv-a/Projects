package SwapLN.Shift;

import org.json.JSONArray;

import java.sql.Time;
import java.util.List;

public interface IShiftManagement {

    // SHIFTS
    Shift getShift(int shiftID) throws Exception;

    List<Shift> getScheduleShifts(List<Integer> shiftIDs) throws Exception;

    List<Shift> getShiftsByUC(String curricularUnitCode) throws Exception;

    void addShift(String type, int number, int limit, int building, int roomNumber, int day, String startTime, String endTime, String curricularUnitCode) throws Exception;

    void removeAllShifts() throws Exception;

    void updateShiftLimit(int shiftID, int newLimit) throws Exception;

    void importShifts(JSONArray shiftData) throws Exception;

    // SLOTS
    Slot getSlot(int slotID) throws Exception;

    // ROOMS
    Room getRoom(int roomID) throws Exception;

    // POLITICS
    void addPoliticToCurricularUnit(int subjectId, int politicID) throws Exception;

    void resetPoliticsToDefault() throws Exception;

    // CURRICULAR UNIT
    CurricularUnit getCurricularUnit(String code) throws Exception;

    List<CurricularUnit> getAllCurricularUnits() throws Exception;

    void importPolitics(JSONArray politicData) throws Exception;

    void removeAllCurricularUnits() throws Exception;

    void addCurricularUnit(CurricularUnit unit) throws Exception;

    boolean hasShifts() throws Exception;
}
