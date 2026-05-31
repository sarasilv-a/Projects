package sd.common;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;

public class AuthRequest extends Message {
    private int type; // 1: register, 2: login
    private String username;
    private String password;

    public AuthRequest() {
        super(0, AuthRequest.class.getName());
        this.type = 0;
        this.username = "";
        this.password = "";
    }

    public AuthRequest(int type, String username, String password) {
        super(0, AuthRequest.class.getName());
        this.type = type;
        this.username = username;
        this.password = password;
    }

    public int getType() {
        return this.type;
    }

    public String getUsername() {
        return this.username;
    }

    public String getPassword() {
        return this.password;
    }

    @Override
    protected void serializeSubclass(DataOutputStream output) throws IOException {
        output.writeInt(type);
        output.writeUTF(username);
        output.writeUTF(password);
    }

    @Override
    protected Message deserializeSubclass(DataInputStream input, int clientID) throws IOException {
        int type = input.readInt();
        String username = input.readUTF();
        String password = input.readUTF();
        return new AuthRequest(type, username, password);
    }

    @Override
    public String toString() {
        return super.toString() + "AuthRequest{" + "type=" + this.type + ", username='" + this.username + '\'' + ", password='" + this.password + '\'' + '}';
    }
}
