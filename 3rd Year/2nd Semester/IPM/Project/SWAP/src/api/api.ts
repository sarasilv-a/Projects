import axios from "axios";
import * as types from "@/types/types";

export const API = axios.create({
  baseURL: "http://localhost:3001",
  responseType: "json",
  withCredentials: false,
  headers: {
    "Content-Type": "application/json",
  },
});

export async function login(email: string, password: string) {
  try {
    const directorRes = await API.get<types.Director[]>("/directors");
    const director = directorRes.data.find(
      (u) => u.email === email && u.password === password
    );

    if (director) {
      return {
        id: director.id,
        name: director.name,
        type: "director" as const,
      };
    }

    const studentRes = await API.get<types.Student[]>("/students");
    const student = studentRes.data.find(
      (u) => u.email === email && u.password === password
    );

    if (student) {
      return {
        id: student.id,
        name: student.name,
        type: "student" as const,
      };
    }

    return false;
  } catch (err) {
    console.error("Error in login:", err);
    return false;
  }
}

export async function registerStudent(
  email: string,
  password: string,
  name: string
) {
  try {
    const existing = await API.get<types.Student[]>("/students");
    const exists = existing.data.some((s) => s.email === email);

    if (exists) {
      return { success: false, reason: "email_in_use" };
    }

    const newUser = {
      email,
      password,
      name,
    };

    await API.post("/students", newUser);
    return { success: true };
  } catch (err) {
    console.error("Error in register:", err);
    return { success: false, reason: "error" };
  }
}

export async function checkEmailExists(email: string) {
  try {
    const [studentsRes, directorsRes] = await Promise.all([
      API.get("/students"),
      API.get("/directors"),
    ]);

    const emailToCheck = email.trim().toLowerCase();

    const studentExists = studentsRes.data.some(
      (s: any) => s.email?.toLowerCase() === emailToCheck
    );

    const directorExists = directorsRes.data.some(
      (d: any) => d.email?.toLowerCase() === emailToCheck
    );

    return studentExists || directorExists;
  } catch (err) {
    console.error("Error verifying email:", err);
    return false;
  }
}

export async function getDirectorById(id: number) {
  const response = await API.get(`/directors/${id}`);
  return response.data;
}
