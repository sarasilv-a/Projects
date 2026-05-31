package SwapLN.Shift;

public class Politic {
    private final int politicID;
    private final String politicType;

    public Politic(int politicID, String politicType) {
        this.politicID = politicID;
        this.politicType = politicType;
    }

    public int getPoliticID() {
        return politicID;
    }

    public String getPoliticType() {
        return politicType;
    }
}
