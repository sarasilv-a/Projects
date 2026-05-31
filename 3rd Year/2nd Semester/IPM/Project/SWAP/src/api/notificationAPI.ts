import { API } from "@/api/api";
import type { Notification } from "@/types/types";

function parseNotification(raw: any): Notification {
  const base = {
    ...raw,
    id: Number(raw.id),
  };

  if (raw.type === "Change") {
    return {
      ...base,
      type: "Change",
      studentId: Number(raw.studentId),
      currentShift: Number(raw.currentShift),
      wantedShift: Number(raw.wantedShift),
    };
  }

  return {
    ...base,
    type: "Deadline",
  };
}

export const getAllNotifications = async (): Promise<Notification[]> => {
  const res = await API.get("/notifications");
  return res.data.map(parseNotification);
};

export const getNotificationById = async (
  id: number
): Promise<Notification> => {
  const res = await API.get(`/notifications/${id}`);
  return parseNotification(res.data);
};

export async function getNotificationsByStudent(
  studentId: number
): Promise<Notification[]> {
  const response = await API.get(`/notifications?studentId=${studentId}`);
  return response.data.map(parseNotification);
}

export const createNotification = async (
  newNotification: Omit<Notification, "id">
): Promise<Notification> => {
  const allNotifications = await getAllNotifications();
  const ids = allNotifications.map((n) => n.id);
  const newId = ids.length > 0 ? Math.max(...ids) + 1 : 1;

  const notification = {
    id: newId,
    ...newNotification,
  } as Notification;

  const res = await API.post("/notifications", {
    ...notification,
    id: String(notification.id),
  });

  return parseNotification(res.data);
};

export const updateNotification = async (
  id: number,
  updatedNotification: Partial<Notification>
): Promise<Notification> => {
  const res = await API.patch(`/notifications/${id}`, {
    ...updatedNotification,
    id: String(id),
  });

  return parseNotification(res.data);
};

export const deleteNotification = async (id: number): Promise<void> => {
  await API.delete(`/notifications/${id}`);
};
