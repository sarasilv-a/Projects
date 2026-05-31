package sd.common;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

public class User {
    private String username;
    private String password;

    public User() {
        this.username = "";
        this.password = "";
    }

    public User(String username, String password) {
        this.username = username;
        this.password = password;
    }

    public String getUsername() {
        return this.username;
    }

    public String getPassword() {
        return this.password;
    }

    public void serialize(DataOutputStream output) throws IOException {
        output.writeUTF(this.username);
        output.writeUTF(this.password);
    }

    public void deserialize(DataInputStream input) throws IOException {
        this.username = input.readUTF();
        this.password = input.readUTF();
    }

    @Override
    public String toString() {
        return "User{" + "username='" + this.username + '\'' + ", password=" + '\'' + this.password + '}';
    }
}