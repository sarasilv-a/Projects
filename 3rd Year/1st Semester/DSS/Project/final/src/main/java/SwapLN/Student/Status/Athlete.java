package SwapLN.Student.Status;

public class Athlete extends Status {
    public Athlete(String statusType) {
        super(statusType);
    }

    @Override
    public String getStatusType() {
        return "Athlete";
    }
}
