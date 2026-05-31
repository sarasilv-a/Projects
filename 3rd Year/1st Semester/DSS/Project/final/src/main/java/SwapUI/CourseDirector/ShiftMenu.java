package SwapUI.CourseDirector;

import SwapLN.MainFacade;
import SwapUI.Menu;
import SwapUI.InputMenu;

public class ShiftMenu {
    private final MainFacade mainFacade;

    public ShiftMenu(MainFacade mainFacade) {
        this.mainFacade = mainFacade;
    }

    public void display() {
        Menu shiftsMenu = new Menu("Shifts");
        shiftsMenu.addOption("Add Shifts", this::addShifts);
        shiftsMenu.addOption("Remove Shifts", this::removeShifts);
        shiftsMenu.display();
    }

    private void addShifts() {
        try {
            InputMenu<String> filePathMenu = new InputMenu<>("Enter the file path for the shifts JSON file", String.class);
            String filePath = filePathMenu.display();

            if (mainFacade.getAllCurricularUnits().isEmpty()) {
                System.out.println("No curricular units exist. Please add curricular units before adding shifts.");
                return;
            }

            mainFacade.importShiftsFromJSON(filePath);
            System.out.println("Shifts added successfully.");
        } catch (Exception e) {
            System.out.println("Error adding shifts: " + e.getMessage());
        }
    }

    private void removeShifts() {
        try {
            mainFacade.removeAllShifts();
            System.out.println("All shifts removed successfully.");
        } catch (Exception e) {
            System.out.println("Error removing shifts: " + e.getMessage());
        }
    }
}