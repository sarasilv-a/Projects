import { API } from "@/api/api";
import type { Schedule } from "@/types/types";

function parseSchedule(raw: any): Schedule {
  return {
    ...raw,
    id: Number(raw.id),
  };
}

export const getAllSchedules = async (): Promise<Schedule[]> => {
  const res = await API.get("/schedules");
  return res.data.map(parseSchedule);
};

export const getScheduleById = async (id: number): Promise<Schedule> => {
  const res = await API.get(`/schedules/${id}`);
  return parseSchedule(res.data);
};

export async function getScheduleByStudent(
  studentId: number
): Promise<Schedule[]> {
  const res = await API.get(`/schedules?studentId=${studentId}`);
  return res.data.map(parseSchedule);
}

export const createSchedule = async (
  newSchedule: Omit<Schedule, "id">
): Promise<Schedule> => {
  const allSchedules = await getAllSchedules();
  const ids = allSchedules.map((s) => s.id);
  const newId = ids.length > 0 ? Math.max(...ids) + 1 : 1;

  const scheduleToSave = {
    ...newSchedule,
    id: String(newId),
  };

  const res = await API.post("/schedules", scheduleToSave);
  return parseSchedule(res.data);
};

export const updateSchedule = async (
  id: number,
  updatedSchedule: Schedule
): Promise<Schedule> => {
  const res = await API.put(`/schedules/${id}`, {
    ...updatedSchedule,
    id: String(updatedSchedule.id),
  });

  return parseSchedule(res.data);
};

export const deleteSchedule = async (id: number): Promise<void> => {
  await API.delete(`/schedules/${id}`);
};

export async function getSchedulesByShift(
  shiftId: number
): Promise<Schedule[]> {
  const res = await API.get(`/schedules?shiftId=${shiftId}`);
  return res.data.map(parseSchedule);
}
