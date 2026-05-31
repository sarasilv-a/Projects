package SwapUI.CourseDirector;

import SwapLN.MainFacade;
import SwapLN.Shift.CurricularUnit;
import SwapLN.Shift.Room;
import SwapLN.Shift.Shift;
import SwapLN.Shift.Slot;
import SwapLN.Student.Student;
import SwapUI.InputMenu;
import SwapUI.Menu;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class ScheduleMenu {
    private final MainFacade mainFacade;

    public ScheduleMenu(MainFacade mainFacade) {
        this.mainFacade = mainFacade;
    }

    public void display() {
        Menu schedulesMenu = new Menu("Schedules");
        schedulesMenu.addOption("View Schedules", this::viewSchedules);
        schedulesMenu.addOption("Generate Schedules", this::generateSchedules);
        schedulesMenu.addOption("Manual Generate Schedules", this::manualGenerateSchedules);
        schedulesMenu.addOption("Resolve Incomplete Schedules", this::resolveIncompleteSchedules);
        schedulesMenu.display();
    }

    private void viewSchedules() {
        Menu viewSchedules = new Menu("View Schedules");
        viewSchedules.addOption("View student schedule", () -> {
            try {
                String studentNumber = new InputMenu<>("Please enter the student number", String.class).display();
                List<Integer> shiftIDs = mainFacade.getShifts(studentNumber);
                if (shiftIDs.isEmpty()) {
                    System.out.println("No shifts found for the student.");
                    return;
                }
                displayShifts(mainFacade.getScheduleShifts(shiftIDs), false);
            } catch (Exception e) {
                System.out.println("Error retrieving student schedule: " + e.getMessage());
            }
        });
        viewSchedules.addOption("View UC schedule", () -> {
            try {
                String curricularUnitCode = new InputMenu<>("Please enter the UC code", String.class).display();
                List<Shift> shifts = mainFacade.getShiftsByUC(curricularUnitCode);
                if (shifts.isEmpty()) {
                    System.out.println("No shifts found for the curricular unit.");
                    return;
                }
                displayShifts(shifts, true);
            } catch (Exception e) {
                System.out.println("Error retrieving UC schedule: " + e.getMessage());
            }
        });
        viewSchedules.display();
    }

    private void generateSchedules() {
        Menu generateMenu = new Menu("Generate Schedules");

        generateMenu.addOption("Generate", () -> {
            try {
                List<Student> students = mainFacade.getAllStudents();
                boolean hasShifts = mainFacade.hasShifts();

                if (students.isEmpty()) {
                    System.out.println("No students found. Cannot generate schedules.");
                    return;
                }

                if (!hasShifts) {
                    System.out.println("No shifts found. Cannot generate schedules.");
                    return;
                }

                applyPolicies();

                for (Student student : students) {
                    String studentNumber = student.getStudentNumber();

                    List<CurricularUnit> units = mainFacade.getEnrolledCurricularUnits(studentNumber);

                    for (CurricularUnit unit : units) {
                        List<Shift> shifts = mainFacade.getShiftsByUC(unit.getCode());

                        List<Shift> theoreticalShifts = shifts.stream()
                                .filter(shift -> shift.getType().equals("T"))
                                .toList();
                        List<Shift> practicalShifts = shifts.stream()
                                .filter(shift -> shift.getType().equals("TP") || shift.getType().equals("PL"))
                                .toList();

                        Shift selectedTheoretical = findAvailableShift(theoreticalShifts, studentNumber);
                        Shift selectedPractical = findAvailableShift(practicalShifts, studentNumber);

                        if (selectedTheoretical != null) {
                            mainFacade.allocateStudentToShift(studentNumber, selectedTheoretical.getShiftID());
                        }

                        if (selectedPractical != null) {
                            mainFacade.allocateStudentToShift(studentNumber, selectedPractical.getShiftID());
                        }
                    }
                }

                System.out.println("Schedules generated successfully!");
            } catch (Exception e) {
                System.out.println("Error generating schedules: " + e.getMessage());
            }
        });

        generateMenu.addOption("Remove Previous", () -> {
            try {
                mainFacade.removeAllSchedules();
                System.out.println("All previous schedules removed successfully.");
            } catch (Exception e) {
                System.out.println("Error removing schedules: " + e.getMessage());
            }
        });

        generateMenu.display();
    }


    private Shift findAvailableShift(List<Shift> shifts, String studentNumber) throws Exception {
        for (Shift shift : shifts) {
            List<Integer> studentShifts = mainFacade.getShifts(studentNumber);
            boolean alreadyAllocatedToUnit = studentShifts.stream()
                    .anyMatch(shiftID -> {
                        try {
                            Shift allocatedShift = mainFacade.getShift(shiftID);
                            return allocatedShift.getCurricularUnitCode().equals(shift.getCurricularUnitCode()) &&
                                    allocatedShift.getType().equals(shift.getType());
                        } catch (Exception e) {
                            return false;
                        }
                    });

            if (alreadyAllocatedToUnit) {
                continue;
            }

            List<String> enrolledStudents = mainFacade.getStudents(shift.getShiftID());
            if (enrolledStudents.size() < shift.getLimit() - 5) {

                Slot shiftSlot = mainFacade.getSlot(shift.getSlotID());
                boolean hasConflict = studentShifts.stream()
                        .map(shiftID -> {
                            try {
                                return mainFacade.getSlot(mainFacade.getShift(shiftID).getSlotID());
                            } catch (Exception e) {
                                return null;
                            }
                        })
                        .anyMatch(studentSlot -> studentSlot != null && shiftSlot.conflictsWith(studentSlot));

                if (!hasConflict) {
                    return shift;
                }
            }
        }
        return null;
    }


    private void applyPolicies() {
        try {
            String filePath = "data/politics.json";
            JSONArray politics = new JSONArray(Files.readString(Path.of(filePath)));

            for (int i = 0; i < politics.length(); i++) {
                JSONObject policy = politics.getJSONObject(i);
                String curricularUnitCode = String.valueOf(policy.getInt("subjectId"));
                String policyType = policy.getString("politic");

                if (policyType.equals("limit")) {
                    int limit = policy.getInt("number");
                    applyLimitPolicy(curricularUnitCode, limit);
                } else if (policyType.equals("group")) {
                    JSONArray groups = policy.getJSONArray("students");
                    applyGroupPolicy(curricularUnitCode, groups);
                }
            }

            System.out.println("Policies applied successfully!");
        } catch (Exception e) {
            System.out.println("Error applying policies: " + e.getMessage());
        }
    }

    private void applyLimitPolicy(String curricularUnitCode, int limit) throws Exception {
        List<Shift> shifts = mainFacade.getShiftsByUC(curricularUnitCode);

        List<Shift> practicalShifts = shifts.stream()
                .filter(shift -> shift.getType().equals("TP") || shift.getType().equals("PL"))
                .toList();

        for (Shift shift : practicalShifts) {
            mainFacade.updateShiftLimit(shift.getShiftID(), limit);
        }
    }

    private void applyGroupPolicy(String curricularUnitCode, JSONArray groups) throws Exception {
        List<Shift> shifts = mainFacade.getShiftsByUC(curricularUnitCode);

        List<Shift> practicalShifts = shifts.stream()
                .filter(shift -> shift.getType().equals("TP") || shift.getType().equals("PL"))
                .toList();

        int shiftIndex = 0;
        for (int i = 0; i < groups.length(); i++) {
            JSONArray group = groups.getJSONArray(i);

            Shift shift = practicalShifts.get(shiftIndex % practicalShifts.size());
            for (int j = 0; j < group.length(); j++) {
                String studentNumber = group.getString(j);
                mainFacade.allocateStudentToShift(studentNumber, shift.getShiftID());
            }

            shiftIndex++;
        }
    }

    private void manualGenerateSchedules() {
        try {
            InputMenu<String> studentIdMenu = new InputMenu<>("Enter the student ID to modify the schedule", String.class);
            String studentId = studentIdMenu.display();

            boolean studentExists = mainFacade.studentExists(studentId);
            if (!studentExists) {
                System.out.println("Student ID not found. Exiting schedule modification.");
                return;
            }

            System.out.println("Current schedule for student " + studentId + ":");
            viewStudentSchedule(studentId);

            modifyScheduleMenu(studentId);

        } catch (Exception e) {
            System.out.println("Error manually generating schedules: " + e.getMessage());
        }
    }

    private void viewStudentSchedule(String studentId) {
        try {
            List<Integer> shiftIDs = mainFacade.getShifts(studentId);
            if (shiftIDs.isEmpty()) {
                System.out.println("No shifts found for the student.");
                return;
            }
            displayShifts(mainFacade.getScheduleShifts(shiftIDs), false);
        } catch (Exception e) {
            System.out.println("Error retrieving student schedule: " + e.getMessage());
        }
    }

    private void displayShifts(List<Shift> shifts, boolean includeStudents) {
        try {
            // Ordenar os turnos por dia da semana e, em caso de empate, pela hora de início
            shifts.sort(Comparator.comparingInt((Shift shift) -> {
                        try {
                            return mainFacade.getSlot(shift.getSlotID()).getWeekDay();
                        } catch (Exception e) {
                            throw new RuntimeException(e);
                        }
                    })
                    .thenComparing(shift -> {
                        try {
                            return mainFacade.getSlot(shift.getSlotID()).getStartTime();
                        } catch (Exception e) {
                            throw new RuntimeException(e);
                        }
                    }));

            StringBuilder allShiftsInfo = new StringBuilder();

            for (Shift shift : shifts) {
                Slot slot = mainFacade.getSlot(shift.getSlotID());
                Room room = mainFacade.getRoom(slot.getRoomID());
                CurricularUnit curricularUnit = mainFacade.getCurricularUnit(shift.getCurricularUnitCode());

                String shiftInfo = String.format(
                        "Shift %d (%s - %d) | %s (%s) | Semester %d | Day %d: %s - %s | Room: %s - %s (Max:%d)",
                        shift.getShiftID(),
                        shift.getType(),
                        shift.getNumber(),
                        curricularUnit.getName(),
                        curricularUnit.getShortName(),
                        curricularUnit.getSemester(),
                        slot.getWeekDay(),
                        slot.getStartTime(),
                        slot.getEndTime(),
                        room.getBuilding(),
                        room.getRoomNumber(),
                        room.getCapacity()
                );

                // Adicionar informações de estudantes, se necessário
                if (includeStudents) {
                    List<String> students = mainFacade.getStudents(shift.getShiftID());
                    String studentInfo = students.isEmpty()
                            ? "No students enrolled"
                            : "Students Enrolled: " + String.join(", ", students);
                    shiftInfo += " | " + studentInfo;
                }

                allShiftsInfo.append(shiftInfo).append("\n");
            }

            // Imprimir todas as informações formatadas
            System.out.println(allShiftsInfo.toString());
        } catch (Exception e) {
            System.out.println("Error displaying shifts: " + e.getMessage());
        }
    }


    private void resolveIncompleteSchedules() {
        try {
            Menu resolveIncompleteScheduleMenu = new Menu("Resolve Incomplete Schedules");

            resolveIncompleteScheduleMenu.addOption("View students with incomplete schedules", () -> {
                try {
                    List<Student> students = mainFacade.getStudentsWithIncompleteSchedules();

                    if (students.isEmpty()) {
                        System.out.println("No students with incomplete schedules found.");
                        return;
                    }

                    System.out.println("Students with incomplete schedules:");
                    for (Student student : students) {
                        System.out.println(student.getStudentNumber() + " - " + student.getName());
                    }

                    InputMenu<String> studentIdMenu = new InputMenu<>("Enter the student ID to resolve the schedule", String.class);
                    String studentId = studentIdMenu.display();

                    boolean studentExists = mainFacade.studentExists(studentId);
                    if (!studentExists) {
                        System.out.println("Student ID not found. Returning to menu.");
                        return;
                    }

                    viewStudentSchedule(studentId);
                    modifyScheduleMenu(studentId);

                } catch (Exception e) {
                    System.out.println("Error fetching or resolving schedules: " + e.getMessage());
                }
            });

            resolveIncompleteScheduleMenu.display();

        } catch (Exception e) {
            System.out.println("Error resolving incomplete schedules: " + e.getMessage());
        }
    }

    private void modifyScheduleMenu(String studentId) {
        try {
            Menu modificationMenu = new Menu("Modify Schedule");

            modificationMenu.addOption("Add a shift", () -> {
                List<CurricularUnit> curricularUnits = null;
                try {
                    curricularUnits = mainFacade.getEnrolledCurricularUnits(studentId);
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }

                if (curricularUnits.isEmpty()) {
                    System.out.println("No curricular units found for the student.");
                    return;
                }

                System.out.println("Available Curricular Units:");
                for (CurricularUnit unit : curricularUnits) {
                    System.out.println(unit.toString());
                }

                InputMenu<String> curricularUnitMenu = new InputMenu<>("Enter the code of the curricular unit to view shifts", String.class);
                String selectedCU = curricularUnitMenu.display();

                List<Shift> shifts = null;
                try {
                    shifts = mainFacade.getShiftsByUC(selectedCU);
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }

                if (shifts.isEmpty()) {
                    System.out.println("No shifts available for the selected curricular unit.");
                    return;
                }

                System.out.println("Available Shifts for Curricular Unit " + selectedCU + ":");
                for (Shift shift : shifts) {
                    try {
                        Slot slot = mainFacade.getSlot(shift.getSlotID());
                        System.out.println("Shift ID: " + shift.getShiftID() +
                                            ", Type: " + shift.getType() +
                                            ", Number: " + shift.getNumber() +
                                            ", Limit: " + shift.getLimit() +
                                            ", Start Time: " + slot.getStartTime() +
                                            ", Week Day: " + slot.getWeekDay() +
                                            ", Students Enrolled: " + shift.getStudentsEnrolled() + " out of " + shift.getLimit());
                    } catch (Exception e) {
                        throw new RuntimeException(e);
                    }
                }

                InputMenu<String> shiftIdMenu = new InputMenu<>("Enter the ID of the shift to add", String.class);
                String shiftToAdd = shiftIdMenu.display();

                boolean notAlreadyEnrolledInShift = true;
                try {
                    notAlreadyEnrolledInShift = mainFacade.addShiftStudent(studentId, Integer.parseInt(shiftToAdd));
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }

                if (!notAlreadyEnrolledInShift){
                    System.out.println("Student is already enrolled in a shift of the same type and curricular unit.");
                }
                else{
                    System.out.println("Shift " + shiftToAdd + " added to student " + studentId + ".");
                    System.out.println("Updated schedule for student " + studentId + ":");
                }
                viewStudentSchedule(studentId);
            });

            modificationMenu.addOption("Remove a shift", () -> {
                InputMenu<String> shiftIdMenu = new InputMenu<>("Enter the ID of the shift to remove", String.class);
                String shiftToRemove = shiftIdMenu.display();

                try {
                    mainFacade.removeShiftStudent(studentId, Integer.parseInt(shiftToRemove));
                } catch (Exception e) {
                    throw new RuntimeException(e);
                }
                System.out.println("Shift " + shiftToRemove + " removed from student " + studentId + ".");

                System.out.println("Updated schedule for student " + studentId + ":");
                viewStudentSchedule(studentId);
            });

            modificationMenu.display();

        } catch (Exception e) {
            System.out.println("Error modifying schedule: " + e.getMessage());
        }
    }
}
