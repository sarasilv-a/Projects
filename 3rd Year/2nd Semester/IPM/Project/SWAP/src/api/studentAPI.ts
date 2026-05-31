import { API } from "@/api/api";
import type { Student } from "@/types/types";

function parseStudent(raw: any): Student {
  return {
    ...raw,
    id: Number(raw.id),
  };
}

export async function getStudents(): Promise<Student[]> {
  const response = await API.get("/students");
  return response.data.map(parseStudent);
}

export async function getStudentById(id: number): Promise<Student> {
  const response = await API.get(`/students/${id}`);
  return parseStudent(response.data);
}

export async function createStudent(
  student: Omit<Student, "id">
): Promise<Student> {
  const allStudents = await getStudents();
  const maxId =
    allStudents.length > 0 ? Math.max(...allStudents.map((s) => s.id)) : 0;

  const newStudent: Student = {
    ...student,
    id: maxId + 1,
  };

  const response = await API.post("/students", {
    ...newStudent,
    id: newStudent.id.toString(),
  });

  return parseStudent(response.data);
}

export async function updateStudent(
  id: number,
  updatedStudent: Partial<Student>
): Promise<Student> {
  const response = await API.patch(`/students/${id}`, updatedStudent);
  return parseStudent(response.data);
}

export async function deleteStudent(id: number): Promise<void> {
  await API.delete(`/students/${id}`);
}

export async function getStudentsByShift(shiftId: number): Promise<Student[]> {
  const response = await API.get(`/schedules?shiftId=${shiftId}`);
  const scheduleEntries = response.data;
  const studentIds = scheduleEntries.map((entry: any) => entry.studentId);

  const studentPromises = studentIds.map((id: number) =>
    API.get(`/students/${id.toString()}`)
  );
  const studentsResponses = await Promise.all(studentPromises);

  return studentsResponses.map((res) => parseStudent(res.data));
}

export async function getStudentsWithEnrollments(
  subjectId: number
): Promise<Student[]> {
  const enrollmentsRes = await API.get(`/enrollments?subjectId=${subjectId}`);
  const enrollments = enrollmentsRes.data;
  const studentIds = enrollments.map((e: any) => e.studentId);

  const studentPromises = studentIds.map((id: number) =>
    API.get(`/students/${id.toString()}`)
  );
  const studentsResponses = await Promise.all(studentPromises);

  return studentsResponses.map((res) => parseStudent(res.data));
}
