package SwapLN.Student.Status;

public class SpecialNeeds extends Status{
    public SpecialNeeds(String statusType) {
        super(statusType);
    }

    @Override
    public String getStatusType() {
        return "SpecialNeeds";
    }
}
