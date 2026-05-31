import { API } from "@/api/api";
import type { Enrollment } from "@/types/types";

function parseEnrollment(raw: any): Enrollment {
  return {
    id: Number(raw.id),
    studentId: Number(raw.studentId),
    subjectId: Number(raw.subjectId),
  };
}

export const getAllEnrollments = async (): Promise<Enrollment[]> => {
  const res = await API.get("/enrollments");
  return res.data.map(parseEnrollment);
};

export const getEnrollmentById = async (id: number): Promise<Enrollment> => {
  const res = await API.get(`/enrollments/${id}`);
  return parseEnrollment(res.data);
};

export const createEnrollment = async (
  newEnrollment: Omit<Enrollment, "id">
): Promise<Enrollment> => {
  const allEnrollments = await getAllEnrollments();

  const ids = allEnrollments.map((e) => e.id);
  const newId = ids.length > 0 ? Math.max(...ids) + 1 : 1;

  const enrollmentToCreate: Enrollment = {
    id: newId,
    ...newEnrollment,
  };

  const res = await API.post("/enrollments", {
    ...enrollmentToCreate,
    id: String(enrollmentToCreate.id),
    studentId: String(enrollmentToCreate.studentId),
    subjectId: String(enrollmentToCreate.subjectId),
  });

  return parseEnrollment(res.data);
};

export const updateEnrollment = async (
  id: number,
  updatedEnrollment: Partial<Enrollment>
): Promise<Enrollment> => {
  const res = await API.patch(`/enrollments/${id}`, {
    ...updatedEnrollment,
    studentId: updatedEnrollment.studentId?.toString(),
    subjectId: updatedEnrollment.subjectId?.toString(),
  });

  return parseEnrollment(res.data);
};

export const deleteEnrollment = async (id: number): Promise<void> => {
  await API.delete(`/enrollments/${id}`);
};
