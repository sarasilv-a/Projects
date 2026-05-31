package SwapLN.Shift;

import java.sql.Time;

public class Slot {
    private final int slotID;
    private final Time startTime;
    private final Time endTime;
    private final int roomID;
    private final int weekDay;

    public Slot(int slotID, Time startTime, Time endTime, int roomID, int weekDay) {
        this.slotID = slotID;
        this.startTime = startTime;
        this.endTime = endTime;
        this.roomID = roomID;
        this.weekDay = weekDay;
    }

    public int getSlotID() {
        return slotID;
    }

    public Time getStartTime() {
        return startTime;
    }

    public Time getEndTime() {
        return endTime;
    }

    public int getRoomID() {
        return roomID;
    }

    public int getWeekDay() {
        return weekDay;
    }

    public boolean conflictsWith(Slot other) {
        return this.weekDay == other.weekDay &&
                this.startTime.before(other.endTime) &&
                this.endTime.after(other.startTime);
    }

}
