import { defineStore } from "pinia";

export const useSessionStore = defineStore("session", {
  state: () => ({
    id: "",
    name: "",
    type: "" as "student" | "director" | "",
  }),
  actions: {
    login(id: string, name: string, type: "student" | "director") {
      this.id = id;
      this.name = name;
      this.type = type;
    },
    logout() {
      this.id = "";
      this.name = "";
      this.type = "";
    },
  },
  getters: {
    isLoggedIn: (state) => !!state.id && !!state.name && !!state.type,
    isStudent: (state) => state.type === "student",
    isDirector: (state) => state.type === "director",
  },
  persist: true,
});
