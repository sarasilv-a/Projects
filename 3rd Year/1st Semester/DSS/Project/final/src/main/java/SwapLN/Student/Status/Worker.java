package SwapLN.Student.Status;

public class Worker extends Status{
    public Worker(String statusType) {
        super(statusType);
    }

    @Override
    public String getStatusType() {
        return "Worker";
    }
}
