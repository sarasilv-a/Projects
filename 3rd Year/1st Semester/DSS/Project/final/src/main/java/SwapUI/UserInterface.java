package SwapUI;

import SwapLN.MainFacade;
import SwapUI.CourseDirector.CourseDirectorMenu;

public class UserInterface implements Runnable {
    private final MainFacade MainFacade = new MainFacade();
    private final boolean operationMode; // true = director, false = student

    public UserInterface(boolean operationMode) {
        this.operationMode = operationMode;
    }

    public void run() {
        if (operationMode)
            new CourseDirectorMenu(MainFacade).run();
        else
            new StudentMenu(MainFacade).run();
    }
}
