package SwapUI.CourseDirector;

import SwapLN.MainFacade;
import SwapUI.InputMenu;
import SwapUI.Menu;

public class CourseDirectorMenu implements Runnable {
    private final MainFacade mainFacade;

    public CourseDirectorMenu(MainFacade mainFacade) {
        this.mainFacade = mainFacade;
    }

    @Override
    public void run() {
        try {
            authenticateCourseDirector();
        } catch (Exception e) {
            System.out.println(e.getMessage());
            return;
        }

        Menu admin = new Menu("Course Director");
        admin.addOption("Access the system", this::accessSystem);
        admin.addOption("Change password", this::updatePassword);
        admin.display();
    }

    private void accessSystem() {
        Menu accessSystem = new Menu("Access System");
        accessSystem.addOption("Students", () -> new StudentMenu(mainFacade).display());
        accessSystem.addOption("Curricular Units", () -> new CurricularUnitMenu(mainFacade).display());
        accessSystem.addOption("Politics", () -> new PoliticsMenu(mainFacade).display());
        accessSystem.addOption("Shifts", () -> new ShiftMenu(mainFacade).display());
        accessSystem.addOption("Schedules", () -> new ScheduleMenu(mainFacade).display());
        accessSystem.display();
    }

    private void updatePassword() {
        try {
            authenticateCourseDirector();
        } catch (Exception e) {
            System.out.println(e.getMessage());
            return;
        }
        String newPassword = new InputMenu<>("Please type a new password", String.class).display();
        try {
            mainFacade.updatePassword(newPassword);
            System.out.println("Password updated");
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }

    private void authenticateCourseDirector() throws Exception {
        boolean authenticated = false;
        while (!authenticated) {
            String password = new InputMenu<>("Please type your password", String.class).display();
            if (mainFacade.authenticateCourseDirector(password))
                authenticated = true;
            else
                System.out.println("Incorrect password.");
        }
        System.out.println("Successfully authenticated.");
    }
}
