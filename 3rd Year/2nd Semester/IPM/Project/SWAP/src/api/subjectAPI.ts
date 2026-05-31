import { API } from "@/api/api";
import type { Subject } from "@/types/types";

function parseSubject(raw: any): Subject {
  return {
    ...raw,
    id: Number(raw.id),
  };
}

export const getAllSubjects = async (): Promise<Subject[]> => {
  const res = await API.get("/subjects");
  return res.data.map(parseSubject);
};

export const getSubjectById = async (id: number): Promise<Subject> => {
  const res = await API.get(`/subjects/${id}`);
  return parseSubject(res.data);
};

export const createSubject = async (
  subject: Omit<Subject, "id">
): Promise<Subject> => {
  const allSubjects = await getAllSubjects();

  const ids = allSubjects.map((s) => s.id);
  const newId = ids.length > 0 ? Math.max(...ids) + 1 : 1;

  const newSubject: Subject = {
    id: newId,
    ...subject,
  };

  const res = await API.post("/subjects", {
    ...newSubject,
    id: String(newSubject.id),
  });

  return parseSubject(res.data);
};

export const updateSubject = async (
  id: number,
  updatedSubject: Subject
): Promise<Subject> => {
  const res = await API.put(`/subjects/${id}`, {
    ...updatedSubject,
    id: String(updatedSubject.id),
  });

  return parseSubject(res.data);
};

export const deleteSubject = async (id: number): Promise<void> => {
  await API.delete(`/subjects/${id}`);
};
