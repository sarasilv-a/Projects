package SwapUI.CourseDirector;

import SwapLN.MainFacade;
import SwapLN.Shift.CurricularUnit;
import SwapLN.Student.Student;
import SwapUI.InputMenu;
import SwapUI.Menu;

import java.util.List;

public class StudentMenu {
    private final MainFacade mainFacade;

    public StudentMenu(MainFacade mainFacade) {
        this.mainFacade = mainFacade;
    }

    public void display() {
        Menu studentsMenu = new Menu("Students");
        studentsMenu.addOption("View Students", this::viewStudents);
        studentsMenu.addOption("Add Students", this::addStudents);
        studentsMenu.addOption("Remove Students", this::removeStudents);
        studentsMenu.display();
    }

    private void viewStudents() {
        try {
            List<Student> students = mainFacade.getAllStudents();
            if (students.isEmpty()) {
                System.out.println("No students found in the system.");
                return;
            }

            System.out.println("List of Students:");
            for (Student student : students) {
                System.out.println("  Number: " + student.getStudentNumber() +
                        "  Name: " + student.getName() +
                        "  Status: " + student.getStatus());
                System.out.println("----------------------------");
            }
        } catch (Exception e) {
            System.out.println("Error retrieving students: " + e.getMessage());
        }
    }

    private void addStudents() {
        try {
            String path = new InputMenu<>("Enter file path", String.class).display();

            List<CurricularUnit> uc = mainFacade.getAllCurricularUnits();

            if (uc.isEmpty()) {
                System.out.println("No curricular units exist. Please add curricular units before adding students.");
                return;
            }

            mainFacade.importStudentsFromJSON(path);
            System.out.println("Students added successfully.");
        } catch (Exception e) {
            System.out.println("Error adding students: " + e.getMessage());
        }
    }

    private void removeStudents() {
        try {
            mainFacade.removeAllStudents();
            System.out.println("All students removed successfully.");
        } catch (Exception e) {
            System.out.println("Error removing students: " + e.getMessage());
        }
    }
}
