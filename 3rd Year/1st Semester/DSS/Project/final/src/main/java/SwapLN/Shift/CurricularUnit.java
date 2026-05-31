package SwapLN.Shift;

public class CurricularUnit {
    private final String code;
    private final String name;
    private final String shortName;
    private final int year;
    private final int semester;
    private final int politicID;
    private final boolean optional;

    public CurricularUnit(String code, String name, String shortName, int year, int semester, int politicID, boolean optional) {
        this.code = code;
        this.name = name;
        this.shortName = shortName;
        this.year = year;
        this.semester = semester;
        this.politicID = politicID;
        this.optional = optional;
    }

    public String getCode() {
        return code;
    }

    public String getName() {
        return name;
    }

    public String getShortName() {
        return shortName;
    }

    public int getYear() {
        return year;
    }

    public int getSemester() {
        return semester;
    }

    public int getPoliticID() {
        return politicID;
    }

    public boolean isOptional() {
        return optional;
    }

    @Override
    public String toString() {
        return "CurricularUnit {" +
                "code='" + code + '\'' +
                ", name='" + name + '\'' +
                ", shortName='" + shortName + '\'' +
                ", year=" + year +
                ", semester=" + semester +
                ", politicID=" + politicID +
                ", optional=" + optional +
                '}';
    }

}
