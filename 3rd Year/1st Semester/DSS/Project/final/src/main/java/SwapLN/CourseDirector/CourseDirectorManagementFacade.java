package SwapLN.CourseDirector;

import SwapDL.CourseDirectorDAO;

public class CourseDirectorManagementFacade implements ICourseDirectorManagement {
    private final CourseDirectorDAO courseDirectorDAO;

    public CourseDirectorManagementFacade() {
        this.courseDirectorDAO = new CourseDirectorDAO();
    }

    @Override
    public boolean authenticateCourseDirector(String password) throws Exception {
        return password.equals(courseDirectorDAO.getPassword());
    }

    @Override
    public void updatePassword(String newPassword) throws Exception {
        courseDirectorDAO.setPassword(newPassword);
    }
}
