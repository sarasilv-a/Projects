package SwapLN.Student;

import SwapLN.Student.Status.Status;

public class Student {
    private final String studentNumber;
    private final String name;
    private final Status status;

    public Student(String studentNumber, String name, Status status) {
        this.studentNumber = studentNumber;
        this.name = name;
        this.status = status;
    }

    public String getStudentNumber() {
        return studentNumber;
    }

    public String getName() {
        return name;
    }

    public String getStatus() {
        return status != null ? status.getStatus() : "No status";
    }

    @Override
    public String toString() {
        return "Student{" +
                "studentNumber='" + studentNumber + '\'' +
                ", name='" + name + '\'' +
                ", status=" + (status != null ? status.getStatus() : "No status") +
                '}';
    }
}
