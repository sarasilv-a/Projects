package SwapUI.CourseDirector;

import SwapLN.MainFacade;
import SwapUI.Menu;
import SwapUI.InputMenu;

public class PoliticsMenu {
    private final MainFacade mainFacade;

    public PoliticsMenu(MainFacade mainFacade) {
        this.mainFacade = mainFacade;
    }

    public void display() {
        Menu politicsMenu = new Menu("Politics");
        politicsMenu.addOption("Add Politics", this::addPolitics);
        politicsMenu.addOption("Remove Politics", this::removePolitics);
        politicsMenu.display();
    }

    private void addPolitics() {
        try {
            InputMenu<String> filePathMenu = new InputMenu<>("Enter the file path for the politics JSON file", String.class);
            String filePath = filePathMenu.display();

            mainFacade.addPoliticsFromJSON(filePath);
            System.out.println("Politics added successfully.");
        } catch (Exception e) {
            System.out.println("Error adding politics: " + e.getMessage());
        }
    }

    private void removePolitics() {
        try {
            mainFacade.removeAllPolitics();
            System.out.println("All politics removed successfully.");
        } catch (Exception e) {
            System.out.println("Error removing politics: " + e.getMessage());
        }
    }
}
