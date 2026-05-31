package SwapLN.Shift;

public abstract class Shift {
    private final int shiftID;
    private final int number;
    private final int limit;
    private final int studentsEnrolled;
    private final int slotID;
    private final String curricularUnitCode;

    public Shift(int shiftID, int number, int limit, int slotID, String curricularUnitCode, int studentsEnrolled) {
        this.shiftID = shiftID;
        this.number = number;
        this.limit = limit;
        this.studentsEnrolled = studentsEnrolled;
        this.slotID = slotID;
        this.curricularUnitCode = curricularUnitCode;
    }

    public int getShiftID() {
        return shiftID;
    }

    public int getNumber() {
        return number;
    }

    public int getLimit() {
        return limit;
    }

    public int getStudentsEnrolled() {
        return studentsEnrolled;
    }

    public int getSlotID() {
        return slotID;
    }

    public String getCurricularUnitCode() {
        return curricularUnitCode;
    }

    public abstract String getType();
}
