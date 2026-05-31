package SwapLN.Student.Status;

public abstract class Status {
    private final String statusType;

    public Status(String statusType) {
        this.statusType = statusType;
    }

    public String getStatus() {
        return statusType != null ? statusType : "No status";
    }

    public abstract String getStatusType();
}
