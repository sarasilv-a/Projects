package SwapLN.Student.Status;

public class Associate extends Status {
    public Associate(String statusType) {
        super(statusType);
    }

    @Override
    public String getStatusType() {
        return "Associate";
    }
}
