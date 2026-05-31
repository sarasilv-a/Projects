package SwapLN.Shift.Type;

import SwapLN.Shift.Shift;

public class TP extends Shift {

    public TP(int shiftID, int number, int limit, int slotID, String curricularUnitCode, int studentsEnrolled) {
        super(shiftID, number, limit, slotID, curricularUnitCode, studentsEnrolled);
    }

    @Override
    public String getType() {
        return "TP";
    }
}

