export type Student = {
  id: number;
  email: string;
  number: string;
  name: string;
  password: string;
  interests: string;
  goals: string;
  quote: string;
  age: number;
  year: number;
  city: string;
  occupation: string;
  education: string;
  challenges: string;
  solutions: string;
  status: string;
};

export type Subject = {
  id: number;
  name: string;
  shortname: string;
  year: number;
  semester: number;
};

export type Shift = {
  id: number;
  name: string;
  type: "T" | "TP";
  building: string;
  room: string;
  day: number;
  start: string;
  end: string;
  limit: number;
  subjectId: number;
};

export type Enrollment = {
  id: number;
  studentId: number;
  subjectId: number;
};

export type Schedule = {
  id: number;
  studentId: number;
  shiftId: number;
};

export type Notification =
  | {
      id: number;
      type: "Change";
      date: string; // ISO format
      message: string;
      studentId: number;
      currentShift: number;
      wantedShift: number;
    }
  | {
      id: number;
      type: "Deadline";
      date: string;
      message: string;
    };

export type Director = {
  id: number;
  email: string;
  name: string;
  password: string;
  interests: string;
  goals: string;
  quote: string;
  age: number;
  city: string;
  occupation: string;
  education: string;
  challenges: string;
  solutions: string;
};
