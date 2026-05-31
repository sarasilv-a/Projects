package SwapUI.CourseDirector;

import SwapLN.MainFacade;
import SwapLN.Shift.CurricularUnit;
import SwapLN.Shift.Shift;
import SwapLN.Student.Student;
import SwapUI.Menu;
import SwapUI.InputMenu;

import java.util.Comparator;
import java.util.List;

public class CurricularUnitMenu {
    private final MainFacade mainFacade;

    public CurricularUnitMenu(MainFacade mainFacade) {
        this.mainFacade = mainFacade;
    }

    public void display() {
        Menu curricularUnitsMenu = new Menu("Curricular Units");
        curricularUnitsMenu.addOption("View Curricular Units", this::viewCurricularUnits);
        curricularUnitsMenu.addOption("Add Curricular Units", this::addCurricularUnits);
        curricularUnitsMenu.addOption("Remove All Curricular Units", this::removeAllCurricularUnits);
        curricularUnitsMenu.display();
    }

    private void viewCurricularUnits() {
        try {
            // Obter e ordenar as unidades curriculares
            List<CurricularUnit> units = mainFacade.getAllCurricularUnits();
            units.sort(Comparator.comparing(CurricularUnit::getCode)); // Ordenar por código da UC

            if (units.isEmpty()) {
                System.out.println("No curricular units found in the system.");
                return;
            }

            // Apresentar as Unidades Curriculares
            for (CurricularUnit unit : units) {
                System.out.println("Curricular Unit:");
                System.out.println("  Code: " + unit.getCode() +
                        " | Name: " + unit.getName() +
                        " (" + unit.getShortName() + ")" +
                        " | Year: " + unit.getYear() +
                        " | Semester: " + unit.getSemester());

                // Obter e ordenar os turnos associados à UC
                List<Shift> shifts = mainFacade.getShiftsByUC(unit.getCode());
                shifts.sort(Comparator.comparing(Shift::getNumber)); // Ordenar por número de turno

                if (shifts.isEmpty()) {
                    System.out.println("  No shifts available for this curricular unit.");
                } else {
                    System.out.println("  Shifts:");
                    for (Shift shift : shifts) {
                        System.out.println("    | Type: " + shift.getType() +
                                " | Number: " + shift.getNumber() +
                                " | Students: " + shift.getStudentsEnrolled());
                    }
                }
                System.out.println();
            }
        } catch (Exception e) {
            System.out.println("Error retrieving curricular units: " + e.getMessage());
        }
    }

    private void addCurricularUnits() {
        try {
            InputMenu<String> filePathMenu = new InputMenu<>("Enter the file path for the curricular units JSON file", String.class);
            String filePath = filePathMenu.display();

            mainFacade.importCurricularUnitsFromJSON(filePath);
            System.out.println("All curricular units added successfully.");
        } catch (Exception e) {
            System.out.println("Error adding curricular units: " + e.getMessage());
        }
    }

    private void removeAllCurricularUnits() {
        try {

            List<Student> st = mainFacade.getAllStudents();

            if (!st.isEmpty()){
                System.out.println("Students still in the system. Please remove all students before removing curricular units.");
                return;
            }

            mainFacade.removeAllCurricularUnits();
            System.out.println("All curricular units removed successfully.");
        } catch (Exception e) {
            System.out.println("Error removing curricular units: " + e.getMessage());
        }
    }
}