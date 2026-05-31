package SwapLN.Shift;

public class Room {
    private final int roomID;
    private final int building;
    private final int roomNumber;
    private final int capacity;

    public Room(int roomID, int building, int roomNumber, int capacity) {
        this.roomID = roomID;
        this.building = building;
        this.roomNumber = roomNumber;
        this.capacity = capacity;
    }

    public int getRoomID() {
        return roomID;
    }

    public int getBuilding() {
        return building;
    }

    public int getRoomNumber() {
        return roomNumber;
    }

    public int getCapacity() {
        return capacity;
    }
}
