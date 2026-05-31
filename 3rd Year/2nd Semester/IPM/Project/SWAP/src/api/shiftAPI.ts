import { API } from "@/api/api";
import type { Shift, Schedule } from "@/types/types";

function parseShift(raw: any): Shift {
  return {
    ...raw,
    id: Number(raw.id),
    subjectId: Number(raw.subjectId),
  };
}

export const getAllShifts = async (): Promise<Shift[]> => {
  const res = await API.get("/shifts");
  return res.data.map(parseShift);
};

export const getShiftById = async (id: number): Promise<Shift> => {
  const res = await API.get(`/shifts/${id}`);
  return parseShift(res.data);
};

export async function getShiftsBySubject(subjectId: number): Promise<Shift[]> {
  const response = await API.get(`/shifts?subjectId=${subjectId}`);
  return response.data.map(parseShift);
}

export const createShift = async (shift: Omit<Shift, "id">): Promise<Shift> => {
  const allShifts = await getAllShifts();
  const ids = allShifts.map((s) => s.id);
  const newId = ids.length > 0 ? Math.max(...ids) + 1 : 1;

  const newShift: Shift = {
    id: newId,
    ...shift,
  };

  const res = await API.post("/shifts", {
    ...newShift,
    id: String(newShift.id),
  });

  return parseShift(res.data);
};

export const updateShift = async (
  id: number,
  updatedShift: Shift
): Promise<Shift> => {
  const res = await API.put(`/shifts/${id}`, {
    ...updatedShift,
    id: String(updatedShift.id),
  });

  return parseShift(res.data);
};

export const deleteShift = async (id: number): Promise<void> => {
  await API.delete(`/shifts/${id}`);
};

export async function getAvailableShiftsForStudent(
  studentId: number,
  subjectId: number
): Promise<Shift[]> {
  const [shiftsRes, scheduleRes] = await Promise.all([
    API.get(`/shifts?subjectId=${subjectId}`),
    API.get(`/schedules?studentId=${studentId}`),
  ]);

  const shifts: Shift[] = shiftsRes.data.map(parseShift);
  const schedule: Schedule[] = scheduleRes.data;

  const studentShiftIds = schedule.map((s) => s.shiftId);
  const subjectShifts = shifts.filter((s) => !studentShiftIds.includes(s.id));

  return subjectShifts.filter((shift) => shift.limit > 0);
}

function timeOverlap(
  start1: string,
  end1: string,
  start2: string,
  end2: string
): boolean {
  return start1 < end2 && start2 < end1;
}

export async function getShiftConflictsForStudent(
  studentId: number
): Promise<{ shiftA: Shift; shiftB: Shift }[]> {
  const scheduleRes = await API.get(`/schedules?studentId=${studentId}`);
  const schedule = scheduleRes.data;
  const shiftIds = schedule.map((entry: any) => entry.shiftId);

  const shiftPromises = shiftIds.map((id: number) => API.get(`/shifts/${id}`));
  const shiftsRes = await Promise.all(shiftPromises);
  const shifts = shiftsRes.map((res) => parseShift(res.data));

  const conflicts: { shiftA: Shift; shiftB: Shift }[] = [];

  for (let i = 0; i < shifts.length; i++) {
    for (let j = i + 1; j < shifts.length; j++) {
      const a = shifts[i];
      const b = shifts[j];
      if (a.day === b.day && timeOverlap(a.start, a.end, b.start, b.end)) {
        conflicts.push({ shiftA: a, shiftB: b });
      }
    }
  }

  return conflicts;
}
