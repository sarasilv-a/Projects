package SwapLN.CourseDirector;

public interface ICourseDirectorManagement {

    boolean authenticateCourseDirector(String password) throws Exception;

    void updatePassword(String newPassword) throws Exception;
}
