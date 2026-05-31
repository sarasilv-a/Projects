package SwapUI;

import SwapLN.Shift.CurricularUnit;
import SwapLN.MainFacade;
import SwapLN.Shift.Room;
import SwapLN.Shift.Shift;
import SwapLN.Shift.Slot;

import java.util.Comparator;
import java.util.List;

public class StudentMenu implements Runnable {
    private final MainFacade mainFacade;

    public StudentMenu(MainFacade mainFacade) {
        this.mainFacade = mainFacade;
    }

    public void viewSchedule(String studentNumber) {
        Menu viewSchedule = new Menu("View Schedule");
        viewSchedule.addOption("View my schedule", () -> {
            try {
                List<Integer> shiftIDs = mainFacade.getShifts(studentNumber);

                if (shiftIDs.isEmpty()) {
                    System.out.println("No shifts found for the student.");
                    return;
                }

                List<Shift> shifts = mainFacade.getScheduleShifts(shiftIDs);

                // Ordenar os turnos por dia da semana e hora de início
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

                    allShiftsInfo.append(shiftInfo).append("\n");
                }

                System.out.println(allShiftsInfo.toString());
            } catch (Exception e) {
                System.out.println("Error retrieving schedule: " + e.getMessage());
            }
        });

        viewSchedule.addOption("Export my schedule to JSON", () -> {
            try {
                String filePath = "horario_aluno_" + studentNumber + ".json";
                mainFacade.exportStudentScheduleToJSON(studentNumber, filePath);
                System.out.println("Schedule exported successfully to: " + filePath);
            } catch (Exception e) {
                System.out.println("Error exporting schedule: " + e.getMessage());
            }
        });

        viewSchedule.display();
    }

    private String authenticateStudent() throws Exception {
        boolean authenticated = false;
        String studentNumber = null;
        String password = null;
        while (!authenticated) {
            studentNumber = new InputMenu<>("Please enter your student number", String.class).display();
            password = new InputMenu<>("Please enter your password", String.class).display();
            if (mainFacade.authenticateStudent(studentNumber, password))
                authenticated = true;
            else
                System.out.println("Invalid student number.");
        }
        System.out.println("Successfully authenticated.");
        return studentNumber;
    }

    private void updatePassword(String studentNumber) {
        try {
            authenticateStudent();
        } catch (Exception e) {
            System.out.println(e.getMessage());
            return;
        }
        String newPassword = new InputMenu<>("Please type a new password", String.class).display();
        try {
            mainFacade.updateStudentPassword(studentNumber, newPassword);
            System.out.println("Password updated");
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }

    public void run() {
        String studentNumber;
        try {
            studentNumber = authenticateStudent();
        }
        catch (Exception e) {
            System.out.println(e.getMessage());
            return;
        }

        Menu student = new Menu("Student");
        String finalStudentNumber = studentNumber;
        student.addOption("View Schedule", () -> viewSchedule(finalStudentNumber));
        student.addOption("Change Password", () -> updatePassword(finalStudentNumber));
        student.display();
    }
}

